import json
import logging
from flask import Blueprint, request, jsonify

from database.db import db
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.planner import PlannerTask
from engine.burnout_engine import BurnoutEngine
from ai_engine.conversation_manager import process_message
from ai_engine.state_manager import (
    create_state,
    refresh_state,
    get_missing_fields,
    get_missing_categories,
)
from ai_engine.llm_connector import LLMServiceError
from utils.auth import jwt_required

logger = logging.getLogger(__name__)

interview_bp = Blueprint("interview", __name__)


def _compute_fallback_report(state_data: dict) -> dict:
    """Dynamically estimate burnout and wellness scores based on collected text

    if the BurnoutEngine fails or raises an unhandled exception.
    """
    text_blob = str(state_data).lower()
    
    positive_words = [
        "rested", "good", "great", "light", "fine", "happy", 
        "pretty good", "solid", "well", "10", "9", "8", "manageable"
    ]
    negative_words = [
        "heavy", "exhausted", "tired", "stressed", "overwhelmed", 
        "burnt", "burnout", "bad", "awful", "hard", "struggling"
    ]
    
    pos_count = sum(1 for w in positive_words if w in text_blob)
    neg_count = sum(1 for w in negative_words if w in text_blob)

    if pos_count >= neg_count:
        burnout_score = max(10, 35 - (pos_count * 5))
        wellness_score = 100 - burnout_score
        risk_level = "Low"
        contributors = ["General Check-in"]
        focus_areas = ["Maintain healthy sleep routine", "Keep balanced study habits"]
    else:
        burnout_score = min(90, 60 + (neg_count * 10))
        wellness_score = 100 - burnout_score
        risk_level = "High" if burnout_score > 75 else "Moderate"
        contributors = ["Academic Load", "Emotional Exhaustion"]
        focus_areas = ["Reduce workload overload", "Break assignments into smaller tasks"]

    return {
        "burnout_score": burnout_score,
        "wellness_score": wellness_score,
        "risk_level": risk_level,
        "primary_contributors": contributors,
        "recovery_focus_areas": focus_areas,
        "category_summaries": {}
    }


@interview_bp.route("/interview", methods=["POST"])
@jwt_required
def interview():
    user_id = request.current_user_id
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    message = data.get("message", "")
    session_id = data.get("session_id")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "message is required"}), 400
    if len(message) > 4000:
        return jsonify({"error": "message is too long (maximum 4000 characters)"}), 400

    if session_id:
        session = InterviewSession.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not session:
            return jsonify({"error": "Session not found"}), 404

        collected = session.collected_facts or {}
        history_raw = session.conversation_history or "[]"
        try:
            history = (
                json.loads(history_raw)
                if isinstance(history_raw, str)
                else history_raw
            )
        except (json.JSONDecodeError, TypeError):
            history = []

        state = refresh_state({
            "data": collected,
            "history": history,
        })
    else:
        session = InterviewSession(user_id=user_id)
        db.session.add(session)
        db.session.flush()
        state = create_state()

    try:
        ai_result = process_message(message, state)
    except LLMServiceError as error:
        db.session.rollback()
        return jsonify({"error": str(error)}), 503
    except Exception as e:
        logger.error(f"Error processing message: {e}", exc_info=True)
        db.session.rollback()
        return jsonify({
            "complete": False,
            "reply": "I'm right here with you. How has your sleep and workload been feeling lately?",
            "session_id": session.session_id,
            "missing_categories": [],
            "missing_fields": [],
        }), 200

    state = ai_result["state"]
    session.collected_facts = state.get("data", {})
    session.conversation_history = json.dumps(state.get("history", []))
    db.session.commit()

    is_finished = ai_result.get("complete", False)
    if not is_finished:
        return jsonify({
            "complete": False,
            "reply": ai_result.get("reply", "Thanks for sharing."),
            "session_id": session.session_id,
            "missing_categories": get_missing_categories(state),
            "missing_fields": get_missing_fields(state),
        }), 200

    session.interview_status = "Completed"
    report = ai_result.get("report")
    if not report:
        try:
            report = BurnoutEngine.generate_report(state.get("data", {}))
        except Exception as report_err:
            logger.error(f"BurnoutEngine failed: {report_err}", exc_info=True)
            report = _compute_fallback_report(state.get("data", {}))

    try:
        assessment = BurnoutAssessment(
            user_id=user_id,
            session_id=session.session_id,
            burnout_score=report.get("burnout_score", 50),
            wellness_score=report.get("wellness_score", 50),
            risk_level=report.get("risk_level", "Moderate"),
            sleep_score=report.get("sleep_score"),
            stress_score=report.get("stress_score"),
            motivation_score=report.get("motivation_score"),
            academic_load_score=report.get("academic_load_score"),
            emotional_exhaustion_score=report.get("emotional_exhaustion_score"),
            cognitive_score=report.get("cognitive_score"),
            lifestyle_score=report.get("lifestyle_score"),
            mental_energy_score=report.get("mental_energy_score"),
            mood_score=report.get("mood_score"),
            productivity_score=report.get("productivity_score"),
            primary_contributors=report.get("primary_contributors", []),
            recovery_focus_areas=report.get("recovery_focus_areas", []),
            category_summaries=report.get("category_summaries", {}),
        )

        db.session.add(assessment)
        db.session.commit()

        for goal_text in report.get("recovery_focus_areas", []):
            goal = RecoveryGoal(
                assessment_id=assessment.assessment_id,
                user_id=user_id,
                goal=goal_text,
            )
            db.session.add(goal)
            db.session.flush()

            task = PlannerTask(
                user_id=user_id,
                goal_id=goal.goal_id,
                title=goal_text,
                category="Recovery",
                priority="Medium",
                task_source="ENGINE",
                completed=False,
            )
            db.session.add(task)

        db.session.commit()
        assessment_id = assessment.assessment_id
    except Exception as db_err:
        logger.error(f"Failed to persist assessment to DB: {db_err}", exc_info=True)
        db.session.rollback()
        assessment_id = None

    return jsonify({
        "complete": True,
        "message": "Interview complete",
        "reply": ai_result.get("reply", "Here is your wellness report:"),
        "session_id": session.session_id,
        "assessment_id": assessment_id,
        "report": {
            "burnout_score": report.get("burnout_score", 50),
            "wellness_score": report.get("wellness_score", 50),
            "risk_level": report.get("risk_level", "Moderate"),
            "primary_contributors": report.get("primary_contributors", []),
            "recovery_focus_areas": report.get("recovery_focus_areas", []),
            "category_summaries": report.get("category_summaries", {}),
        },
    }), 200