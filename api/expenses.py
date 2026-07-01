from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import db, Expense

expenses_bp = Blueprint("expenses", __name__)


# GET /api/expenses  list all expenses
@expenses_bp.route("/", methods=["GET"])
@jwt_required()
def get_expenses():
    expenses = Expense.query.order_by(Expense.expense_date.desc()).all()
    return jsonify([_expense_dict(e) for e in expenses]), 200


# POST /api/expenses  log new expense
@expenses_bp.route("/", methods=["POST"])
@jwt_required()
def add_expense():
    user_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["category", "description", "amount", "expense_date"]
    for f in required:
        if not data.get(f):
            return jsonify({"error": f"{f} is required"}), 400

    expense = Expense(
        category=data["category"],
        description=data["description"],
        amount=data["amount"],
        expense_date=data["expense_date"],
        paid_by=data.get("paid_by", user_id),
        logged_by=user_id,
        receipt_url=data.get("receipt_url")
    )
    db.session.add(expense)
    db.session.commit()
    return jsonify(_expense_dict(expense)), 201


# PUT /api/expenses/<id>  update expense
@expenses_bp.route("/<int:exp_id>", methods=["PUT"])
@jwt_required()
def update_expense(exp_id):
    expense = Expense.query.get_or_404(exp_id)
    data = request.get_json()
    expense.description = data.get("description", expense.description)
    expense.amount = data.get("amount", expense.amount)
    expense.category = data.get("category", expense.category)
    expense.receipt_url = data.get("receipt_url", expense.receipt_url)
    db.session.commit()
    return jsonify(_expense_dict(expense)), 200


# DELETE /api/expenses/<id>  delete expense
@expenses_bp.route("/<int:exp_id>", methods=["DELETE"])
@jwt_required()
def delete_expense(exp_id):
    expense = Expense.query.get_or_404(exp_id)
    db.session.delete(expense)
    db.session.commit()
    return jsonify({"message": "Expense deleted"}), 200


# GET /api/expenses/summary  monthly P&L summary
@expenses_bp.route("/summary", methods=["GET"])
@jwt_required()
def summary():
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)

    from models import Invoice
    from sqlalchemy import extract

    query = Expense.query
    inv_query = Invoice.query.filter_by(status="PAID")

    if month and year:
        query = query.filter(
            extract("month", Expense.expense_date) == month,
            extract("year", Expense.expense_date) == year
        )
        inv_query = inv_query.filter_by(month=month, year=year)

    expenses = query.all()
    total_expense = sum(float(e.amount) for e in expenses)
    total_income = sum(float(i.amount) for i in inv_query.all())

    by_category = {}
    for e in expenses:
        by_category[e.category] = by_category.get(e.category, 0) + float(e.amount)

    return jsonify({
        "total_income": total_income,
        "total_expense": total_expense,
        "net_balance": total_income - total_expense,
        "by_category": by_category
    }), 200


#  helper 
def _expense_dict(e):
    return {
        "id": e.id,
        "category": e.category,
        "description": e.description,
        "amount": float(e.amount),
        "expense_date": str(e.expense_date),
        "paid_by": e.paid_by,
        "paid_by_name": e.payer.name if e.payer else None,
        "receipt_url": e.receipt_url,
        "created_at": str(e.created_at)
    }
