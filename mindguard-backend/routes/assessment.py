from flask import Blueprint, jsonify
from models.assessment import BurnoutAssessment

assessment_bp = Blueprint("assessment", __name__)

@assessment_bp.route("/assessment/<int:id>")
def assessment(id):

    a = BurnoutAssessment.query.get_or_404(id)

    return jsonify({
        "assessment_id": a.assessment_id,
        "burnout_score": a.burnout_score,
        "wellness_score": a.wellness_score,
        "risk_level": a.risk_level,
        "sleep_score": a.sleep_score,
        "stress_score": a.stress_score,
        "motivation_score": a.motivation_score,
        "productivity_score": a.productivity_score,
        "primary_contributors": a.primary_contributors,
        "recovery_focus_areas": a.recovery_focus_areas
    })