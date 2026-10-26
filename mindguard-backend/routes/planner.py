from flask import Blueprint, jsonify, request
from datetime import datetime
from database.db import db
from models.planner import PlannerTask
from models.recovery_goal import RecoveryGoal
from utils.auth import jwt_required

planner_bp = Blueprint("planner", __name__)

PRIORITIES = {"Low", "Medium", "High"}


def _serialize(task):
    return {
        "task_id": task.task_id,
        "title": task.title,
        "description": task.description or "",
        "category": task.category or "General",
        "priority": task.priority or "Medium",
        "due_date": task.due_date or "",
        "due_time": task.due_time or "",
        "completed": bool(task.completed),
        "task_source": task.task_source or "USER",
        "goal_id": task.goal_id,
        "created_at": str(task.created_at) if task.created_at else None,
        "completion_date": str(task.completion_date) if task.completion_date else None,
    }


@planner_bp.route("/planner")
@jwt_required
def get_tasks():
    user_id = request.current_user_id
    tasks = PlannerTask.query.filter_by(user_id=user_id).order_by(
        PlannerTask.created_at.desc()
    ).all()

    return jsonify([_serialize(t) for t in tasks])


@planner_bp.route("/planner", methods=["POST"])
@jwt_required
def add_task():
    user_id = request.current_user_id
    data = request.get_json(silent=True) or {}

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Title is required"}), 400
    if len(title) > 200:
        return jsonify({"error": "Title must be 200 characters or fewer"}), 400

    priority = data.get("priority", "Medium")
    if priority not in PRIORITIES:
        return jsonify({"error": "Priority must be Low, Medium or High"}), 400

    goal_id = data.get("goal_id")
    if goal_id is not None:
        goal = RecoveryGoal.query.filter_by(
            goal_id=goal_id, user_id=user_id
        ).first()
        if not goal:
            return jsonify({"error": "Recovery goal not found"}), 404
        goal_id = goal.goal_id

    task = PlannerTask(
        user_id=user_id,
        title=title,
        description=(data.get("description") or "")[:500],
        category=(data.get("category") or "General")[:50],
        priority=priority,
        due_date=data.get("due_date") or None,
        due_time=data.get("due_time") or None,
        completed=False,
        task_source="USER",
        goal_id=goal_id,
    )
    db.session.add(task)
    db.session.commit()

    return jsonify({
        "message": "Task added",
        "task": _serialize(task),
    }), 201


@planner_bp.route("/planner/<int:task_id>", methods=["PUT"])
@jwt_required
def update_task(task_id):
    user_id = request.current_user_id
    task = PlannerTask.query.filter_by(
        task_id=task_id, user_id=user_id
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json(silent=True) or {}

    if "title" in data:
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify({"error": "Title cannot be empty"}), 400
        task.title = title[:200]

    if "description" in data:
        task.description = (data.get("description") or "")[:500]

    if "category" in data:
        task.category = (data.get("category") or "General")[:50]

    if "priority" in data:
        if data["priority"] not in PRIORITIES:
            return jsonify({"error": "Priority must be Low, Medium or High"}), 400
        task.priority = data["priority"]

    if "due_date" in data:
        task.due_date = data.get("due_date") or None

    if "due_time" in data:
        task.due_time = data.get("due_time") or None

    if "completed" in data:
        task.completed = bool(data["completed"])
        task.completion_date = datetime.utcnow() if task.completed else None

        if task.goal_id:
            goal = RecoveryGoal.query.filter_by(
                goal_id=task.goal_id, user_id=user_id
            ).first()
            if goal:
                goal.completed = task.completed

    db.session.commit()
    return jsonify({"message": "Task updated", "task": _serialize(task)})


@planner_bp.route("/planner/<int:task_id>", methods=["DELETE"])
@jwt_required
def delete_task(task_id):
    user_id = request.current_user_id
    task = PlannerTask.query.filter_by(
        task_id=task_id, user_id=user_id
    ).first()

    if not task:
        return jsonify({"error": "Task not found"}), 404

    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"})
