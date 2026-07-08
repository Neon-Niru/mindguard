import json
from flask import Blueprint, request, jsonify
from database.db import db
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.planner import PlannerTask
from engine.burnout_engine import BurnoutEngine
from engine.schema import ENGINE_SCHEMA
from ai_engine.conversation_manager import process_message
from ai_engine.state_manager import create_state, is_complete, REQUIRED_INTERVIEW_CATEGORIES
from utils.auth import jwt_required

MAX_INTERVIEW_ROUNDS = 6
interview_bp = Blueprint("interview", __name__)


def _recalculate_missing(collected):
    return [cat for cat in REQUIRED_INTERVIEW_CATEGORIES if cat not in collected]


def _build_complete_facts(collected):
    facts = dict(collected)
    for cat, fields in ENGINE_SCHEMA.items():
        if cat not in facts:
            facts[cat] = {}
        for field_name, rules in fields.items():
            if field_name not in facts[cat]:
                ftype = rules.get("type", "")
                if ftype in ("continuous", "percentage"):
                    facts[cat][field_name] = rules.get("min", 50)
                else:
                    facts[cat][field_name] = "Sometimes"
    return facts


@interview_bp.route("/interview", methods=["POST"])
@jwt_required
def interview():
    user_id = request.current_user_id
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    message = data.get("message", "")
    session_id = data.get("session_id")

    if not message:
        return jsonify({"error": "message is required"}), 400

    if session_id:
        session = InterviewSession.query.filter_by(
            session_id=session_id, user_id=user_id
        ).first()
        if not session:
            return jsonify({"error": "Session not found"}), 404

        collected = session.collected_facts or {}
        history_raw = session.conversation_history or "[]"
        try:
            history = json.loads(history_raw) if isinstance(history_raw, str) else history_raw
        except (json.JSONDecodeError, TypeError):
            history = []

        missing = _recalculate_missing(collected)
        state = {
            "data": collected,
            "completed": list(collected.keys()),
            "missing": missing,
            "history": history,
        }
    else:
        session = InterviewSession(user_id=user_id)
        db.session.add(session)
        db.session.commit()
        state = create_state()

    ai_result = process_message(message, state)

    session.collected_facts = state.get("data", {})
    session.conversation_history = json.dumps(state.get("history", []))
    db.session.commit()

    is_finished = ai_result.get("complete", False)
    rounds = len(state.get("history", [])) // 2

    if not is_finished and rounds >= MAX_INTERVIEW_ROUNDS:
        is_finished = True

    if not is_finished:
        reply = ai_result.get("reply")
        if not reply:
            missing = state.get("missing", [])
            if missing:
                questions = {
                    "sleep": "How has your sleep been this week?",
                    "academic_load": "How are your studies going?",
                    "emotional_exhaustion": "Have you been feeling emotionally drained?",
                    "motivation": "How is your motivation for studying these days?",
                    "cognitive": "How is your concentration and memory?",
                    "stress": "How would you rate your stress level?",
                    "anxiety": "Do you find yourself worrying often?",
                    "mood": "How has your mood been lately?",
                    "productivity": "How productive have you been feeling?",
                    "time_management": "How well are you managing your time?",
                    "social_support": "Do you have people you can talk to?",
                    "lifestyle": "How is your daily routine?",
                    "digital_behaviour": "How is your screen time?",
                    "burnout_symptoms": "Have you been feeling overwhelmed?",
                    "recent_life_events": "Have there been any major changes recently?",
                    "exercise": "Are you getting any physical activity?",
                }
                reply = questions.get(missing[0], "Tell me more about how you've been feeling.")
            else:
                reply = "I think I have enough information now."

        return jsonify({
            "complete": False,
            "reply": reply,
            "session_id": session.session_id,
            "missing_categories": state.get("missing", []),
        })

    session.interview_status = "Completed"
    collected = state.get("data", {})
    facts = _build_complete_facts(collected)

    report = BurnoutEngine.generate_report(facts)

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

    return jsonify({
        "complete": True,
        "message": "Interview complete",
        "assessment_id": assessment.assessment_id,
        "report": {
            "burnout_score": report["burnout_score"],
            "wellness_score": report["wellness_score"],
            "risk_level": report["risk_level"],
            "primary_contributors": report.get("primary_contributors", []),
            "recovery_focus_areas": report.get("recovery_focus_areas", []),
            "category_summaries": report.get("category_summaries", {}),
        },
    })
