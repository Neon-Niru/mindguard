from flask import Blueprint, jsonify, request
from database.db import db
from models.settings import UserSettings
from utils.auth import jwt_required

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings")
@jwt_required
def get_settings():
    user_id = request.current_user_id
    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if settings is None:
        return jsonify({
            "theme": "dark",
            "notifications": True,
            "privacy_settings": "private"
        })

    return jsonify({
        "theme": settings.theme,
        "notifications": settings.notification_preference,
        "privacy_settings": settings.privacy_settings
    })


@settings_bp.route("/settings", methods=["POST"])
@jwt_required
def save_settings():
    user_id = request.current_user_id
    data = request.get_json()

    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if settings is None:
        settings = UserSettings(
            user_id=user_id,
            theme=data.get("theme", "dark"),
            notification_preference=data.get("notifications", True),
            privacy_settings=data.get("privacy_settings", "private")
        )
        db.session.add(settings)
    else:
        settings.theme = data.get("theme", settings.theme)
        settings.notification_preference = data.get("notifications", settings.notification_preference)
        settings.privacy_settings = data.get("privacy_settings", settings.privacy_settings)

    db.session.commit()

    return jsonify({"message": "Settings saved"})
