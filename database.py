from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime, timezone

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(200))
    role = db.Column(db.String(20), default='candidate')
    sessions = db.relationship('ScreeningSession', backref='user', lazy=True)
    ats_history = db.relationship('ATSCheck', backref='user', lazy=True, cascade="all, delete-orphan")

class ScreeningSession(db.Model):
    id = db.Column(db.String(36), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    job_description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    candidates = db.relationship('Candidate', backref='session', lazy=True, cascade="all, delete-orphan")

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_id = db.Column(db.String(36), db.ForeignKey('screening_session.id'))
    data = db.Column(db.Text)

class ATSCheck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    job_description = db.Column(db.Text)
    resume_filename = db.Column(db.String(200))
    score = db.Column(db.Integer)
    result_data = db.Column(db.Text)
