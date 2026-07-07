from flask import Blueprint, request, jsonify
from database.db import db
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal

interview_bp = Blueprint("interview", __name__)

@interview_bp.route("/interview", methods=["POST"])
def interview():

    data = request.get_json()

    user_id = data["user_id"]
    conversation = data["conversation"]

    session = InterviewSession(
        user_id=user_id,
        conversation_history=conversation
    )

    db.session.add(session)
    db.session.commit()

    burnout_score = 35
    wellness_score = 65

    assessment = BurnoutAssessment(
        user_id=user_id,
        session_id=session.session_id,

        burnout_score=burnout_score,
        wellness_score=wellness_score,
        risk_level="Low",

        sleep_score=75,
        stress_score=30,
        motivation_score=70,
        academic_load_score=50,
        emotional_exhaustion_score=35,
        cognitive_score=80,
        lifestyle_score=70,
        mental_energy_score=72,
        mood_score=78,
        productivity_score=74,

        primary_contributors="Stress",
        recovery_focus_areas="Sleep",
        category_summaries="{}"
    )

    db.session.add(assessment)
    db.session.commit()

    goal = RecoveryGoal(
        assessment_id=assessment.assessment_id,
        user_id=user_id,
        goal="Sleep before 11 PM for the next 5 days."
    )

    db.session.add(goal)
    db.session.commit()

    return jsonify({
        "message":"Interview Complete",
        "assessment_id":assessment.assessment_id,
        "burnout_score":burnout_score,
        "wellness_score":wellness_score
    })