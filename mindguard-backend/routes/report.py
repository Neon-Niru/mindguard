from flask import Blueprint, jsonify, request
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

report_bp = Blueprint("report", __name__)


@report_bp.route("/report")
@jwt_required
def report():
    user_id = request.current_user_id

    assessment = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_id.desc()
    ).first()

    if not assessment:
        return jsonify({"message": "No assessment found"}), 404

    goals = RecoveryGoal.query.filter_by(
        assessment_id=assessment.assessment_id
    ).all()

    return jsonify({
        "assessment_id": assessment.assessment_id,
        "burnout_score": assessment.burnout_score,
        "wellness_score": assessment.wellness_score,
        "risk_level": assessment.risk_level,
        "category_scores": {
            "sleep": assessment.sleep_score,
            "stress": assessment.stress_score,
            "motivation": assessment.motivation_score,
            "academic_load": assessment.academic_load_score,
            "emotional_exhaustion": assessment.emotional_exhaustion_score,
            "cognitive": assessment.cognitive_score,
            "lifestyle": assessment.lifestyle_score,
            "mental_energy": assessment.mental_energy_score,
            "mood": assessment.mood_score,
            "productivity": assessment.productivity_score
        },
        "contributors": assessment.primary_contributors,
        "focus": assessment.recovery_focus_areas,
        "goals": [g.goal for g in goals]
    })
