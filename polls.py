from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Vote, VoteOption, VoteResponse

polls_bp = Blueprint("polls", __name__)


# GET /api/polls  all polls
@polls_bp.route("/", methods=["GET"])
@jwt_required()
def get_polls():
    polls = Vote.query.order_by(Vote.created_at.desc()).all()
    return jsonify([_poll_dict(p) for p in polls]), 200


# POST /api/polls  create poll
@polls_bp.route("/", methods=["POST"])
@jwt_required()
def create_poll():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    if not data.get("title") or not data.get("options"):
        return jsonify({"error": "title and options are required"}), 400

    if len(data["options"]) < 2:
        return jsonify({"error": "At least 2 options required"}), 400

    poll = Vote(
        title=data["title"],
        description=data.get("description"),
        created_by=user_id,
        start_date=data.get("start_date"),
        end_date=data.get("end_date"),
        status="ACTIVE"
    )
    db.session.add(poll)
    db.session.flush()

    for opt_text in data["options"]:
        opt = VoteOption(vote_id=poll.id, option_text=opt_text)
        db.session.add(opt)

    db.session.commit()
    return jsonify(_poll_dict(poll)), 201


# GET /api/polls/<id>  single poll with results
@polls_bp.route("/<int:pid>", methods=["GET"])
@jwt_required()
def get_poll(pid):
    poll = Vote.query.get_or_404(pid)
    return jsonify(_poll_dict(poll)), 200


# POST /api/polls/<id>/vote  cast vote
@polls_bp.route("/<int:pid>/vote", methods=["POST"])
@jwt_required()
def cast_vote(pid):
    user_id = int(get_jwt_identity())
    poll = Vote.query.get_or_404(pid)

    if poll.status != "ACTIVE":
        return jsonify({"error": "Poll is not active"}), 400

    # check already voted
    already = VoteResponse.query.filter_by(vote_id=pid, user_id=user_id).first()
    if already:
        return jsonify({"error": "You have already voted"}), 409

    data = request.get_json()
    option = VoteOption.query.filter_by(
        id=data.get("option_id"), vote_id=pid
    ).first()
    if not option:
        return jsonify({"error": "Invalid option"}), 400

    response = VoteResponse(
        vote_id=pid,
        option_id=option.id,
        user_id=user_id
    )
    db.session.add(response)
    db.session.commit()
    return jsonify({"message": "Vote cast successfully", "poll": _poll_dict(poll)}), 200


# PUT /api/polls/<id>/close  close poll
@polls_bp.route("/<int:pid>/close", methods=["PUT"])
@jwt_required()
def close_poll(pid):
    poll = Vote.query.get_or_404(pid)
    poll.status = "CLOSED"
    db.session.commit()
    return jsonify({"message": "Poll closed", "poll": _poll_dict(poll)}), 200


# DELETE /api/polls/<id>  delete poll
@polls_bp.route("/<int:pid>", methods=["DELETE"])
@jwt_required()
def delete_poll(pid):
    poll = Vote.query.get_or_404(pid)
    db.session.delete(poll)
    db.session.commit()
    return jsonify({"message": "Poll deleted"}), 200


#  helper 
def _poll_dict(p):
    total_votes = len(p.responses)
    options = []
    for opt in p.options:
        count = VoteResponse.query.filter_by(option_id=opt.id).count()
        options.append({
            "id": opt.id,
            "text": opt.option_text,
            "votes": count,
            "percentage": round((count / total_votes * 100), 1) if total_votes > 0 else 0
        })
    return {
        "id": p.id,
        "title": p.title,
        "description": p.description,
        "status": p.status,
        "total_votes": total_votes,
        "options": options,
        "created_by": p.created_by,
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None,
        "created_at": str(p.created_at)
    }
