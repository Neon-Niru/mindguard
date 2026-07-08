from flask import Blueprint, jsonify, request
from datetime import datetime
from database.db import db
from models.planner import PlannerTask
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

planner_bp = Blueprint("planner", __name__)


@planner_bp.route("/planner")
@jwt_required
def get_tasks():
    user_id = request.current_user_id
    tasks = PlannerTask.query.filter_by(user_id=user_id).order_by(
        PlannerTask.created_at.desc()
    ).all()

    return jsonify([
        {
            "task_id": t.task_id,
            "title": t.title,
            "description": t.description or "",
            "category": t.category or "General",
            "priority": t.priority or "Medium",
            "due_date": t.due_date or "",
            "due_time": t.due_time or "",
            "completed": t.completed or False,
            "task_source": t.task_source or "USER",
            "goal_id": t.goal_id,
            "created_at": str(t.created_at) if t.created_at else None
        }
        for t in tasks
    ])


@planner_bp.route("/planner", methods=["POST"])
@jwt_required
def add_task():
    user_id = request.current_user_id
    data = request.get_json()
    if not data or not data.get("title"):
        return jsonify({"error": "Title is required"}), 400

    task = PlannerTask(
        user_id=user_id,
        title=data["title"],
        description=data.get("description", ""),
        category=data.get("category", "General"),
        priority=data.get("priority", "Medium"),
        due_date=data.get("due_date"),
        due_time=data.get("due_time"),
        completed=False,
        task_source=data.get("task_source", "USER"),
        goal_id=data.get("goal_id")
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task added",
        "task_id": task.task_id
    }), 201


@planner_bp.route("/planner/<int:task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    user_id = request.current_user_id
    task = PlannerTask.query.filter_by(task_id=task_id, user_id=user_id).first_or_404()
    data = request.get_json()

    if "title" in data:
        task.title = data["title"]
    if "description" in data:
        task.description = data["description"]
    if "category" in data:
        task.category = data["category"]
    if "priority" in data:
        task.priority = data["priority"]
    if "due_date" in data:
        task.due_date = data["due_date"]
    if "due_time" in data:
        task.due_time = data["due_time"]
    if "completed" in data:
        task.completed = data["completed"]
        if data["completed"]:
            task.completion_date = datetime.utcnow()
            if task.goal_id:
                goal = RecoveryGoal.query.get(task.goal_id)
                if goal:
                    goal.completed = True

    db.session.commit()
    return jsonify({"message": "Task updated"})


@planner_bp.route("/planner/<int:task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id):
    user_id = request.current_user_id
    task = PlannerTask.query.filter_by(task_id=task_id, user_id=user_id).first_or_404()
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})
