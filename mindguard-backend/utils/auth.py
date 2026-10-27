import os
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
import jwt as pyjwt


def generate_token(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(days=30),
        "iat": datetime.utcnow()
    }
    secret = current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY", "mindguard-secret-key")
    return pyjwt.encode(payload, secret, algorithm="HS256")


def decode_token(token):
    secret = current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY", "mindguard-secret-key")
    return pyjwt.decode(token, secret, algorithms=["HS256"])


def jwt_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        if not token:
            return jsonify({"error": "Authorization required"}), 401
        try:
            data = decode_token(token)
            request.current_user_id = data["user_id"]
        except pyjwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except pyjwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)
    return decorated
