from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User

auth_bp = Blueprint("auth", __name__)


# ── POST /api/auth/register ────────────────────────────────────
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    required = ["name", "email", "password", "role"]
    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"error": "Email already registered"}), 409

    valid_roles = ["ADMIN", "TENANT", "OWNER", "TREASURER",
                   "WORKER", "COMMITTEE_MEMBER", "AUDITOR", "SYSTEM_ADMIN"]
    if data["role"] not in valid_roles:
        return jsonify({"error": f"Invalid role. Choose from {valid_roles}"}), 400

    user = User(
        name=data["name"],
        email=data["email"],
        phone=data.get("phone"),
        password_hash=generate_password_hash(data["password"]),
        role=data["role"]
    )
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "User registered successfully",
        "token": token,
        "user": _user_dict(user)
    }), 201


# ── POST /api/auth/login ───────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password required"}), 400

    user = User.query.filter_by(email=data["email"]).first()
    if not user or not check_password_hash(user.password_hash, data["password"]):
        return jsonify({"error": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"error": "Account is deactivated"}), 403

    token = create_access_token(identity=str(user.id))
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": _user_dict(user)
    }), 200


# ── GET /api/auth/me ───────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(_user_dict(user)), 200


# ── PUT /api/auth/change-password ─────────────────────────────
@auth_bp.route("/change-password", methods=["PUT"])
@jwt_required()
def change_password():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    data = request.get_json()

    if not check_password_hash(user.password_hash, data.get("old_password", "")):
        return jsonify({"error": "Old password is incorrect"}), 400

    user.password_hash = generate_password_hash(data["new_password"])
    db.session.commit()
    return jsonify({"message": "Password changed successfully"}), 200


# ── helper ────────────────────────────────────────────────────
def _user_dict(u):
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "phone": u.phone,
        "role": u.role,
        "is_active": u.is_active,
        "created_at": str(u.created_at)
    }
