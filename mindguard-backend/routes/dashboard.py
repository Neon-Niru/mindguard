from flask import Blueprint, jsonify, request
from datetime import date, datetime
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.planner import PlannerTask
from utils.auth import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
@jwt_required
def dashboard():
    user_id = request.current_user_id

    previous = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_id.desc()
    ).offset(1).first()

    latest = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_id.desc()
    ).first()

    if latest is None:
        return jsonify({
            "has_assessment": False,
            "message": "No assessment found"
        })

    previous_comparison = None
    if previous:
        previous_comparison = {
            "wellness_score": previous.wellness_score,
            "burnout_score": previous.burnout_score
        }

    today = date.today()
    planner_tasks = PlannerTask.query.filter(
        PlannerTask.user_id == user_id,
        PlannerTask.created_at >= datetime(today.year, today.month, today.day)
    ).all()
    total_tasks = len(planner_tasks)
    completed_tasks = sum(1 for t in planner_tasks if t.completed)
    planner_progress = round((completed_tasks / total_tasks * 100)) if total_tasks > 0 else 0

    goals = RecoveryGoal.query.filter_by(
        user_id=user_id,
        completed=False
    ).limit(5).all()

    recovery_goals = [
        {
            "goal_id": g.goal_id,
            "goal": g.goal,
            "completed": g.completed
        }
        for g in goals
    ]

    return jsonify({
        "has_assessment": True,
        "wellness_score": latest.wellness_score,
        "burnout_score": latest.burnout_score,
        "risk_level": latest.risk_level,
        "sleep_score": latest.sleep_score,
        "stress_score": latest.stress_score,
        "motivation_score": latest.motivation_score,
        "productivity_score": latest.productivity_score,
        "mood_score": latest.mood_score,
        "previous_comparison": previous_comparison,
        "planner_progress": planner_progress,
        "recovery_goals": recovery_goals
    })
