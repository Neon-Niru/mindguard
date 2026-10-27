from flask import Blueprint, jsonify, request
from models.assessment import BurnoutAssessment
from utils.auth import jwt_required

assessment_bp = Blueprint("assessment", __name__)


@assessment_bp.route("/assessment/<int:id>")
@jwt_required
def get_assessment(id):
    a = BurnoutAssessment.query.get_or_404(id)
    return jsonify({
        "assessment_id": a.assessment_id,
        "user_id": a.user_id,
        "session_id": a.session_id,
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
        "recovery_focus_areas": a.recovery_focus_areas,
        "category_summaries": a.category_summaries
    })
