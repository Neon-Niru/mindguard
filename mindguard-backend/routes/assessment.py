from flask import Blueprint, jsonify, request
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/assessment/<int:id>")
@jwt_required
def get_assessment(id):
    assessment = BurnoutAssessment.query.filter_by(
        assessment_id=id,
        user_id=request.current_user_id,
    ).first()

    if not assessment:
        return jsonify({"error": "Assessment not found"}), 404

    goals = RecoveryGoal.query.filter_by(
        assessment_id=assessment.assessment_id,
        user_id=request.current_user_id,
    ).all()

    return jsonify({
        "assessment_id": assessment.assessment_id,
        "session_id": assessment.session_id,
        "date": str(assessment.assessment_date),
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
        "primary_contributors": assessment.primary_contributors,
        "recovery_focus_areas": assessment.recovery_focus_areas,
        "category_summaries": assessment.category_summaries,
        "goals": [
            {
                "goal_id": goal.goal_id,
                "goal": goal.goal,
                "completed": goal.completed,
            }
            for goal in goals
        ],
    })
