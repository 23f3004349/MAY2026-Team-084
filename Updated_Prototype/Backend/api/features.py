from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, VisitorPass, AmenityBooking, EventAttendance, MarketplaceListing, MarketplaceMessage, User
from uuid import uuid4

features_bp = Blueprint("features", __name__)


@features_bp.route("/visitor-passes", methods=["GET"])
def list_visitor_passes():
    rows = VisitorPass.query.order_by(VisitorPass.created_at.desc()).all()
    return jsonify([_pass_dict(row) for row in rows]), 200


@features_bp.route("/visitor-passes", methods=["POST"])
@jwt_required()
def create_visitor_pass():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    visitor_name = (data.get("visitor_name") or "").strip()
    slot = (data.get("slot") or "").strip()
    if not visitor_name or not slot:
        return jsonify({"error": "visitor_name and slot are required"}), 400

    record = VisitorPass(
        visitor_name=visitor_name,
        pass_type=data.get("pass_type") or "Visitor",
        slot=slot,
        status=data.get("status") or "Pending",
        eta=data.get("eta"),
        pass_code=data.get("pass_code") or f"VP-{uuid4().hex[:6].upper()}",
        note=data.get("note"),
        created_by=user_id,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(_pass_dict(record)), 201


@features_bp.route("/amenity-bookings", methods=["GET"])
def list_amenity_bookings():
    user_id = None
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        user_id = None
    if user_id is None:
        rows = []
    else:
        rows = AmenityBooking.query.filter_by(user_id=user_id).order_by(AmenityBooking.created_at.desc()).all()
    return jsonify([_booking_dict(row) for row in rows]), 200


@features_bp.route("/amenity-bookings", methods=["POST"])
@jwt_required()
def toggle_amenity_booking():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    amenity_name = (data.get("amenity_name") or "").strip()
    slot_time = (data.get("slot_time") or "").strip()
    if not amenity_name or not slot_time:
        return jsonify({"error": "amenity_name and slot_time are required"}), 400

    existing = AmenityBooking.query.filter_by(user_id=user_id, amenity_name=amenity_name, slot_time=slot_time).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        return jsonify({"booked": False, "message": "Booking removed"}), 200

    booking = AmenityBooking(
        user_id=user_id,
        amenity_name=amenity_name,
        slot_time=slot_time,
        recurring=bool(data.get("recurring", False)),
    )
    db.session.add(booking)
    db.session.commit()
    return jsonify({"booked": True, "booking": _booking_dict(booking)}), 201


@features_bp.route("/event-attendance", methods=["GET"])
def list_event_attendance():
    user_id = None
    try:
        user_id = int(get_jwt_identity())
    except Exception:
        user_id = None
    if user_id is None:
        rows = []
    else:
        rows = EventAttendance.query.filter_by(user_id=user_id).order_by(EventAttendance.event_id).all()
    return jsonify([_attendance_dict(row) for row in rows]), 200


@features_bp.route("/events/<int:event_id>/attendance", methods=["POST"])
@jwt_required()
def set_event_attendance(event_id):
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    row = EventAttendance.query.filter_by(event_id=event_id, user_id=user_id).first()
    if not row:
        row = EventAttendance(event_id=event_id, user_id=user_id)
        db.session.add(row)
        db.session.flush()

    if "is_attending" in data:
        row.is_attending = bool(data.get("is_attending"))
    if "reminder_enabled" in data:
        row.reminder_enabled = bool(data.get("reminder_enabled"))
    db.session.commit()
    return jsonify(_attendance_dict(row)), 200


@features_bp.route("/marketplace/listings", methods=["GET"])
def list_marketplace_listings():
    rows = MarketplaceListing.query.order_by(MarketplaceListing.created_at.desc()).all()
    return jsonify([_listing_dict(row) for row in rows]), 200


@features_bp.route("/marketplace/listings", methods=["POST"])
@jwt_required()
def create_marketplace_listing():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400

    record = MarketplaceListing(
        title=title,
        price=int(data.get("price") or 0),
        category=data.get("category") or "For Sale",
        condition=data.get("condition") or "New listing",
        seller_name=user.name if user else "Resident",
        seller_flat=data.get("seller_flat") or "A-101",
        emoji=data.get("emoji") or "🏷️",
        created_by=user_id,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(_listing_dict(record)), 201


@features_bp.route("/marketplace/listings/<int:listing_id>/messages", methods=["GET"])
def list_marketplace_messages(listing_id):
    listing = MarketplaceListing.query.get_or_404(listing_id)
    rows = MarketplaceMessage.query.filter_by(listing_id=listing.id).order_by(MarketplaceMessage.created_at.asc()).all()
    return jsonify([_message_dict(row) for row in rows]), 200


@features_bp.route("/marketplace/listings/<int:listing_id>/messages", methods=["POST"])
@jwt_required()
def add_marketplace_message(listing_id):
    listing = MarketplaceListing.query.get_or_404(listing_id)
    data = request.get_json() or {}
    text = (data.get("text") or "").strip()
    if not text:
        return jsonify({"error": "text is required"}), 400

    record = MarketplaceMessage(
        listing_id=listing.id,
        author_name=data.get("author_name") or "You",
        text=text,
    )
    db.session.add(record)
    db.session.commit()
    return jsonify(_message_dict(record)), 201


@features_bp.route("/redeemables", methods=["GET"])
def list_redeemables():
    return jsonify([
        {"id": 1, "title": "Complimentary guest pass", "cost": 180, "icon": "fa-id-card", "desc": "One free visitor day pass for the next weekend", "accent": "teal"},
        {"id": 2, "title": "Priority amenity booking", "cost": 240, "icon": "fa-calendar-check", "desc": "Reserve prime slots ahead of other residents", "accent": "navy"},
        {"id": 3, "title": "Community lounge coupon", "cost": 320, "icon": "fa-gift", "desc": "₹200 off for the clubhouse café", "accent": "marigold"},
    ]), 200


def _pass_dict(record):
    return {
        "id": record.id,
        "visitor_name": record.visitor_name,
        "pass_type": record.pass_type,
        "slot": record.slot,
        "status": record.status,
        "eta": record.eta,
        "passCode": record.pass_code,
        "note": record.note,
        "created_at": str(record.created_at),
    }


def _booking_dict(record):
    return {
        "id": record.id,
        "amenity_name": record.amenity_name,
        "slot_time": record.slot_time,
        "recurring": record.recurring,
        "created_at": str(record.created_at),
    }


def _attendance_dict(record):
    return {
        "event_id": record.event_id,
        "is_attending": record.is_attending,
        "reminder_enabled": record.reminder_enabled,
    }


def _listing_dict(record):
    return {
        "id": record.id,
        "title": record.title,
        "price": record.price,
        "category": record.category,
        "condition": record.condition,
        "seller": record.seller_name,
        "flat": record.seller_flat,
        "emoji": record.emoji,
        "time": str(record.created_at),
        "messages": [_message_dict(msg) for msg in record.messages],
    }


def _message_dict(record):
    return {
        "id": record.id,
        "author": record.author_name,
        "text": record.text,
        "time": str(record.created_at),
    }
