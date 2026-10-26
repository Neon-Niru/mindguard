from collections import OrderedDict
from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request

from models.assessment import BurnoutAssessment
from models.planner import PlannerTask
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

progress_bp = Blueprint("progress", __name__)

MAX_WEEKS = 8


def _serialize_assessment(assessment):
    return {
        "assessment_id": assessment.assessment_id,
        "date": str(assessment.assessment_date) if assessment.assessment_date else None,
        "burnout_score": assessment.burnout_score,
        "wellness_score": assessment.wellness_score,
        "risk_level": assessment.risk_level,
        "engine_version": assessment.engine_version,
        "sleep_score": assessment.sleep_score,
        "stress_score": assessment.stress_score,
        "motivation_score": assessment.motivation_score,
        "academic_load_score": assessment.academic_load_score,
        "emotional_exhaustion_score": assessment.emotional_exhaustion_score,
        "cognitive_score": assessment.cognitive_score,
        "lifestyle_score": assessment.lifestyle_score,
        "mental_energy_score": assessment.mental_energy_score,
        "mood_score": assessment.mood_score,
        "productivity_score": assessment.productivity_score,
        "primary_contributors": assessment.primary_contributors or [],
        "recovery_focus_areas": assessment.recovery_focus_areas or [],
        "category_summaries": assessment.category_summaries or {},
    }


def _week_start(moment):
    return (moment - timedelta(days=moment.weekday())).date()


def _planner_history(tasks):
    """Weekly planner completion for the last few weeks.

    A task counts towards the week it was created in, which makes the chart
    show "how much of what I planned did I finish" rather than simply
    replaying the wellness score.
    """
    buckets = OrderedDict()

    for task in tasks:
        created = task.created_at or task.completion_date
        if not created:
            continue

        week = _week_start(created)
        bucket = buckets.setdefault(
            week,
            {"total": 0, "completed": 0},
        )
        bucket["total"] += 1
        if task.completed:
            bucket["completed"] += 1

    weeks = sorted(buckets.items())[-MAX_WEEKS:]

    history = []
    for week, stats in weeks:
        percent = (
            round(stats["completed"] / stats["total"] * 100)
            if stats["total"] else 0
        )
        history.append({
            "label": week.isoformat(),
            "week_start": week.isoformat(),
            "total": stats["total"],
            "completed": stats["completed"],
            "percent": percent,
        })

    return history


@progress_bp.route("/progress")
@jwt_required
def progress():
    user_id = request.current_user_id

    assessments = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_date
    ).all()

    goals = RecoveryGoal.query.filter_by(user_id=user_id).all()
    total_goals = len(goals)
    completed_goals = sum(1 for g in goals if g.completed)

    tasks = PlannerTask.query.filter_by(user_id=user_id).all()
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.completed)

    return jsonify({
        "assessments": [_serialize_assessment(a) for a in assessments],
        "recovery_goals": {
            "total": total_goals,
            "completed": completed_goals,
            "percent": (
                round(completed_goals / total_goals * 100)
                if total_goals else 0
            ),
        },
        "planner": {
            "total": total_tasks,
            "completed": completed_tasks,
            "percent": (
                round(completed_tasks / total_tasks * 100)
                if total_tasks else 0
            ),
            "history": _planner_history(tasks),
        },
    })
