from database.db import db
from datetime import datetime

class PlannerTask(db.Model):

    __tablename__ = "planner_tasks"

    task_id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.String(500))

    category = db.Column(db.String(50))

    due_date = db.Column(db.String(50))

    completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)