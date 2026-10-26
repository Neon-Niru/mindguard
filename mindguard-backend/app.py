import os

from flask import Flask, jsonify, request
from flask_cors import CORS
from sqlalchemy import inspect, text

from config import Config
from database.db import db
from utils.extensions import bcrypt

from models.user import User
from models.planner import PlannerTask
from models.interview import InterviewSession
from models.assessment import BurnoutAssessment
from models.recovery_goal import RecoveryGoal
from models.settings import UserSettings

from routes.auth import auth_bp
from routes.report import report_bp
from routes.dashboard import dashboard_bp
from routes.planner import planner_bp
from routes.progress import progress_bp
from routes.settings import settings_bp
from routes.interview import interview_bp
from routes.assessment import assessment_bp


# Columns added after the first release. `db.create_all()` never alters an
# existing table, so new deployments with an old database need these added
# manually. Each entry keeps the SQL portable across SQLite and PostgreSQL.
SCHEMA_UPGRADES = {
    "user_settings": {
        "notification_checkins": "BOOLEAN DEFAULT 1",
        "notification_planner": "BOOLEAN DEFAULT 1",
        "notification_weekly": "BOOLEAN DEFAULT 0",
        "ai_tone": "VARCHAR(30) DEFAULT 'supportive'",
    },
    "burnout_assessments": {
        "engine_version": "VARCHAR(20)",
    },
}


def _apply_schema_upgrades():
    """Best-effort additive migration for databases created by older builds."""
    inspector = inspect(db.engine)

    for table_name, columns in SCHEMA_UPGRADES.items():
        if not inspector.has_table(table_name):
            continue

        existing = {column["name"] for column in inspector.get_columns(table_name)}

        for column_name, definition in columns.items():
            if column_name in existing:
                continue

            with db.engine.begin() as connection:
                connection.execute(text(
                    f"ALTER TABLE {table_name} "
                    f"ADD COLUMN {column_name} {definition}"
                ))


def _register_error_handlers(app):

    def wants_json():
        return (
            request.path.startswith("/api")
            or request.accept_mimetypes.best == "application/json"
        )

    @app.errorhandler(400)
    def bad_request(error):
        if wants_json():
            return jsonify({"error": "Bad request"}), 400
        return error

    @app.errorhandler(401)
    def unauthorized(error):
        if wants_json():
            return jsonify({"error": "Authorization required"}), 401
        return error

    @app.errorhandler(403)
    def forbidden(error):
        if wants_json():
            return jsonify({"error": "Forbidden"}), 403
        return error

    @app.errorhandler(404)
    def not_found(error):
        if wants_json():
            return jsonify({"error": "Not found"}), 404
        return error

    @app.errorhandler(405)
    def method_not_allowed(error):
        if wants_json():
            return jsonify({"error": "Method not allowed"}), 405
        return error

    @app.errorhandler(413)
    def payload_too_large(error):
        if wants_json():
            return jsonify({"error": "Request body is too large"}), 413
        return error

    @app.errorhandler(500)
    def server_error(error):
        db.session.rollback()
        if wants_json():
            return jsonify({"error": "Something went wrong on our side"}), 500
        return error


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    CORS(
        app,
        resources={r"/api/*": {"origins": app.config.get("CORS_ORIGINS", "*")}},
        supports_credentials=False,
    )

    db.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(report_bp, url_prefix="/api")
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(planner_bp, url_prefix="/api")
    app.register_blueprint(progress_bp, url_prefix="/api")
    app.register_blueprint(settings_bp, url_prefix="/api")
    app.register_blueprint(interview_bp, url_prefix="/api")
    app.register_blueprint(assessment_bp, url_prefix="/api")

    _register_error_handlers(app)

    @app.route("/api/health")
    def health():
        return jsonify({
            "status": "ok",
            "service": "mindguard-api",
        })

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "DENY")
        response.headers.setdefault("Referrer-Policy", "no-referrer")
        return response

    with app.app_context():
        db.create_all()
        _apply_schema_upgrades()

    return app


def main():
    app = create_app()
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", "5000")),
        debug=os.getenv("FLASK_DEBUG", "false").lower() in ("1", "true"),
    )


# Waitress/Render entry point: `waitress-serve app:app`
# Set MINDGUARD_DEFER_APP=1 in tests to import `create_app` without creating
# the default application and database.
if os.getenv("MINDGUARD_DEFER_APP") != "1":
    app = create_app()


if __name__ == "__main__":
    main()
