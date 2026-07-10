from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, ConflictReport
from datetime import datetime

conflicts_bp = Blueprint("conflicts", __name__)


# GET /api/conflicts — admin sees all, resident sees their reports only
@conflicts_bp.route("/", methods=["GET"])
@jwt_required()
def get_conflicts():
    user_id = int(get_jwt_identity())
    from models import User
    user = User.query.get(user_id)

    if user.role in ["ADMIN", "TREASURER", "COMMITTEE_MEMBER"]:
        reports = ConflictReport.query.order_by(ConflictReport.created_at.desc()).all()
        return jsonify([_conflict_dict(r, reveal_reporter=True) for r in reports]), 200
    else:
        # resident sees only reports they raised
        reports = ConflictReport.query.filter_by(reported_by=user_id)\
                    .order_by(ConflictReport.created_at.desc()).all()
        return jsonify([_conflict_dict(r, reveal_reporter=False) for r in reports]), 200


# POST /api/conflicts — resident raises a conflict report
@conflicts_bp.route("/", methods=["POST"])
@jwt_required()
def raise_conflict():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["reported_apartment_id", "category", "description"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    report = ConflictReport(
        reported_by=user_id,
        reported_apartment_id=data["reported_apartment_id"],
        category=data["category"],
        description=data["description"]
    )
    db.session.add(report)
    db.session.commit()

    return jsonify({
        "message": "Conflict report submitted. The concerned flat will be notified anonymously.",
        "report_id": report.id
    }), 201


# PUT /api/conflicts/<id>/respond — reported flat submits their side
@conflicts_bp.route("/<int:rid>/respond", methods=["PUT"])
@jwt_required()
def submit_response(rid):
    report = ConflictReport.query.get_or_404(rid)
    data = request.get_json()

    if not data.get("response"):
        return jsonify({"error": "response text is required"}), 400

    report.reported_flat_response = data["response"]
    report.response_submitted_at = datetime.utcnow()
    report.status = "UNDER_REVIEW"
    db.session.commit()

    return jsonify({"message": "Response submitted. Secretary will review both sides."}), 200


# PUT /api/conflicts/<id>/resolve — secretary resolves
@conflicts_bp.route("/<int:rid>/resolve", methods=["PUT"])
@jwt_required()
def resolve_conflict(rid):
    user_id = int(get_jwt_identity())
    report = ConflictReport.query.get_or_404(rid)
    data = request.get_json()

    report.status = "RESOLVED"
    report.resolution_note = data.get("resolution_note", "Resolved by secretary")
    report.resolved_by = user_id
    report.resolved_at = datetime.utcnow()
    db.session.commit()

    return jsonify({"message": "Conflict resolved", "report": _conflict_dict(report, reveal_reporter=True)}), 200


# GET /api/conflicts/pending — conflicts awaiting response
@conflicts_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending():
    reports = ConflictReport.query.filter(
        ConflictReport.status.in_(["OPEN", "UNDER_REVIEW"])
    ).all()
    return jsonify([_conflict_dict(r, reveal_reporter=True) for r in reports]), 200


# ── helper ────────────────────────────────────────────────────
def _conflict_dict(r, reveal_reporter=False):
    data = {
        "id": r.id,
        "category": r.category,
        "description": r.description,
        "reported_apartment_id": r.reported_apartment_id,
        "reported_flat": r.reported_apartment.flat_number if r.reported_apartment else None,
        "reported_flat_response": r.reported_flat_response,
        "response_submitted_at": str(r.response_submitted_at) if r.response_submitted_at else None,
        "status": r.status,
        "resolution_note": r.resolution_note,
        "resolved_at": str(r.resolved_at) if r.resolved_at else None,
        "created_at": str(r.created_at)
    }
    # reporter identity only visible to admin/secretary
    if reveal_reporter:
        data["reported_by"] = r.reported_by
        data["reported_by_name"] = r.reporter.name if r.reporter else None
    return data
