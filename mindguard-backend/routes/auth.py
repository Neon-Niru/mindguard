from flask import Blueprint, jsonify, request
from datetime import datetime
from database.db import db
from models.user import User
from utils.extensions import bcrypt
from utils.auth import generate_token, jwt_required, decode_token

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    name = data.get("full_name", "").strip()
    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "full_name, email, and password are required"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    existing = User.query.filter_by(email=email).first()
    if existing:
        return jsonify({"error": "Email already registered"}), 409

    password_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(
        full_name=name,
        email=email,
        password_hash=password_hash
    )
    db.session.add(user)
    db.session.commit()

    token = generate_token(user.user_id)

    return jsonify({
        "message": "Account created",
        "token": token,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email
        }
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email", "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid email or password"}), 401

    user.last_login = datetime.utcnow()
    db.session.commit()

    token = generate_token(user.user_id)

    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "user_id": user.user_id,
            "full_name": user.full_name,
            "email": user.email
        }
    })


@auth_bp.route("/me")
@jwt_required
def get_me():
    user = User.query.get(request.current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
        "account_created": str(user.account_created) if user.account_created else None
    })


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = data.get("email", "").strip().lower()
    user = User.query.filter_by(email=email).first()

    if user:
        import secrets
        from datetime import timedelta
        token = secrets.token_urlsafe(32)
        user.reset_token = token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        db.session.commit()

    return jsonify({"message": "If an account exists for that email, a reset link has been sent."})


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    token = data.get("token", "")
    new_password = data.get("password", "")

    if not token or not new_password:
        return jsonify({"error": "Token and password are required"}), 400

    if len(new_password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"error": "Invalid or expired token"}), 400

    if user.reset_token_expires_at and user.reset_token_expires_at < datetime.utcnow():
        return jsonify({"error": "Token has expired"}), 400

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.reset_token = None
    user.reset_token_expires_at = None
    db.session.commit()

    return jsonify({"message": "Password has been reset successfully."})
