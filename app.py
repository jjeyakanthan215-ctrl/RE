import os
import io
import csv
import nltk
import uuid
import json
import PyPDF2
import pypdfium2 as pdfium
from datetime import datetime, timezone
from flask import Flask, request, render_template, redirect, url_for, flash, make_response, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import logging
from resume_processor import process_resume
from ats_checker import check_ats_score
from coding_bp import coding_bp
from interview_bp import interview_bp

# NLTK data is typically pre-downloaded in build phase, but we keep this as a safe fallback
def init_nltk():
    try:
        import nltk
        for res in ['punkt', 'stopwords', 'averaged_perceptron_tagger']:
            try:
                nltk.data.find(f'tokenizers/{res}' if res == 'punkt' else f'corpora/{res}')
            except (LookupError, AttributeError):
                nltk.download(res)
    except Exception:
        pass

init_nltk()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Rebrand the terminal logs from 'werkzeug' to 'ESCTRIX'
logging.getLogger('werkzeug').name = 'ESCTRIX'
log = logging.getLogger('ESCTRIX')

app = Flask(__name__)
from database import db, User, ScreeningSession, Candidate, ATSCheck

# Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-key-123')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'esctrix.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Create tables and initialize app context
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# Database setup
# (db already initialized above)

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

@app.route("/")
def index():
    return render_template("index.html", current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            # Automatic redirect for admin Jerry
            if user.name.lower() == 'jerry':
                return redirect(url_for('admin.dashboard'))
            return redirect(url_for('index'))
        flash('Invalid email or password.')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        role = request.form.get('role', 'candidate') # Default to candidate
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.')
            return redirect(url_for('signup'))
        new_user = User(email=email, name=name, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route("/screen", methods=["GET", "POST"])
@login_required
def screen():
    if request.method == "POST":
        job_description = request.form.get("job_description")
        files = request.files.getlist("resumes")

        if not job_description or not files or files[0].filename == '':
            return render_template("screen.html", error="Please provide details.")

        results = []
        upload_dir = "uploaded_resumes"
        os.makedirs(upload_dir, exist_ok=True)

        for file in files:
            if file.filename == '': continue
            temp_path = os.path.join(upload_dir, file.filename)
            file.save(temp_path)
            try:
                processed_data = process_resume(temp_path, job_description)
                if processed_data:
                    results.append(processed_data)
            except Exception as e:
                logger.error(f"Error processing resume {file.filename}: {e}")
                continue

        results.sort(key=lambda x: x['score'], reverse=True)
        
        session_id = str(uuid.uuid4())
        new_session = ScreeningSession(id=session_id, user_id=current_user.id, job_description=job_description)
        db.session.add(new_session)

        for processed_data in results:
            cand_entry = Candidate(session_id=session_id, data=json.dumps(processed_data))
            db.session.add(cand_entry)
            
        db.session.commit()
        session['last_screening_id'] = session_id
        session.modified = True
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({"status": "success", "redirect": url_for('results_view')})
        return redirect(url_for('results_view'))

    return render_template("screen.html")

@app.route("/results")
@login_required
def results_view():
    session_id = session.get('last_screening_id')
    if not session_id:
        return redirect(url_for('screen'))
        
    screening_session = ScreeningSession.query.get(session_id)
    if not screening_session or screening_session.user_id != current_user.id:
        return redirect(url_for('screen'))
    
    candidates = Candidate.query.filter_by(session_id=session_id).all()
    results_list = [json.loads(c.data) for c in candidates]
    results_list.sort(key=lambda x: x['score'], reverse=True)
    
    return render_template("results.html", results=results_list, job_description=screening_session.job_description)

@app.route("/candidate/<int:index>")
@login_required
def candidate_detail(index):
    session_id = session.get('last_screening_id')
    if not session_id: return redirect(url_for('screen'))
    
    screening_session = db.session.get(ScreeningSession, session_id)
    if not screening_session: return redirect(url_for('screen'))
    
    candidates = Candidate.query.filter_by(session_id=session_id).all()
    results_list = [json.loads(c.data) for c in candidates]
    results_list.sort(key=lambda x: x['score'], reverse=True)
    
    if 0 <= index < len(results_list):
        candidate = results_list[index]
        return render_template("candidate_detail.html", candidate=candidate, index=index)
    return redirect(url_for('results_view'))

@app.route("/export")
@login_required
def export_csv():
    session_id = session.get('last_screening_id')
    if not session_id: return redirect(url_for('screen'))
    
    candidates = Candidate.query.filter_by(session_id=session_id).all()
    results_list = [json.loads(c.data) for c in candidates]
    results_list.sort(key=lambda x: x['score'], reverse=True)
    
    if not results_list: return redirect(url_for('results_view'))
    
    si = io.StringIO()
    cw = csv.DictWriter(si, fieldnames=results_list[0].keys())
    cw.writeheader()
    cw.writerows(results_list)
    
    output = make_response(si.getvalue())
    output.headers["Content-Disposition"] = "attachment; filename=esctrix_shortlist.csv"
    output.headers["Content-type"] = "text/csv"
    return output

@app.route("/ats-check", methods=["GET", "POST"])
@login_required
def ats_check():
    if request.method == "POST":
        job_description = request.form.get("job_description")
        resume_file = request.files.get("resume")
        
        if not job_description or not resume_file or resume_file.filename == '':
            return render_template("ats_check.html", error="Please provide both a resume and a job description.")
            
        upload_dir = "uploaded_resumes"
        os.makedirs(upload_dir, exist_ok=True)
        temp_path = os.path.join(upload_dir, resume_file.filename)
        resume_file.save(temp_path)
        
        try:
            result = check_ats_score(temp_path, job_description)
            session['ats_result'] = json.dumps(result)
            
            # Save to ATS History
            if current_user.is_authenticated:
                ats_check_entry = ATSCheck(
                    user_id=current_user.id,
                    job_description=job_description,
                    resume_filename=resume_file.filename,
                    score=result.get('total_score', 0),
                    result_data=json.dumps(result)
                )
                db.session.add(ats_check_entry)
                db.session.commit()
                
            return redirect(url_for('ats_result'))
        except Exception as e:
            logger.error(f"Error checking ATS score: {e}")
            return render_template("ats_check.html", error=f"Processing Error: {str(e)}")
            
    return render_template("ats_check.html")

@app.route("/ats-result")
@login_required
def ats_result():
    result_json = session.get('ats_result')
    if not result_json:
        return redirect(url_for('ats_check'))
    
    result = json.loads(result_json)
    if "error" in result:
        return render_template("ats_check.html", error=result["error"])
        
    return render_template("ats_result.html", result=result)

@app.route("/history")
@login_required
def history():
    # Only show history if user is a candidate, though admins can also view their own checks if they want
    checks = ATSCheck.query.filter_by(user_id=current_user.id).order_by(ATSCheck.created_at.desc()).all()
    
    history_data = []
    for check in checks:
        result_dict = json.loads(check.result_data)
        history_data.append({
            'id': check.id,
            'date': check.created_at.strftime('%Y-%m-%d %H:%M'),
            'filename': check.resume_filename,
            'score': check.score,
            'missing_skills': result_dict.get('missing_skills', [])
        })
        
    return render_template("history.html", history=history_data)

@app.route("/send_invite", methods=["POST"])
@login_required
def send_invite():
    data = request.json
    email = data.get('email')
    candidate_name = data.get('name')
    
    # Simulate Email Sending directly to terminal
    print("\n" + "="*50)
    print("🚀 AUTOMATED SYSTEM EMAIL DISPATCHED 🚀")
    print(f"To: {email}")
    print(f"Subject: Interview Invitation - ESCTRIX Platform")
    print(f"Body: Dear {candidate_name},\n\nWe were impressed by your profile. Please use the link below to schedule an interview with our technical team.\n\nBest,\nThe Hiring Team")
    print("="*50 + "\n")
    
    return jsonify({"status": "success", "message": f"Email successfully dispatched to {email}"})

# Register Blueprints (Shared between Dev and Production)
from admin import admin_bp
app.register_blueprint(admin_bp)
app.register_blueprint(coding_bp)
app.register_blueprint(interview_bp)

if __name__ == "__main__":
    os.makedirs("uploaded_resumes", exist_ok=True)
    with app.app_context():
        db.create_all()
    
    print("\n" + "[+] " + "="*50)
    print("   ESCTRIX PLATFORM - SMART RECRUITMENT ENGINE   ")
    print("   Live Coding + AI Interview Modules Active     ")
    print("="*54 + "\n")
    
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
