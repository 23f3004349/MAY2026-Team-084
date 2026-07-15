from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from models import db, SocietyHealthScore, Invoice, Complaint, Vote, VoteResponse, Announcement, Equipment
from datetime import date

health_bp = Blueprint("health", __name__)


def _calculate_score(month, year):
    """
    Calculates the Society Health Score for a given month/year.
    Returns a dict with individual scores and total.
    """

    # 1. Payment Score (30 pts) 
    total_invoices = Invoice.query.filter_by(month=month, year=year).count()
    paid_invoices = Invoice.query.filter_by(month=month, year=year, status="PAID").count()
    payment_score = round((paid_invoices / total_invoices * 30), 2) if total_invoices > 0 else 0

    # 2. Complaint Resolution Score (25 pts) 
    from sqlalchemy import extract, and_
    all_complaints = Complaint.query.filter(
        extract("month", Complaint.created_at) == month,
        extract("year", Complaint.created_at) == year
    ).count()

    resolved_complaints = Complaint.query.filter(
        extract("month", Complaint.created_at) == month,
        extract("year", Complaint.created_at) == year,
        Complaint.status.in_(["COMPLETED", "CLOSED"])
    ).count()
    complaint_score = round((resolved_complaints / all_complaints * 25), 2) if all_complaints > 0 else 25

    # 3. Notice Engagement Score (15 pts) 
    # Simple check: if any notice was posted this month → full score
    notices_posted = Announcement.query.filter(
        extract("month", Announcement.created_at) == month,
        extract("year", Announcement.created_at) == year,
        Announcement.is_active == True
    ).count()
    notice_score = 15 if notices_posted > 0 else 0

    #4. Poll Participation Score (15 pts)
    total_polls = Vote.query.filter(
        extract("month", Vote.created_at) == month,
        extract("year", Vote.created_at) == year
    ).count()

    from models import User, Resident
    total_residents = Resident.query.count()
    total_votes_cast = VoteResponse.query.filter(
        extract("month", VoteResponse.created_at) == month,
        extract("year", VoteResponse.created_at) == year
    ).count()

    if total_polls > 0 and total_residents > 0:
        participation_rate = total_votes_cast / (total_polls * total_residents)
        poll_score = round(min(participation_rate * 15, 15), 2)
    else:
        poll_score = 15  # no polls = not penalized

    # 5. Maintenance Score (15 pts) 
    all_equipment = Equipment.query.all()
    on_time = 0
    for eq in all_equipment:
        days_since = (date.today() - eq.last_serviced_date).days
        if days_since <= eq.service_frequency_days:
            on_time += 1

    maintenance_score = round((on_time / len(all_equipment) * 15), 2) if all_equipment else 15

    #Total 
    total = round(payment_score + complaint_score + notice_score + poll_score + maintenance_score, 2)

    #
    alerts = []
    if payment_score < 20:
        unpaid = total_invoices - paid_invoices
        alerts.append(f"{unpaid} invoices unpaid")
    if complaint_score < 15:
        overdue = all_complaints - resolved_complaints
        alerts.append(f"{overdue} complaints unresolved")
    if notice_score == 0:
        alerts.append("No notices posted this month")
    alert_reason = " | ".join(alerts) if alerts else "All metrics healthy"

    return {
        "month": month,
        "year": year,
        "payment_score": payment_score,
        "complaint_score": complaint_score,
        "notice_score": notice_score,
        "poll_score": poll_score,
        "maintenance_score": maintenance_score,
        "total_score": total,
        "alert_reason": alert_reason,
        "grade": "GREEN" if total >= 71 else ("YELLOW" if total >= 41 else "RED")
    }


# GET 
@health_bp.route("/calculate", methods=["GET"])
@jwt_required()
def calculate():
    month = request.args.get("month", type=int, default=date.today().month)
    year = request.args.get("year", type=int, default=date.today().year)

    result = _calculate_score(month, year)

    # upsert into DB
    existing = SocietyHealthScore.query.filter_by(month=month, year=year).first()
    if existing:
        existing.payment_score = result["payment_score"]
        existing.complaint_score = result["complaint_score"]
        existing.notice_score = result["notice_score"]
        existing.poll_score = result["poll_score"]
        existing.maintenance_score = result["maintenance_score"]
        existing.total_score = result["total_score"]
        existing.alert_reason = result["alert_reason"]
    else:
        record = SocietyHealthScore(
            month=month, year=year,
            payment_score=result["payment_score"],
            complaint_score=result["complaint_score"],
            notice_score=result["notice_score"],
            poll_score=result["poll_score"],
            maintenance_score=result["maintenance_score"],
            total_score=result["total_score"],
            alert_reason=result["alert_reason"]
        )
        db.session.add(record)

    db.session.commit()
    return jsonify(result), 200


# GET /api/health/history last 6 months scores
@health_bp.route("/history", methods=["GET"])
@jwt_required()
def history():
    scores = SocietyHealthScore.query\
                .order_by(SocietyHealthScore.year.desc(), SocietyHealthScore.month.desc())\
                .limit(6).all()
    return jsonify([_score_dict(s) for s in scores]), 200


# helper
def _score_dict(s):
    total = float(s.total_score)
    return {
        "id": s.id,
        "month": s.month,
        "year": s.year,
        "payment_score": float(s.payment_score),
        "complaint_score": float(s.complaint_score),
        "notice_score": float(s.notice_score),
        "poll_score": float(s.poll_score),
        "maintenance_score": float(s.maintenance_score),
        "total_score": total,
        "grade": "GREEN" if total >= 71 else ("YELLOW" if total >= 41 else "RED"),
        "alert_reason": s.alert_reason,
        "calculated_at": str(s.calculated_at)
    }
