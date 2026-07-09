from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Complaint, ComplaintUpdate
from datetime import datetime
from auth.routes import admin_required

complaints_bp = Blueprint("complaints", __name__)


# GET /api/complaints  list all (admin) or own (resident)
@complaints_bp.route("/", methods=["GET"])
@jwt_required()
def get_complaints():
    user_id = int(get_jwt_identity())
    from models import User
    user = User.query.get(user_id)

    if user.role in ["ADMIN", "TREASURER", "COMMITTEE_MEMBER"]:
        complaints = Complaint.query.order_by(Complaint.created_at.desc()).all()
    else:
        complaints = Complaint.query.filter_by(raised_by=user_id)\
                        .order_by(Complaint.created_at.desc()).all()

    return jsonify([_complaint_dict(c) for c in complaints]), 200


# POST /api/complaints raise new complaint
@complaints_bp.route("/", methods=["POST"])
@jwt_required()
def raise_complaint():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["title", "category", "apartment_id"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    complaint = Complaint(
        raised_by=user_id,
        apartment_id=data["apartment_id"],
        title=data["title"],
        description=data.get("description"),
        category=data["category"],
        priority=data.get("priority", "MEDIUM")
    )
    db.session.add(complaint)
    db.session.commit()
    return jsonify(_complaint_dict(complaint)), 201


# GET /api/complaints/<id>  single complaint detail
@complaints_bp.route("/<int:cid>", methods=["GET"])
@jwt_required()
def get_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    result = _complaint_dict(c)
    result["updates"] = [_update_dict(u) for u in c.updates]
    return jsonify(result), 200


# PUT /api/complaints/<id>/assign  assign worker
@complaints_bp.route("/<int:cid>/assign", methods=["PUT"])
@admin_required
def assign_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    data = request.get_json()

    c.assigned_worker_id = data.get("worker_id")
    c.status = "ASSIGNED"

    update = ComplaintUpdate(
        complaint_id=c.id,
        updated_by=int(get_jwt_identity()),
        status="ASSIGNED",
        remarks=data.get("remarks", "Complaint assigned to worker")
    )
    db.session.add(update)
    db.session.commit()
    return jsonify(_complaint_dict(c)), 200


# PUT /api/complaints/<id>/status update status
@complaints_bp.route("/<int:cid>/status", methods=["PUT"])
@admin_required
def update_status(cid):
    c = Complaint.query.get_or_404(cid)
    data = request.get_json()

    valid = ["OPEN", "ASSIGNED", "IN_PROGRESS", "COMPLETED", "CLOSED"]
    if data.get("status") not in valid:
        return jsonify({"error": f"Invalid status. Choose from {valid}"}), 400

    c.status = data["status"]
    if data["status"] in ["COMPLETED", "CLOSED"]:
        c.resolved_at = datetime.utcnow()

    update = ComplaintUpdate(
        complaint_id=c.id,
        updated_by=int(get_jwt_identity()),
        status=data["status"],
        remarks=data.get("remarks")
    )
    db.session.add(update)
    db.session.commit()
    return jsonify(_complaint_dict(c)), 200


# DELETE /api/complaints/<id> delete complaint
@complaints_bp.route("/<int:cid>", methods=["DELETE"])
@admin_required
def delete_complaint(cid):
    c = Complaint.query.get_or_404(cid)
    db.session.delete(c)
    db.session.commit()
    return jsonify({"message": "Complaint deleted"}), 200


# helpers 
def _complaint_dict(c):
    return {
        "id": c.id,
        "title": c.title,
        "description": c.description,
        "category": c.category,
        "priority": c.priority,
        "status": c.status,
        "apartment_id": c.apartment_id,
        "flat_number": c.apartment.flat_number if c.apartment else None,
        "raised_by": c.raised_by,
        "raised_by_name": c.raiser.name if c.raiser else None,
        "assigned_worker_id": c.assigned_worker_id,
        "assigned_worker_name": c.worker.name if c.worker else None,
        "created_at": str(c.created_at),
        "resolved_at": str(c.resolved_at) if c.resolved_at else None
    }

def _update_dict(u):
    return {
        "id": u.id,
        "status": u.status,
        "remarks": u.remarks,
        "updated_by": u.updated_by,
        "updated_by_name": u.updated_by_user.name if u.updated_by_user else None,
        "updated_at": str(u.updated_at)
    }
