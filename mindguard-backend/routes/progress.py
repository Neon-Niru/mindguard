from flask import Blueprint, jsonify
from models.assessment import BurnoutAssessment

progress_bp = Blueprint("progress", __name__)

@progress_bp.route("/progress/<int:user_id>")
def progress(user_id):

    assessments = BurnoutAssessment.query.filter_by(
        user_id=user_id
    ).order_by(
        BurnoutAssessment.assessment_date
    ).all()

    return jsonify([
        {
            "assessment_id": a.assessment_id,
            "date": str(a.assessment_date),
            "burnout_score": a.burnout_score,
            "wellness_score": a.wellness_score
        }
        for a in assessments
    ])