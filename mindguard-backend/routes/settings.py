from flask import Blueprint, jsonify, request
from database.db import db
from models.settings import UserSettings
from utils.auth import jwt_required

settings_bp = Blueprint("settings", __name__)

THEMES = {"dark", "light"}
TONES = {"supportive", "direct", "reflective"}


def _serialize(settings):
    if settings is None:
        return {
            "theme": "dark",
            "notifications": True,
            "notification_checkins": True,
            "notification_planner": True,
            "notification_weekly": False,
            "ai_tone": "supportive",
            "privacy_settings": "private",
        }

    return {
        "theme": settings.theme or "dark",
        "notifications": bool(settings.notification_preference),
        "notification_checkins": bool(settings.notification_checkins),
        "notification_planner": bool(settings.notification_planner),
        "notification_weekly": bool(settings.notification_weekly),
        "ai_tone": settings.ai_tone or "supportive",
        "privacy_settings": settings.privacy_settings or "private",
    }


@settings_bp.route("/settings")
@jwt_required
def get_settings():
    user_id = request.current_user_id
    settings = UserSettings.query.filter_by(user_id=user_id).first()
    return jsonify(_serialize(settings))


@settings_bp.route("/settings", methods=["POST"])
@jwt_required
def save_settings():
    user_id = request.current_user_id
    data = request.get_json(silent=True) or {}

    theme = data.get("theme")
    if theme is not None and theme not in THEMES:
        return jsonify({"error": "theme must be 'dark' or 'light'"}), 400

    tone = data.get("ai_tone")
    if tone is not None and tone not in TONES:
        return jsonify({"error": "ai_tone must be supportive, direct or reflective"}), 400

    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if settings is None:
        settings = UserSettings(user_id=user_id)
        db.session.add(settings)

    if theme is not None:
        settings.theme = theme

    if "notification_checkins" in data:
        settings.notification_checkins = bool(data["notification_checkins"])
    elif "notifications" in data:
        settings.notification_checkins = bool(data["notifications"])

    if "notification_planner" in data:
        settings.notification_planner = bool(data["notification_planner"])
    elif "notifications" in data:
        settings.notification_planner = bool(data["notifications"])

    if "notification_weekly" in data:
        settings.notification_weekly = bool(data["notification_weekly"])

    if "notifications" in data:
        settings.notification_preference = bool(data["notifications"])

    if tone is not None:
        settings.ai_tone = tone

    if "privacy_settings" in data:
        settings.privacy_settings = str(data["privacy_settings"])[:100]

    db.session.commit()

    return jsonify({
        "message": "Settings saved",
        "settings": _serialize(settings),
    })
