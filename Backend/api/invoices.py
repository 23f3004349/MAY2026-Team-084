from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Invoice, Payment, Apartment, Resident
from datetime import datetime, date

invoices_bp = Blueprint("invoices", __name__)


# GET /api/invoices — all invoices (admin) or own (resident)
@invoices_bp.route("/", methods=["GET"])
@jwt_required()
def get_invoices():
    user_id = int(get_jwt_identity())
    from models import User
    user = User.query.get(user_id)

    if user.role in ["ADMIN", "TREASURER"]:
        invoices = Invoice.query.order_by(Invoice.created_at.desc()).all()
    else:
        resident = Resident.query.filter_by(user_id=user_id).first()
        if not resident:
            return jsonify([]), 200
        invoices = Invoice.query.filter_by(apartment_id=resident.apartment_id)\
                    .order_by(Invoice.created_at.desc()).all()

    return jsonify([_invoice_dict(i) for i in invoices]), 200


# POST /api/invoices — generate single invoice
@invoices_bp.route("/", methods=["POST"])
@jwt_required()
def create_invoice():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["apartment_id", "month", "year", "amount"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    invoice = Invoice(
        apartment_id=data["apartment_id"],
        generated_by=user_id,
        month=data["month"],
        year=data["year"],
        amount=data["amount"],
        due_date=data.get("due_date")
    )
    db.session.add(invoice)
    db.session.commit()
    return jsonify(_invoice_dict(invoice)), 201


# POST /api/invoices/bulk — generate invoices for ALL flats in one click
@invoices_bp.route("/bulk", methods=["POST"])
@jwt_required()
def bulk_generate():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["month", "year", "amount"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    apartments = Apartment.query.all()
    created = []

    for apt in apartments:
        # skip if invoice already exists for this month/year
        exists = Invoice.query.filter_by(
            apartment_id=apt.id,
            month=data["month"],
            year=data["year"]
        ).first()
        if exists:
            continue

        invoice = Invoice(
            apartment_id=apt.id,
            generated_by=user_id,
            month=data["month"],
            year=data["year"],
            amount=data["amount"],
            due_date=data.get("due_date")
        )
        db.session.add(invoice)
        created.append(apt.flat_number)

    db.session.commit()
    return jsonify({
        "message": f"Invoices generated for {len(created)} flats",
        "flats": created
    }), 201


# PUT /api/invoices/<id>/pay — mark invoice as paid
@invoices_bp.route("/<int:inv_id>/pay", methods=["PUT"])
@jwt_required()
def mark_paid(inv_id):
    user_id = int(get_jwt_identity())
    invoice = Invoice.query.get_or_404(inv_id)
    data = request.get_json()

    resident = Resident.query.filter_by(apartment_id=invoice.apartment_id).first()
    if not resident:
        return jsonify({"error": "No resident found for this apartment"}), 404

    invoice.status = "PAID"

    payment = Payment(
        invoice_id=invoice.id,
        resident_id=resident.id,
        amount=invoice.amount,
        payment_method=data.get("payment_method", "CASH"),
        transaction_reference=data.get("transaction_reference"),
        payment_date=datetime.utcnow()
    )
    db.session.add(payment)
    db.session.commit()

    return jsonify({
        "message": "Invoice marked as paid",
        "invoice": _invoice_dict(invoice),
        "receipt": _receipt_dict(payment, invoice)
    }), 200


# GET /api/invoices/<id>/receipt — download receipt data
@invoices_bp.route("/<int:inv_id>/receipt", methods=["GET"])
@jwt_required()
def get_receipt(inv_id):
    invoice = Invoice.query.get_or_404(inv_id)
    if invoice.status != "PAID":
        return jsonify({"error": "Invoice not paid yet"}), 400

    payment = Payment.query.filter_by(invoice_id=inv_id).first()
    return jsonify(_receipt_dict(payment, invoice)), 200


# GET /api/invoices/pending — all unpaid invoices
@invoices_bp.route("/pending", methods=["GET"])
@jwt_required()
def get_pending():
    invoices = Invoice.query.filter(Invoice.status != "PAID").all()
    return jsonify([_invoice_dict(i) for i in invoices]), 200


# ── helpers ───────────────────────────────────────────────────
def _invoice_dict(i):
    return {
        "id": i.id,
        "apartment_id": i.apartment_id,
        "flat_number": i.apartment.flat_number if i.apartment else None,
        "month": i.month,
        "year": i.year,
        "amount": float(i.amount),
        "due_date": str(i.due_date) if i.due_date else None,
        "status": i.status,
        "created_at": str(i.created_at)
    }

def _receipt_dict(p, i):
    return {
        "receipt_number": f"RCP-{str(p.id).zfill(4)}",
        "flat_number": i.apartment.flat_number if i.apartment else None,
        "month": i.month,
        "year": i.year,
        "amount": float(i.amount),
        "payment_method": p.payment_method,
        "transaction_reference": p.transaction_reference,
        "payment_date": str(p.payment_date)
    }
