from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, MaintenanceTask
from datetime import datetime

maintenance_bp = Blueprint("maintenance", __name__)


# GET /api/maintenance  all tasks
@maintenance_bp.route("/", methods=["GET"])
@jwt_required()
def get_tasks():
    tasks = MaintenanceTask.query.order_by(MaintenanceTask.scheduled_date).all()
    return jsonify([_task_dict(t) for t in tasks]), 200


# POST /api/maintenance  add new task
@maintenance_bp.route("/", methods=["POST"])
@jwt_required()
def add_task():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["title", "category", "scheduled_date"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    task = MaintenanceTask(
        title=data["title"],
        description=data.get("description"),
        category=data["category"],
        scheduled_date=data["scheduled_date"],
        created_by=user_id,
        assigned_to=data.get("assigned_to")
    )
    db.session.add(task)
    db.session.commit()
    return jsonify(_task_dict(task)), 201


# PUT /api/maintenance/<id>/complete  mark task complete
@maintenance_bp.route("/<int:tid>/complete", methods=["PUT"])
@jwt_required()
def complete_task(tid):
    task = MaintenanceTask.query.get_or_404(tid)
    task.status = "COMPLETED"
    task.completed_at = datetime.utcnow()
    db.session.commit()
    return jsonify(_task_dict(task)), 200


# PUT /api/maintenance/<id>  update task
@maintenance_bp.route("/<int:tid>", methods=["PUT"])
@jwt_required()
def update_task(tid):
    task = MaintenanceTask.query.get_or_404(tid)
    data = request.get_json()
    task.title = data.get("title", task.title)
    task.description = data.get("description", task.description)
    task.scheduled_date = data.get("scheduled_date", task.scheduled_date)
    task.assigned_to = data.get("assigned_to", task.assigned_to)
    task.status = data.get("status", task.status)
    db.session.commit()
    return jsonify(_task_dict(task)), 200


# DELETE /api/maintenance/<id>  delete task
@maintenance_bp.route("/<int:tid>", methods=["DELETE"])
@jwt_required()
def delete_task(tid):
    task = MaintenanceTask.query.get_or_404(tid)
    db.session.delete(task)
    db.session.commit()
    return jsonify({"message": "Task deleted"}), 200


#  helper 
def _task_dict(t):
    return {
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "category": t.category,
        "scheduled_date": str(t.scheduled_date),
        "status": t.status,
        "created_by": t.created_by,
        "assigned_to": t.assigned_to,
        "assigned_to_name": t.assignee.name if t.assignee else None,
        "completed_at": str(t.completed_at) if t.completed_at else None
    }
