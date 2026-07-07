from flask import Blueprint, jsonify

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/dashboard", methods=["GET"])
def dashboard():

    return jsonify({

        "wellness_score": 82,

        "burnout_score": 18,

        "risk_level": "Low",

        "sleep_summary": "7.5 hours",

        "mood_summary": "Positive",

        "stress_summary": "Moderate",

        "productivity_summary": "Good",

        "planner_progress": 60,

        "recovery_goals": [

            "Sleep before 11 PM",

            "Take one study break every hour",

            "Walk for 20 minutes"

        ],

        "previous_checkin":{

            "burnout_score":24,

            "wellness_score":76

        }

    })