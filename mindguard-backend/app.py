from flask import Flask
from flask_cors import CORS

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

app = Flask(__name__)
app.config.from_object(Config)

CORS(app)

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


@app.route("/")
def home():
    return {
        "status": "running",
        "project": "MindGuard AI"
    }


with app.app_context():
    db.create_all()

if __name__ == "__main__":
    app.run(debug=True)
