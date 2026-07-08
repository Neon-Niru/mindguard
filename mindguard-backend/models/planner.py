from database.db import db
from datetime import datetime


class PlannerTask(db.Model):

    __tablename__ = "planner_tasks"


    task_id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False
    )


    goal_id = db.Column(
        db.Integer,
        db.ForeignKey("recovery_goals.goal_id"),
        nullable=True
    )


    title = db.Column(
        db.String(200),
        nullable=False
    )


    description = db.Column(
        db.String(500)
    )


    category = db.Column(
        db.String(50)
    )


    priority = db.Column(
        db.String(30),
        default="Medium"
    )


    due_date = db.Column(
        db.String(50)
    )


    due_time = db.Column(
        db.String(50)
    )


    task_source = db.Column(
        db.String(20),
        default="USER"
    )


    completed = db.Column(
        db.Boolean,
        default=False
    )


    completion_date = db.Column(
        db.DateTime,
        nullable=True
    )


    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )