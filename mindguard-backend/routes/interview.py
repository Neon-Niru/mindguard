import json
from flask import Blueprint, request, jsonify
from database.db import db
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.planner import PlannerTask
from models.settings import UserSettings
from engine.burnout_engine import BurnoutEngine
from ai_engine.conversation_manager import process_message
from ai_engine.llm_connector import FALLBACK_QUESTIONS_MAP
from ai_engine.state_manager import (
    create_state,
    REQUIRED_INTERVIEW_CATEGORIES,
)
from utils.auth import jwt_required

MAX_INTERVIEW_ROUNDS = 20
MAX_MESSAGE_LENGTH = 4000
interview_bp = Blueprint("interview", __name__)


def _recalculate_missing(collected):
    return [cat for cat in REQUIRED_INTERVIEW_CATEGORIES if cat not in collected]


def _load_history(session):
    history_raw = session.conversation_history or "[]"
    try:
        return json.loads(history_raw) if isinstance(history_raw, str) else history_raw
    except (json.JSONDecodeError, TypeError):
        return []


def _build_state(session):
    collected = session.collected_facts or {}
    return {
        "data": collected,
        "completed": list(collected.keys()),
        "missing": _recalculate_missing(collected),
        "history": _load_history(session),
    }


def _user_tone(user_id):
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    return getattr(settings, "ai_tone", None) or "supportive"


def _create_recovery_plan(assessment, user_id, report):
    existing_titles = {
        title for (title,) in db.session.query(PlannerTask.title).filter_by(
            user_id=user_id,
            task_source="ENGINE",
            completed=False,
        ).all()
    }

    seen_goals = set()

    for goal_text in report.get("recovery_focus_areas", []):
        if not goal_text or goal_text in seen_goals:
            continue
        seen_goals.add(goal_text)

        goal = RecoveryGoal(
            assessment_id=assessment.assessment_id,
            user_id=user_id,
            goal=goal_text,
        )
        db.session.add(goal)
        db.session.flush()

        if goal_text in existing_titles:
            continue

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


@interview_bp.route("/interview", methods=["POST"])
@jwt_required
def interview():
    user_id = request.current_user_id
    data = request.get_json(silent=True)

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    message = (data.get("message") or "").strip()
    session_id = data.get("session_id")

    if not message:
        return jsonify({"error": "message is required"}), 400

    if len(message) > MAX_MESSAGE_LENGTH:
        return jsonify({
            "error": f"message must be {MAX_MESSAGE_LENGTH} characters or fewer"
        }), 400

    if session_id:
        session = InterviewSession.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not session:
            return jsonify({"error": "Session not found"}), 404

        if session.interview_status == "Completed":
            return jsonify({
                "error": "This interview is already complete. Start a new conversation.",
                "session_id": session.session_id,
            }), 409

        state = _build_state(session)
    else:
        session = InterviewSession(user_id=user_id)
        db.session.add(session)
        db.session.commit()
        state = create_state()

    ai_result = process_message(
        message,
        state,
        tone=_user_tone(user_id),
    )

    session.collected_facts = state.get("data", {})
    session.conversation_history = json.dumps(state.get("history", []))
    db.session.commit()

    is_finished = ai_result.get("complete", False)
    rounds = sum(
        1 for item in state.get("history", [])
        if item.get("role") == "student"
    )
    collected = state.get("data", {})

    if not is_finished and rounds >= MAX_INTERVIEW_ROUNDS:
        is_finished = True

    if not is_finished:
        reply = ai_result.get("reply")
        if not reply:
            missing = state.get("missing", [])
            if missing:
                reply = FALLBACK_QUESTIONS_MAP.get(
                    missing[0],
                    "Tell me more about how you've been feeling.",
                )
            else:
                reply = "I think I have enough information now."

        return jsonify({
            "complete": False,
            "reply": reply,
            "session_id": session.session_id,
            "missing_categories": state.get("missing", []),
            "round": rounds,
        })

    if not collected:
        session.interview_status = "Abandoned"
        db.session.commit()
        return jsonify({
            "error": (
                "I wasn't able to collect enough information to build a "
                "report. Please start a new conversation and share a little "
                "more about your week."
            ),
            "complete": False,
            "session_id": session.session_id,
        }), 422

    report = BurnoutEngine.generate_report(collected)

    assessment = BurnoutAssessment(
        user_id=user_id,
        session_id=session.session_id,
        burnout_score=report["burnout_score"],
        wellness_score=report["wellness_score"],
        risk_level=report["risk_level"],
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
        engine_version=report.get("engine_version"),
    )

    db.session.add(assessment)
    db.session.flush()

    _create_recovery_plan(assessment, user_id, report)

    session.interview_status = "Completed"
    db.session.commit()

    return jsonify({
        "complete": True,
        "message": "Interview complete",
        "session_id": session.session_id,
        "assessment_id": assessment.assessment_id,
        "report": {
            "burnout_score": report["burnout_score"],
            "wellness_score": report["wellness_score"],
            "risk_level": report["risk_level"],
            "engine_version": report.get("engine_version"),
            "categories_assessed": report.get("categories_assessed"),
            "data_completeness": report.get("data_completeness"),
            "category_scores": report.get("category_scores", {}),
            "primary_contributors": report.get("primary_contributors", []),
            "recovery_focus_areas": report.get("recovery_focus_areas", []),
            "category_summaries": report.get("category_summaries", {}),
        },
    })
