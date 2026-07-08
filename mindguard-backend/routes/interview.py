from flask import Blueprint, request, jsonify

from database.db import db

from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal

from engine.burnout_engine import BurnoutEngine

from ai_engine.conversation_manager import process_message


interview_bp = Blueprint(
    "interview",
    __name__
)


@interview_bp.route("/interview", methods=["POST"])
def interview():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "Invalid request"
        }), 400


    user_id = data.get("user_id")
    conversation = data.get("conversation")


    if not user_id or not conversation:
        return jsonify({
            "error": "Missing user_id or conversation"
        }), 400



    session = InterviewSession(

        user_id=user_id,

        conversation_history=conversation

    )


    db.session.add(session)

    db.session.commit()



    ai_result = process_message(
        conversation
    )



    if not ai_result["complete"]:


        session.collected_facts = ai_result.get(
            "state",
            {}
        ).get(
            "data",
            {}
        )


        db.session.commit()


        return jsonify({

            "message":
                "Interview continues",

            "reply":
                ai_result.get("reply"),

            "missing_categories":
                ai_result.get("state", {}).get(
                    "missing",
                    []
                ),

            "session_id":
                session.session_id

        })





    facts = ai_result["data"]



    session.collected_facts = facts

    session.interview_status = "Completed"

    db.session.commit()





    report = BurnoutEngine.generate_report(

        facts

    )





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

        emotional_exhaustion_score=report.get(
            "emotional_exhaustion_score"
        ),

        cognitive_score=report.get(
            "cognitive_score"
        ),

        lifestyle_score=report.get(
            "lifestyle_score"
        ),

        mental_energy_score=report.get(
            "mental_energy_score"
        ),

        mood_score=report.get(
            "mood_score"
        ),

        productivity_score=report.get(
            "productivity_score"
        ),


        primary_contributors=
            report["primary_contributors"],


        recovery_focus_areas=
            report["recovery_focus_areas"],


        category_summaries=
            report["category_summaries"]

    )



    db.session.add(
        assessment
    )

    db.session.commit()





    for goal_text in report.get(
        "recovery_focus_areas",
        []
    ):


        goal = RecoveryGoal(

            assessment_id=
                assessment.assessment_id,

            user_id=user_id,

            goal=goal_text

        )


        db.session.add(goal)



    db.session.commit()





    return jsonify({

        "message":
            "Interview Complete",

        "assessment_id":
            assessment.assessment_id,

        "report":
            report

    })