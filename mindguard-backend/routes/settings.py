from flask import Blueprint, jsonify, request
from database.db import db
from models.settings import UserSettings

settings_bp = Blueprint("settings", __name__)

@settings_bp.route("/settings/<int:user_id>")
def get_settings(user_id):

    settings = UserSettings.query.filter_by(user_id=user_id).first()

    if settings is None:
        return jsonify({})

    return jsonify({
    "theme": settings.theme,
    "notifications": settings.notification_preference,
    "privacy_settings": settings.privacy_settings
    })


@settings_bp.route("/settings", methods=["POST"])
def save_settings():

    data = request.get_json()

    settings = UserSettings.query.filter_by(
        user_id=data["user_id"]
    ).first()

    if settings is None:

        settings = UserSettings(
            user_id=data["user_id"],
            theme=data["theme"],
            notification_preference=data["notifications"],
            privacy_settings=data.get("privacy_settings", "private")
        )

        db.session.add(settings)

    else:

        settings.theme = data["theme"]
        settings.notification_preference = data["notifications"]
        settings.privacy_settings = data.get("privacy_settings", settings.privacy_settings)

    db.session.commit()

    return jsonify({
        "message": "Saved"
    })