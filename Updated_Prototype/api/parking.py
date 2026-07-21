from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ParkingSlot
from datetime import datetime
from auth.routes import admin_required
parking_bp = Blueprint("parking", __name__)


# GET /api/parking  all slots with status
@parking_bp.route("/", methods=["GET"])
@jwt_required()
def get_slots():
    slots = ParkingSlot.query.order_by(ParkingSlot.slot_number).all()
    return jsonify([_slot_dict(s) for s in slots]), 200


# GET /api/parking/available  only available slots
@parking_bp.route("/available", methods=["GET"])
@jwt_required()
def get_available():
    slots = ParkingSlot.query.filter_by(status="AVAILABLE").all()
    return jsonify([_slot_dict(s) for s in slots]), 200


# POST /api/parking  add new parking slot (admin)
@parking_bp.route("/", methods=["POST"])
@admin_required
def add_slot():
    data = request.get_json()
    if not data.get("slot_number"):
        return jsonify({"error": "slot_number is required"}), 400

    if ParkingSlot.query.filter_by(slot_number=data["slot_number"]).first():
        return jsonify({"error": "Slot already exists"}), 409

    slot = ParkingSlot(slot_number=data["slot_number"])
    db.session.add(slot)
    db.session.commit()
    return jsonify(_slot_dict(slot)), 201


# PUT /api/parking/<id>/reserve  resident reserves slot for visitor
@parking_bp.route("/<int:sid>/reserve", methods=["PUT"])
@jwt_required()
def reserve_slot(sid):
    user_id = int(get_jwt_identity())
    slot = ParkingSlot.query.get_or_404(sid)

    if slot.status != "AVAILABLE":
        return jsonify({"error": f"Slot is already {slot.status}"}), 400

    data = request.get_json()
    from models import Resident
    resident = Resident.query.filter_by(user_id=user_id).first()

    slot.status = "RESERVED"
    slot.occupied_by_apartment_id = resident.apartment_id if resident else None
    slot.visitor_name = data.get("visitor_name")
    slot.visitor_vehicle_number = data.get("visitor_vehicle_number")
    slot.expected_arrival_time = data.get("expected_arrival_time")
    slot.occupied_since = datetime.utcnow()
    slot.updated_by = user_id

    db.session.commit()
    return jsonify({
        "message": f"Slot {slot.slot_number} reserved successfully",
        "slot": _slot_dict(slot)
    }), 200


# PUT /api/parking/<id>/occupy  guard marks visitor arrived
@parking_bp.route("/<int:sid>/occupy", methods=["PUT"])
@jwt_required()
def occupy_slot(sid):
    user_id = int(get_jwt_identity())
    slot = ParkingSlot.query.get_or_404(sid)
    data = request.get_json()

    slot.status = "OCCUPIED"
    slot.visitor_name = data.get("visitor_name", slot.visitor_name)
    slot.visitor_vehicle_number = data.get("visitor_vehicle_number", slot.visitor_vehicle_number)
    slot.occupied_since = datetime.utcnow()
    slot.updated_by = user_id

    db.session.commit()
    return jsonify({"message": f"Slot {slot.slot_number} marked occupied", "slot": _slot_dict(slot)}), 200


# PUT /api/parking/<id>/release  mark slot available again
@parking_bp.route("/<int:sid>/release", methods=["PUT"])
@jwt_required()
def release_slot(sid):
    user_id = int(get_jwt_identity())
    slot = ParkingSlot.query.get_or_404(sid)

    slot.status = "AVAILABLE"
    slot.occupied_by_apartment_id = None
    slot.visitor_name = None
    slot.visitor_vehicle_number = None
    slot.expected_arrival_time = None
    slot.occupied_since = None
    slot.updated_by = user_id

    db.session.commit()
    return jsonify({"message": f"Slot {slot.slot_number} released", "slot": _slot_dict(slot)}), 200


# DELETE /api/parking/<id>  remove slot
@parking_bp.route("/<int:sid>", methods=["DELETE"])
@admin_required
def delete_slot(sid):
    slot = ParkingSlot.query.get_or_404(sid)
    db.session.delete(slot)
    db.session.commit()
    return jsonify({"message": "Slot removed"}), 200


# helper 
def _slot_dict(s):
    return {
        "id": s.id,
        "slot_number": s.slot_number,
        "status": s.status,
        "occupied_by_apartment_id": s.occupied_by_apartment_id,
        "flat_number": s.occupied_by_apartment.flat_number if s.occupied_by_apartment else None,
        "visitor_name": s.visitor_name,
        "visitor_vehicle_number": s.visitor_vehicle_number,
        "expected_arrival_time": str(s.expected_arrival_time) if s.expected_arrival_time else None,
        "occupied_since": str(s.occupied_since) if s.occupied_since else None
    }
