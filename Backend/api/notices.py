from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Announcement

notices_bp = Blueprint("notices", __name__)


# GET /api/notices — all active notices
@notices_bp.route("/", methods=["GET"])
@jwt_required()
def get_notices():
    notices = Announcement.query.filter_by(is_active=True)\
                .order_by(Announcement.created_at.desc()).all()
    return jsonify([_notice_dict(n) for n in notices]), 200


# POST /api/notices — post new notice
@notices_bp.route("/", methods=["POST"])
@jwt_required()
def add_notice():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get("title") or not data.get("content"):
        return jsonify({"error": "title and content are required"}), 400

    notice = Announcement(
        title=data["title"],
        content=data["content"],
        category=data.get("category", "GENERAL"),
        published_by=user_id
    )
    db.session.add(notice)
    db.session.commit()
    return jsonify(_notice_dict(notice)), 201


# PUT /api/notices/<id> — update notice
@notices_bp.route("/<int:nid>", methods=["PUT"])
@jwt_required()
def update_notice(nid):
    notice = Announcement.query.get_or_404(nid)
    data = request.get_json()
    notice.title = data.get("title", notice.title)
    notice.content = data.get("content", notice.content)
    notice.category = data.get("category", notice.category)
    db.session.commit()
    return jsonify(_notice_dict(notice)), 200


# DELETE /api/notices/<id> — soft delete (deactivate)
@notices_bp.route("/<int:nid>", methods=["DELETE"])
@jwt_required()
def delete_notice(nid):
    notice = Announcement.query.get_or_404(nid)
    notice.is_active = False
    db.session.commit()
    return jsonify({"message": "Notice removed"}), 200


# ── helper ────────────────────────────────────────────────────
def _notice_dict(n):
    return {
        "id": n.id,
        "title": n.title,
        "content": n.content,
        "category": n.category,
        "published_by": n.published_by,
        "published_by_name": n.publisher.name if n.publisher else None,
        "is_active": n.is_active,
        "created_at": str(n.created_at)
    }
