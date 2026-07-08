from database.db import db
from datetime import datetime


class User(db.Model):

    __tablename__ = "users"


    user_id = db.Column(
        db.Integer,
        primary_key=True
    )


    full_name = db.Column(
        db.String(100),
        nullable=False
    )


    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )


    password_hash = db.Column(
        db.String(255),
        nullable=False
    )


    account_created = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    last_login = db.Column(
        db.DateTime
    )


    reset_token = db.Column(
        db.String(255)
    )


    reset_token_expires_at = db.Column(
        db.DateTime
    )



    # Relationships

    interview_sessions = db.relationship(
        "InterviewSession",
        backref="user",
        lazy=True
    )


    assessments = db.relationship(
        "BurnoutAssessment",
        backref="user",
        lazy=True
    )


    recovery_goals = db.relationship(
        "RecoveryGoal",
        backref="user",
        lazy=True
    )


    planner_tasks = db.relationship(
        "PlannerTask",
        backref="user",
        lazy=True
    )


    settings = db.relationship(
        "UserSettings",
        backref="user",
        uselist=False,
        lazy=True
    )



    def __repr__(self):

        return f"<User {self.email}>"