from database.db import db
from datetime import datetime


class UserSettings(db.Model):

    __tablename__ = "user_settings"


    setting_id = db.Column(
        db.Integer,
        primary_key=True
    )


    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.user_id"),
        nullable=False,
        unique=True
    )


    theme = db.Column(
        db.String(30),
        default="dark"
    )


    notification_preference = db.Column(
        db.Boolean,
        default=True
    )


    notification_checkins = db.Column(
        db.Boolean,
        default=True
    )


    notification_planner = db.Column(
        db.Boolean,
        default=True
    )


    notification_weekly = db.Column(
        db.Boolean,
        default=False
    )


    ai_tone = db.Column(
        db.String(30),
        default="supportive"
    )


    privacy_settings = db.Column(
        db.String(100),
        default="private"
    )


    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )
