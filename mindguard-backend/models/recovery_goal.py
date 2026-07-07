from database.db import db
from datetime import datetime

class RecoveryGoal(db.Model):
    __tablename__ = "recovery_goals"

    goal_id = db.Column(db.Integer, primary_key=True)

    assessment_id = db.Column(db.Integer, db.ForeignKey("burnout_assessments.assessment_id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.user_id"))

    goal = db.Column(db.String(300))

    completed = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow)