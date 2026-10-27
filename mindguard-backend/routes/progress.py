from flask import Blueprint, jsonify, request
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

progress_bp = Blueprint("progress", __name__)


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

    return jsonify({
        "assessments": [
            {
                "assessment_id": a.assessment_id,
                "date": str(a.assessment_date),
                "burnout_score": a.burnout_score,
                "wellness_score": a.wellness_score,
                "risk_level": a.risk_level,
                "sleep_score": a.sleep_score,
                "stress_score": a.stress_score,
                "motivation_score": a.motivation_score,
                "academic_load_score": a.academic_load_score,
                "emotional_exhaustion_score": a.emotional_exhaustion_score,
                "cognitive_score": a.cognitive_score,
                "lifestyle_score": a.lifestyle_score,
                "mental_energy_score": a.mental_energy_score,
                "mood_score": a.mood_score,
                "productivity_score": a.productivity_score,
                "primary_contributors": a.primary_contributors,
                "recovery_focus_areas": a.recovery_focus_areas
            }
            for a in assessments
        ],
        "recovery_goals": {
            "total": total_goals,
            "completed": completed_goals
        }
    })
