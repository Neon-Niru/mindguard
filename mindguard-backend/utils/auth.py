import os
from datetime import datetime, timedelta
from functools import wraps

import jwt as pyjwt
from flask import current_app, jsonify, request


def _secret():
    return (
        current_app.config.get("SECRET_KEY")
        or os.getenv("SECRET_KEY", "mindguard-dev-secret-change-me")
    )


def generate_token(user_id):
    days = int(current_app.config.get("JWT_EXPIRES_DAYS", 30))
    now = datetime.utcnow()
    payload = {
        "user_id": user_id,
        "exp": now + timedelta(days=days),
        "iat": now,
    }
    return pyjwt.encode(payload, _secret(), algorithm="HS256")


def decode_token(token):
    return pyjwt.decode(token, _secret(), algorithms=["HS256"])


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ", 1)[1].strip()

        if not token:
            return jsonify({"error": "Authorization required"}), 401

        try:
            data = decode_token(token)
            user_id = data.get("user_id")
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Session expired. Please log in again."}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        if not user_id:
            return jsonify({"error": "Invalid token"}), 401

        # Imported lazily to avoid a circular import at module load time.
        from database.db import db
        from models.user import User

        if db.session.get(User, user_id) is None:
            return jsonify({"error": "Account no longer exists"}), 401

        request.current_user_id = user_id
        return f(*args, **kwargs)

    return decorated
