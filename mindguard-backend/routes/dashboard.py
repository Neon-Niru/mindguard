from datetime import date, datetime, time

from flask import Blueprint, jsonify, request

from models.assessment import BurnoutAssessment
from models.planner import PlannerTask
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

dashboard_bp = Blueprint("dashboard", __name__)


def _today_tasks(user_id, today):
    """Tasks that are relevant *today*: due today, overdue, or undated
    tasks created today. Completed tasks only count when they were either
    due today or completed today, so old history does not inflate progress.
    """
    today_str = today.isoformat()
    start_of_day = datetime.combine(today, time.min)

    tasks = PlannerTask.query.filter(PlannerTask.user_id == user_id).all()

    relevant = []
    for task in tasks:
        due = (task.due_date or "").strip()

        if due == today_str:
            relevant.append(task)
        elif due and due < today_str and not task.completed:
            # Overdue and still open: it belongs in today's workload.
            relevant.append(task)
        elif not due and task.created_at and task.created_at >= start_of_day:
            relevant.append(task)
        elif task.completed and task.completion_date and task.completion_date >= start_of_day:
            relevant.append(task)

    return relevant


@dashboard_bp.route("/dashboard")
@jwt_required
def dashboard():
    user_id = request.current_user_id

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

    previous = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_id.desc()
    ).offset(1).first()

    previous_comparison = None
    if previous:
        previous_comparison = {
            "wellness_score": previous.wellness_score,
            "burnout_score": previous.burnout_score,
            "assessment_date": str(previous.assessment_date) if previous.assessment_date else None,
        }

    tasks = _today_tasks(user_id, date.today())
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.completed)
    planner_progress = (
        round(completed_tasks / total_tasks * 100) if total_tasks else 0
    )

    goals = RecoveryGoal.query.filter_by(
        user_id=user_id,
        completed=False
    ).order_by(RecoveryGoal.goal_id.desc()).limit(5).all()

    return jsonify({
        "has_assessment": True,
        "assessment_id": latest.assessment_id,
        "assessment_date": str(latest.assessment_date) if latest.assessment_date else None,
        "engine_version": latest.engine_version,
        "wellness_score": latest.wellness_score,
        "burnout_score": latest.burnout_score,
        "risk_level": latest.risk_level,
        "sleep_score": latest.sleep_score,
        "stress_score": latest.stress_score,
        "motivation_score": latest.motivation_score,
        "productivity_score": latest.productivity_score,
        "mood_score": latest.mood_score,
        "emotional_exhaustion_score": latest.emotional_exhaustion_score,
        "academic_load_score": latest.academic_load_score,
        "primary_contributors": latest.primary_contributors or [],
        "recovery_focus_areas": latest.recovery_focus_areas or [],
        "previous_comparison": previous_comparison,
        "planner_total": total_tasks,
        "planner_completed": completed_tasks,
        "planner_progress": planner_progress,
        "recovery_goals": [
            {
                "goal_id": goal.goal_id,
                "goal": goal.goal,
                "completed": bool(goal.completed),
            }
            for goal in goals
        ],
    })
