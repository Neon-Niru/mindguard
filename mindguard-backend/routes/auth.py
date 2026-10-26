import secrets
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, current_app
from database.db import db
from models.user import User
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.planner import PlannerTask
from models.settings import UserSettings
from utils.extensions import bcrypt
from utils.auth import generate_token, jwt_required

auth_bp = Blueprint("auth", __name__)


def _user_payload(user):
    return {
        "user_id": user.user_id,
        "full_name": user.full_name,
        "email": user.email,
    }


def _valid_password(password):
    return isinstance(password, str) and len(password) >= 6


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    name = (data.get("full_name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "full_name, email, and password are required"}), 400

    if "@" not in email or "." not in email.split("@")[-1]:
        return jsonify({"error": "Please provide a valid email address"}), 400

    if not _valid_password(password):
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
        "user": _user_payload(user),
    }), 201


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = (data.get("email") or "").strip().lower()
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
        "user": _user_payload(user),
    })


@auth_bp.route("/me")
@jwt_required
def get_me():
    user = db.session.get(User, request.current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify({
        **_user_payload(user),
        "account_created": str(user.account_created) if user.account_created else None,
        "last_login": str(user.last_login) if user.last_login else None,
    })


@auth_bp.route("/me", methods=["PUT"])
@jwt_required
def update_me():
    user = db.session.get(User, request.current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json(silent=True) or {}

    if "full_name" in data:
        name = (data.get("full_name") or "").strip()
        if not name:
            return jsonify({"error": "full_name cannot be empty"}), 400
        user.full_name = name

    if "email" in data:
        email = (data.get("email") or "").strip().lower()
        if not email or "@" not in email or "." not in email.split("@")[-1]:
            return jsonify({"error": "Please provide a valid email address"}), 400

        existing = User.query.filter(
            User.email == email,
            User.user_id != user.user_id,
        ).first()
        if existing:
            return jsonify({"error": "Email already registered"}), 409

        user.email = email

    db.session.commit()

    return jsonify({
        "message": "Profile updated",
        "user": _user_payload(user),
    })


@auth_bp.route("/change-password", methods=["POST"])
@jwt_required
def change_password():
    data = request.get_json(silent=True) or {}
    current_password = data.get("current_password", "")
    new_password = data.get("new_password", "")

    if not current_password or not new_password:
        return jsonify({
            "error": "current_password and new_password are required"
        }), 400

    if not _valid_password(new_password):
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    user = db.session.get(User, request.current_user_id)
    if not user or not bcrypt.check_password_hash(user.password_hash, current_password):
        return jsonify({"error": "Current password is incorrect"}), 401

    user.password_hash = bcrypt.generate_password_hash(new_password).decode("utf-8")
    user.reset_token = None
    user.reset_token_expires_at = None
    db.session.commit()

    return jsonify({"message": "Password updated successfully."})


@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    email = (data.get("email") or "").strip().lower()
    user = User.query.filter_by(email=email).first()

    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(hours=1)

    if user:
        user.reset_token = token
        user.reset_token_expires_at = expires_at
        db.session.commit()

    response = {
        "message": "If an account exists for that email, a reset link has been sent."
    }

    # No SMTP provider is configured for the demo deployment. When explicitly
    # enabled, return the token so the UI can complete the reset flow.
    if current_app.config.get("RETURN_RESET_TOKEN"):
        response["reset_token"] = token

    return jsonify(response)


@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Invalid request"}), 400

    token = (data.get("token") or "").strip()
    new_password = data.get("password", "")

    if not token or not new_password:
        return jsonify({"error": "Token and password are required"}), 400

    if not _valid_password(new_password):
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


@auth_bp.route("/me/export")
@jwt_required
def export_data():
    user = db.session.get(User, request.current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    assessments = BurnoutAssessment.query.filter_by(
        user_id=user.user_id
    ).order_by(BurnoutAssessment.assessment_date).all()

    goals = RecoveryGoal.query.filter_by(user_id=user.user_id).all()
    tasks = PlannerTask.query.filter_by(user_id=user.user_id).all()
    sessions = InterviewSession.query.filter_by(user_id=user.user_id).all()

    return jsonify({
        "user": {
            **_user_payload(user),
            "account_created": str(user.account_created) if user.account_created else None,
        },
        "assessments": [
            {
                "assessment_id": a.assessment_id,
                "date": str(a.assessment_date),
                "burnout_score": a.burnout_score,
                "wellness_score": a.wellness_score,
                "risk_level": a.risk_level,
                "engine_version": a.engine_version,
            }
            for a in assessments
        ],
        "recovery_goals": [
            {
                "goal": g.goal,
                "completed": g.completed,
                "created_at": str(g.created_at) if g.created_at else None,
            }
            for g in goals
        ],
        "planner_tasks": [
            {
                "title": t.title,
                "category": t.category,
                "priority": t.priority,
                "completed": t.completed,
            }
            for t in tasks
        ],
        "interview_sessions": [
            {
                "session_id": s.session_id,
                "interview_date": str(s.interview_date) if s.interview_date else None,
                "status": s.interview_status,
            }
            for s in sessions
        ],
    })


@auth_bp.route("/me", methods=["DELETE"])
@jwt_required
def delete_me():
    data = request.get_json(silent=True) or {}
    password = data.get("password", "")

    if not password:
        return jsonify({"error": "Password is required"}), 400

    user = db.session.get(User, request.current_user_id)
    if not user or not bcrypt.check_password_hash(user.password_hash, password):
        return jsonify({"error": "Password is incorrect"}), 401

    user_id = user.user_id

    PlannerTask.query.filter_by(user_id=user_id).delete()
    RecoveryGoal.query.filter_by(user_id=user_id).delete()
    BurnoutAssessment.query.filter_by(user_id=user_id).delete()
    InterviewSession.query.filter_by(user_id=user_id).delete()
    UserSettings.query.filter_by(user_id=user_id).delete()

    db.session.delete(user)
    db.session.commit()

    return jsonify({"message": "Account deleted"})
