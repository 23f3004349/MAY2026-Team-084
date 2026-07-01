from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, User, Apartment, Resident
from werkzeug.security import generate_password_hash

members_bp = Blueprint("members", __name__)



#  APARTMENTS


# GET /api/members/apartments — list all apartments
@members_bp.route("/apartments", methods=["GET"])
@jwt_required()
def get_apartments():
    apartments = Apartment.query.all()
    return jsonify([_apt_dict(a) for a in apartments]), 200


# POST /api/members/apartments — add new apartment
@members_bp.route("/apartments", methods=["POST"])
@jwt_required()
def add_apartment():
    data = request.get_json()
    if not data.get("flat_number"):
        return jsonify({"error": "flat_number is required"}), 400

    if Apartment.query.filter_by(flat_number=data["flat_number"]).first():
        return jsonify({"error": "Flat number already exists"}), 409

    apt = Apartment(
        flat_number=data["flat_number"],
        block=data.get("block"),
        floor=data.get("floor")
    )
    db.session.add(apt)
    db.session.commit()
    return jsonify(_apt_dict(apt)), 201


# PUT /api/members/apartments/<id>  update apartment
@members_bp.route("/apartments/<int:apt_id>", methods=["PUT"])
@jwt_required()
def update_apartment(apt_id):
    apt = Apartment.query.get_or_404(apt_id)
    data = request.get_json()
    apt.block = data.get("block", apt.block)
    apt.floor = data.get("floor", apt.floor)
    db.session.commit()
    return jsonify(_apt_dict(apt)), 200


# DELETE /api/members/apartments/<id>  delete apartment
@members_bp.route("/apartments/<int:apt_id>", methods=["DELETE"])
@jwt_required()
def delete_apartment(apt_id):
    apt = Apartment.query.get_or_404(apt_id)
    db.session.delete(apt)
    db.session.commit()
    return jsonify({"message": "Apartment deleted"}), 200



#  MEMBERS (Users + Residents)

# GET /api/members  list all members with flat info
@members_bp.route("/", methods=["GET"])
@jwt_required()
def get_members():
    residents = Resident.query.all()
    return jsonify([_resident_dict(r) for r in residents]), 200


# POST /api/members add new member
@members_bp.route("/", methods=["POST"])
@jwt_required()
def add_member():
    data = request.get_json()
    required = ["name", "email", "password", "role", "apartment_id"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    apt = Apartment.query.get(data["apartment_id"])
    if not apt:
        return jsonify({"error": "Apartment not found"}), 404

    user = User(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        password_hash=generate_password_hash(data["password"]),
        role=data["role"]
    )
    db.session.add(user)
    db.session.flush()

    resident = Resident(
        user_id=user.id,
        apartment_id=data["apartment_id"],
        is_owner=data.get("is_owner", False),
        move_in_date=data.get("move_in_date")
    )
    db.session.add(resident)
    db.session.commit()

    return jsonify(_resident_dict(resident)), 201


# PUT /api/members/<id>  update member details
@members_bp.route("/<int:resident_id>", methods=["PUT"])
@jwt_required()
def update_member(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    data = request.get_json()

    # update user fields
    user = resident.user
    user.name = data.get("name", user.name)
    user.phone = data.get("phone", user.phone)

    # update resident fields
    resident.is_owner = data.get("is_owner", resident.is_owner)
    resident.move_in_date = data.get("move_in_date", resident.move_in_date)
    resident.move_out_date = data.get("move_out_date", resident.move_out_date)

    db.session.commit()
    return jsonify(_resident_dict(resident)), 200


# DELETE /api/members/<id>  deactivate member
@members_bp.route("/<int:resident_id>", methods=["DELETE"])
@jwt_required()
def deactivate_member(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    resident.user.is_active = False
    db.session.commit()
    return jsonify({"message": "Member deactivated"}), 200


# GET /api/members/<id>  get single member
@members_bp.route("/<int:resident_id>", methods=["GET"])
@jwt_required()
def get_member(resident_id):
    resident = Resident.query.get_or_404(resident_id)
    return jsonify(_resident_dict(resident)), 200


#  helpers 
def _apt_dict(a):
    return {
        "id": a.id,
        "flat_number": a.flat_number,
        "block": a.block,
        "floor": a.floor
    }

def _resident_dict(r):
    return {
        "id": r.id,
        "user_id": r.user_id,
        "name": r.user.name,
        "email": r.user.email,
        "phone": r.user.phone,
        "role": r.user.role,
        "is_active": r.user.is_active,
        "apartment_id": r.apartment_id,
        "flat_number": r.apartment.flat_number,
        "block": r.apartment.block,
        "floor": r.apartment.floor,
        "is_owner": r.is_owner,
        "move_in_date": str(r.move_in_date) if r.move_in_date else None,
        "move_out_date": str(r.move_out_date) if r.move_out_date else None,
    }
