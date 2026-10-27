from database.db import db
from datetime import datetime


class BurnoutAssessment(db.Model):

    __tablename__ = "burnout_assessments"


    assessment_id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )


    session_id = db.Column(
        db.Integer,
        db.ForeignKey("interview_sessions.session_id"),
        nullable=False
    )


    assessment_date = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    burnout_score = db.Column(
        db.Float,
        nullable=False
    )


    wellness_score = db.Column(
        db.Float,
        nullable=False
    )


    risk_level = db.Column(
        db.String(30),
        nullable=False
    )



    # Category health scores

    sleep_score = db.Column(
        db.Float
    )


    stress_score = db.Column(
        db.Float
    )


    motivation_score = db.Column(
        db.Float
    )


    academic_load_score = db.Column(
        db.Float
    )


    emotional_exhaustion_score = db.Column(
        db.Float
    )


    cognitive_score = db.Column(
        db.Float
    )


    lifestyle_score = db.Column(
        db.Float
    )


    mental_energy_score = db.Column(
        db.Float
    )


    mood_score = db.Column(
        db.Float
    )


    productivity_score = db.Column(
        db.Float
    )



    # Detailed engine output

    primary_contributors = db.Column(
        db.JSON,
        default=list
    )


    recovery_focus_areas = db.Column(
        db.JSON,
        default=list
    )


    category_summaries = db.Column(
        db.JSON,
        default=dict
    )


    engine_version = db.Column(
        db.String(20),
        default="1.0"
    )



    recovery_goals = db.relationship(
        "RecoveryGoal",
        backref="assessment",
        lazy=True
    )