from flask import Blueprint, request, jsonify
from database.db import db
from models.user import User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

auth_bp = Blueprint("auth", __name__)

# -------------------------
# Register
# -------------------------

@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    full_name = data.get("full_name")
    email = data.get("email")
    password = data.get("password")

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    hashed = bcrypt.generate_password_hash(password).decode("utf-8")

    user = User(
        full_name=full_name,
        email=email,
        password_hash=hashed
    )

    db.session.add(user)
    db.session.commit()

    return jsonify({"message": "User created"})


# -------------------------
# Login
# -------------------------

@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    user = User.query.filter_by(email=email).first()

    if user is None:
        return jsonify({"error":"Invalid email or password"}),401

    if not bcrypt.check_password_hash(user.password_hash,password):
        return jsonify({"error":"Invalid email or password"}),401

    return jsonify({
        "message":"Login Successful",
        "user_id":user.user_id,
        "full_name":user.full_name,
        "email":user.email
    })


# -------------------------
# Logout
# -------------------------

@auth_bp.route("/logout", methods=["POST"])
def logout():

    return jsonify({
        "message":"Logged out successfully"
    })