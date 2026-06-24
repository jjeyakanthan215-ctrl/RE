"""
ESCTRIX - AI Mock Interview Module
Blueprint: interview_bp
Routes: /mock-interview (GET), /mock-interview/respond (POST)
 
Uses a Smart Simulation Engine: reads the candidate's ATS interview
questions from session, presents them one-by-one, analyzes the
user's answers via keyword matching, and grades the response.
No external API key required.
"""
from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
import json

interview_bp = Blueprint('interview', __name__)

# Fallback generic questions if no ATS data is in session
FALLBACK_QUESTIONS = [
    "Tell me about yourself and your technical background.",
    "What is your greatest strength as a software developer?",
    "Describe a challenging project you've worked on. How did you overcome the obstacles?",
    "Where do you see yourself in 5 years, and how does this role fit into your career path?",
    "Do you have any questions for us about the role or the company?"
]

# Feedback templates for grading
POSITIVE_FEEDBACK = [
    "Great answer! You gave a clear, structured response.",
    "Excellent! You highlighted the right points effectively.",
    "Strong response. Your answer demonstrated solid understanding.",
    "Very good! That was a well-organized and confident answer.",
]
NEGATIVE_FEEDBACK = [
    "Your answer could be stronger. Try using the STAR method: Situation, Task, Action, Result.",
    "Good start, but try to add more specific examples from your experience.",
    "Consider elaborating more — be specific about the technologies or methodologies you used.",
    "Try to be more concise and structured. A focused, 2-3 minute answer is ideal.",
]


def evaluate_answer(question, answer):
    """
    Enhanced evaluator to detect intent and provide guidance.
    Returns: (score, feedback, grade, should_retry)
    """
    if not answer:
        return 0, "Please provide an answer to continue.", "Empty", True

    ans = answer.strip().lower()
    
    # 1. Detect Greetings/Small Talk
    greetings = ['hi', 'hello', 'hey', 'good morning', 'good afternoon', 'sup', 'yo']
    if any(ans == g for g in greetings) or len(ans) < 5:
        return 0, "Hello! I'm ready when you are. Please provide a detailed response to the question above so I can evaluate your skills.", "Greeting", True

    # 2. Detect "I don't know" / Evasive answers
    evasive_terms = ["don't know", "dont know", "not sure", "no idea", "can't say", "forget", "no experience"]
    if any(term in ans for term in evasive_terms) and len(ans) < 30:
        return 30, "It's okay to not know everything! Try to describe a related concept you ARE familiar with, or tell me how you would find the answer.", "Guidance", False

    # 3. Detect Irrelevant/Non-technical filler
    filler_terms = ["blah", "test", "asdf", "okay", "fine", "yes", "no"]
    if ans in filler_terms:
         return 10, "I need a bit more than that to help you practice! Try explaining your thought process step-by-step.", "Too Short", True

    # --- Normal Evaluation ---
    word_count = len(answer.split())
    score = 0

    # Length score (max 40 pts)
    if word_count >= 40: score += 40
    elif word_count >= 20: score += 25
    else: score += 10

    # Keyword vocabulary (max 40 pts)
    strong_keywords = [
        'developed', 'implemented', 'designed', 'built', 'optimized', 'improved',
        'led', 'managed', 'collaborated', 'created', 'analyzed', 'solved',
        'result', 'success', 'achieved', 'delivered', 'experience', 'learned',
        'python', 'java', 'sql', 'api', 'team', 'project', 'system', 'data',
        'challenge', 'solution', 'approach', 'strategy', 'framework', 'deploy'
    ]
    keyword_hits = sum(1 for kw in strong_keywords if kw in ans)
    score += min(40, keyword_hits * 10)

    # Confidence indicators (max 20 pts)
    confidence_words = ['i', "i've", "i'm", 'my', 'we', 'our', 'specifically', 'example', 'situation']
    confidence_hits = sum(1 for cw in confidence_words if cw in ans.split())
    score += min(20, confidence_hits * 5)

    score = min(100, score)

    import random
    if score >= 75:
        feedback_text = random.choice(POSITIVE_FEEDBACK)
        grade = "Strong"
    elif score >= 50:
        feedback_text = random.choice(NEGATIVE_FEEDBACK[1:3])
        grade = "Average"
    else:
        feedback_text = NEGATIVE_FEEDBACK[0]
        grade = "Needs Work"

    return score, feedback_text, grade, False


@interview_bp.route('/mock-interview')
@login_required
def mock_interview():
    """Load the interview page. Pull questions from ATS session if available."""
    # Try to get ATS-generated interview questions from session
    ats_data_json = session.get('ats_result')
    interview_questions = FALLBACK_QUESTIONS

    if ats_data_json:
        try:
            ats_data = json.loads(ats_data_json)
            ats_questions = ats_data.get('interview_questions', [])
            if ats_questions and len(ats_questions) >= 3:
                interview_questions = ats_questions
        except Exception:
            pass

    # Store questions in the Flask session for the respond route
    session['interview_questions'] = interview_questions

    return render_template('interview.html',
                           questions=interview_questions,
                           name=current_user.name)


@interview_bp.route('/mock-interview/respond', methods=['POST'])
@login_required
def respond():
    """Evaluate a candidate's answer and return feedback + next question."""
    data = request.get_json()
    question = data.get('question', '')
    answer = data.get('answer', '')
    question_index = data.get('question_index', 0)

    questions = session.get('interview_questions', FALLBACK_QUESTIONS)

    score, feedback, grade, should_retry = evaluate_answer(question, answer)
    
    # If retry, don't return next question yet
    if should_retry:
        return jsonify({
            'score': 0,
            'feedback': feedback,
            'grade': 'Guidance',
            'next_question': None,
            'should_retry': True,
            'is_last': False
        })

    # Check if there's a next question
    next_question = None
    if question_index + 1 < len(questions):
        next_question = questions[question_index + 1]

    return jsonify({
        'score': score,
        'feedback': feedback,
        'grade': grade,
        'next_question': next_question,
        'should_retry': False,
        'is_last': next_question is None
    })
