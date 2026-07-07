from database.db import db
from datetime import datetime

class BurnoutAssessment(db.Model):
    __tablename__ = "burnout_assessments"

    assessment_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))
    session_id = db.Column(db.Integer, db.ForeignKey("interview_sessions.session_id"))

    assessment_date = db.Column(db.DateTime, default=datetime.utcnow)

    burnout_score = db.Column(db.Float)
    wellness_score = db.Column(db.Float)
    risk_level = db.Column(db.String(30))

    sleep_score = db.Column(db.Float)
    stress_score = db.Column(db.Float)
    motivation_score = db.Column(db.Float)
    academic_load_score = db.Column(db.Float)
    emotional_exhaustion_score = db.Column(db.Float)
    cognitive_score = db.Column(db.Float)
    lifestyle_score = db.Column(db.Float)
    mental_energy_score = db.Column(db.Float)
    mood_score = db.Column(db.Float)
    productivity_score = db.Column(db.Float)

    primary_contributors = db.Column(db.Text)
    recovery_focus_areas = db.Column(db.Text)
    category_summaries = db.Column(db.Text)

    engine_version = db.Column(db.String(20), default="1.0")