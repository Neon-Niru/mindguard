from flask import Blueprint, jsonify, request
from database.db import db
from models.planner import PlannerTask

planner_bp = Blueprint("planner", __name__)

# ---------------- GET ALL TASKS ----------------

@planner_bp.route("/planner/<int:user_id>")
def planner(user_id):

    tasks = PlannerTask.query.filter_by(user_id=user_id).all()

    return jsonify([
        {
            "task_id": t.task_id,
            "title": t.title,
            "completed": t.completed
        }
        for t in tasks
    ])


# ---------------- ADD TASK ----------------

@planner_bp.route("/planner", methods=["POST"])
def add_task():

    data = request.get_json()

    task = PlannerTask(
        user_id=data["user_id"],
        title=data["title"],
        completed=False
    )

    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task Added"
    })


# ---------------- COMPLETE TASK ----------------

@planner_bp.route("/planner/<int:id>", methods=["PUT"])
def complete_task(id):

    task = PlannerTask.query.get_or_404(id)

    task.completed = True

    db.session.commit()

    return jsonify({
        "message": "Completed"
    })