from flask import Blueprint, request, jsonify
from database.db import db
from models.planner import PlannerTask

planner_bp = Blueprint("planner", __name__)


@planner_bp.route("/planner", methods=["GET"])
def get_tasks():

    tasks = PlannerTask.query.all()

    output = []

    for t in tasks:

        output.append({

            "task_id": t.task_id,

            "title": t.title,

            "description": t.description,

            "category": t.category,

            "due_date": t.due_date,

            "completed": t.completed

        })

    return jsonify(output)


@planner_bp.route("/planner", methods=["POST"])
def add_task():

    data = request.get_json()

    task = PlannerTask(

        user_id=1,

        title=data["title"],

        description=data.get("description"),

        category=data.get("category"),

        due_date=data.get("due_date")

    )

    db.session.add(task)

    db.session.commit()

    return jsonify({"message":"Task Added"})


@planner_bp.route("/planner/<int:id>", methods=["DELETE"])
def delete_task(id):

    task = PlannerTask.query.get(id)

    if task is None:

        return jsonify({"error":"Task not found"}),404

    db.session.delete(task)

    db.session.commit()

    return jsonify({"message":"Task Deleted"})
@planner_bp.route("/planner/<int:id>", methods=["PUT"])
def update_task(id):

    task = PlannerTask.query.get(id)

    if task is None:
        return jsonify({"error":"Task not found"}),404

    data = request.get_json()

    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.category = data.get("category", task.category)
    task.due_date = data.get("due_date", task.due_date)

    db.session.commit()

    return jsonify({
        "message":"Task Updated"
    })


@planner_bp.route("/planner/<int:id>/complete", methods=["PUT"])
def complete_task(id):

    task = PlannerTask.query.get(id)

    if task is None:
        return jsonify({"error":"Task not found"}),404

    task.completed = True

    db.session.commit()

    return jsonify({
        "message":"Task Completed"
    })