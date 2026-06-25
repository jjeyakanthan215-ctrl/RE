from flask import Blueprint, render_template, redirect, url_for, flash # type: ignore
from flask_login import login_required, current_user # type: ignore
import json

admin_bp = Blueprint('admin', __name__)

def admin_only(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # We check for the name "Jerry" or if they have the recruiter role
        if not current_user.is_authenticated or (current_user.name.lower() != 'jerry' and current_user.role != 'recruiter'):
            flash("Access Denied: Administrative privileges required.")
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_only
def dashboard():  # sourcery skip: comprehension-to-generator
    from database import db, User, ScreeningSession, ATSCheck  # noqa: F401
    # Jerry can see EVERYONE'S sessions
    all_sessions = db.session.query(ScreeningSession).order_by(ScreeningSession.created_at.desc()).all()
    
    # Analytics
    total_ats_checks = db.session.query(ATSCheck).count()
    all_checks = db.session.query(ATSCheck).all()
    avg_score = 0
    if total_ats_checks > 0:
        avg_score = sum([c.score for c in all_checks]) / total_ats_checks
        
    return render_template('admin_dashboard.html', sessions=all_sessions, total_ats_checks=total_ats_checks, avg_score=round(avg_score))

@admin_bp.route('/admin/session/<session_id>')
@login_required
@admin_only
def view_session(session_id):
    from database import db, Candidate, ScreeningSession
    session_data = db.session.get(ScreeningSession, session_id)
    if not session_data:
        flash("Session not found.")
        return redirect(url_for('admin.dashboard'))
    
    candidates = db.session.query(Candidate).filter_by(session_id=session_id).all()
    results_list = [json.loads(c.data) for c in candidates]
    results_list.sort(key=lambda x: x.get('score', 0), reverse=True)
    
    return render_template("results.html", results=results_list, job_description=session_data.job_description)

@admin_bp.route('/admin/delete/<session_id>')
@login_required
@admin_only
def delete_session(session_id):  # sourcery skip: use-named-expression
    from database import db, ScreeningSession
    session_data = db.session.get(ScreeningSession, session_id)
    if session_data:
        db.session.delete(session_data)
        db.session.commit()
        flash("Screening record deleted successfully.")
    else:
        flash("Record not found.")
    return redirect(url_for('admin.dashboard'))
