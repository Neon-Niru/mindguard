from database.db import db
from datetime import datetime

class InterviewSession(db.Model):
    __tablename__ = "interview_sessions"

    session_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    interview_date = db.Column(db.DateTime, default=datetime.utcnow)
    conversation_history = db.Column(db.Text)
    interview_status = db.Column(db.String(30), default="Completed")