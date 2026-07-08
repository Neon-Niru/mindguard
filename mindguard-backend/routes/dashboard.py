from flask import Blueprint, jsonify
from models.assessment import BurnoutAssessment

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard/<int:user_id>")
def dashboard(user_id):

    latest = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_id.desc()
    ).first()

    if latest is None:
        return jsonify({
            "message": "No assessment found"
        })

    return jsonify({

        "burnout_score": latest.burnout_score,
        "wellness_score": latest.wellness_score,
        "risk_level": latest.risk_level,

        "sleep": latest.sleep_score,
        "stress": latest.stress_score,
        "motivation": latest.motivation_score,
        "productivity": latest.productivity_score,

        "focus": latest.recovery_focus_areas
    })