"""
Shared source-of-truth for all SocietyEase diagrams.

Reverse-engineered from the actual codebase (models.py, app.py, api/*, auth/,
Frontend/src/*) and the project's git history. Every diagram script imports from
here so the diagrams stay consistent and accurate to the real code.
"""

# ---------------------------------------------------------------------------
# Domains: logical grouping of the 19 models, each with a colour theme.
# (header colour, cell fill colour)
# ---------------------------------------------------------------------------
DOMAINS = {
    "Identity & Residency": ("#2563eb", "#eff6ff"),
    "Complaints":           ("#ea580c", "#fff7ed"),
    "Finance":              ("#16a34a", "#f0fdf4"),
    "Operations":           ("#0d9488", "#f0fdfa"),
    "Governance":           ("#7c3aed", "#f5f3ff"),
    "Feature Modules":      ("#dc2626", "#fef2f2"),
}

# ---------------------------------------------------------------------------
# The 19 SQLAlchemy models.
# name -> {domain, table, fields: [(field, type, key)]}
#   key in {"PK", "FK", "U", ""}  (U = unique)
# ---------------------------------------------------------------------------
MODELS = {
    # --- Identity & Residency -------------------------------------------------
    "User": {
        "domain": "Identity & Residency", "table": "users",
        "fields": [
            ("id", "int", "PK"),
            ("name", "str(100)", ""),
            ("email", "str(120)", "U"),
            ("phone", "str(15)", "U"),
            ("password_hash", "str(255)", ""),
            ("role", "Enum(role)", ""),
            ("is_active", "bool", ""),
            ("created_at", "datetime", ""),
        ],
    },
    "Apartment": {
        "domain": "Identity & Residency", "table": "apartments",
        "fields": [
            ("id", "int", "PK"),
            ("block", "str(20)", ""),
            ("flat_number", "str(20)", "U"),
            ("floor", "int", ""),
        ],
    },
    "Resident": {
        "domain": "Identity & Residency", "table": "residents",
        "fields": [
            ("id", "int", "PK"),
            ("user_id", "int -> users", "FK"),
            ("apartment_id", "int -> apartments", "FK"),
            ("is_owner", "bool", ""),
            ("move_in_date", "date", ""),
            ("move_out_date", "date", ""),
        ],
    },
    # --- Complaints -----------------------------------------------------------
    "Complaint": {
        "domain": "Complaints", "table": "complaints",
        "fields": [
            ("id", "int", "PK"),
            ("raised_by", "int -> users", "FK"),
            ("apartment_id", "int -> apartments", "FK"),
            ("title", "str(150)", ""),
            ("description", "text", ""),
            ("category", "Enum", ""),
            ("priority", "Enum", ""),
            ("status", "Enum", ""),
            ("assigned_worker_id", "int -> users", "FK"),
            ("created_at", "datetime", ""),
            ("updated_at", "datetime", ""),
            ("resolved_at", "datetime", ""),
        ],
    },
    "ComplaintUpdate": {
        "domain": "Complaints", "table": "complaint_updates",
        "fields": [
            ("id", "int", "PK"),
            ("complaint_id", "int -> complaints", "FK"),
            ("updated_by", "int -> users", "FK"),
            ("status", "str(30)", ""),
            ("remarks", "text", ""),
            ("updated_at", "datetime", ""),
        ],
    },
    # --- Finance --------------------------------------------------------------
    "Invoice": {
        "domain": "Finance", "table": "invoices",
        "fields": [
            ("id", "int", "PK"),
            ("apartment_id", "int -> apartments", "FK"),
            ("generated_by", "int -> users", "FK"),
            ("month", "int", ""),
            ("year", "int", ""),
            ("amount", "Numeric(10,2)", ""),
            ("due_date", "date", ""),
            ("status", "Enum", ""),
            ("created_at", "datetime", ""),
        ],
    },
    "Payment": {
        "domain": "Finance", "table": "payments",
        "fields": [
            ("id", "int", "PK"),
            ("invoice_id", "int -> invoices", "FK"),
            ("resident_id", "int -> residents", "FK"),
            ("amount", "Numeric(10,2)", ""),
            ("payment_method", "str(50)", ""),
            ("transaction_reference", "str(100)", ""),
            ("payment_date", "datetime", ""),
        ],
    },
    "Expense": {
        "domain": "Finance", "table": "expenses",
        "fields": [
            ("id", "int", "PK"),
            ("category", "Enum", ""),
            ("description", "str(255)", ""),
            ("amount", "Numeric(10,2)", ""),
            ("expense_date", "date", ""),
            ("paid_by", "int -> users", "FK"),
            ("logged_by", "int -> users", "FK"),
            ("receipt_url", "str(255)", ""),
            ("created_at", "datetime", ""),
        ],
    },
    # --- Operations -----------------------------------------------------------
    "MaintenanceTask": {
        "domain": "Operations", "table": "maintenance_tasks",
        "fields": [
            ("id", "int", "PK"),
            ("title", "str(150)", ""),
            ("description", "text", ""),
            ("category", "Enum", ""),
            ("scheduled_date", "date", ""),
            ("status", "Enum", ""),
            ("created_by", "int -> users", "FK"),
            ("assigned_to", "int -> users", "FK"),
            ("created_at", "datetime", ""),
            ("completed_at", "datetime", ""),
        ],
    },
    "EmergencyContact": {
        "domain": "Operations", "table": "emergency_contacts",
        "fields": [
            ("id", "int", "PK"),
            ("name", "str(100)", ""),
            ("service_type", "str(50)", ""),
            ("phone", "str(15)", ""),
            ("availability", "str(100)", ""),
        ],
    },
    # --- Governance -----------------------------------------------------------
    "Announcement": {
        "domain": "Governance", "table": "announcements",
        "fields": [
            ("id", "int", "PK"),
            ("title", "str(200)", ""),
            ("content", "text", ""),
            ("category", "Enum", ""),
            ("published_by", "int -> users", "FK"),
            ("is_active", "bool", ""),
            ("created_at", "datetime", ""),
        ],
    },
    "Vote": {
        "domain": "Governance", "table": "votes",
        "fields": [
            ("id", "int", "PK"),
            ("title", "str(200)", ""),
            ("description", "text", ""),
            ("created_by", "int -> users", "FK"),
            ("start_date", "date", ""),
            ("end_date", "date", ""),
            ("status", "Enum", ""),
            ("created_at", "datetime", ""),
        ],
    },
    "VoteOption": {
        "domain": "Governance", "table": "vote_options",
        "fields": [
            ("id", "int", "PK"),
            ("vote_id", "int -> votes", "FK"),
            ("option_text", "str(255)", ""),
        ],
    },
    "VoteResponse": {
        "domain": "Governance", "table": "vote_responses",
        "fields": [
            ("id", "int", "PK"),
            ("vote_id", "int -> votes", "FK"),
            ("option_id", "int -> vote_options", "FK"),
            ("user_id", "int -> users", "FK"),
            ("created_at", "datetime", ""),
            ("UQ(vote_id, user_id)", "constraint", ""),
        ],
    },
    # --- Feature Modules ------------------------------------------------------
    "Equipment": {
        "domain": "Feature Modules", "table": "equipment",
        "fields": [
            ("id", "int", "PK"),
            ("name", "str(150)", ""),
            ("category", "Enum", ""),
            ("last_serviced_date", "date", ""),
            ("service_frequency_days", "int", ""),
            ("estimated_service_cost", "Numeric(10,2)", ""),
            ("created_by", "int -> users", "FK"),
            ("created_at", "datetime", ""),
        ],
    },
    "EquipmentServiceLog": {
        "domain": "Feature Modules", "table": "equipment_service_logs",
        "fields": [
            ("id", "int", "PK"),
            ("equipment_id", "int -> equipment", "FK"),
            ("serviced_date", "date", ""),
            ("cost", "Numeric(10,2)", ""),
            ("vendor_name", "str(150)", ""),
            ("notes", "text", ""),
            ("logged_by", "int -> users", "FK"),
            ("created_at", "datetime", ""),
        ],
    },
    "SocietyHealthScore": {
        "domain": "Feature Modules", "table": "society_health_scores",
        "fields": [
            ("id", "int", "PK"),
            ("month", "int", ""),
            ("year", "int", ""),
            ("payment_score", "Numeric(5,2)", ""),
            ("complaint_score", "Numeric(5,2)", ""),
            ("notice_score", "Numeric(5,2)", ""),
            ("poll_score", "Numeric(5,2)", ""),
            ("maintenance_score", "Numeric(5,2)", ""),
            ("total_score", "Numeric(5,2)", ""),
            ("alert_reason", "text", ""),
            ("calculated_at", "datetime", ""),
            ("UQ(month, year)", "constraint", ""),
        ],
    },
    "ConflictReport": {
        "domain": "Feature Modules", "table": "conflict_reports",
        "fields": [
            ("id", "int", "PK"),
            ("reported_by", "int -> users", "FK"),
            ("reported_apartment_id", "int -> apartments", "FK"),
            ("category", "Enum", ""),
            ("description", "text", ""),
            ("reported_flat_response", "text", ""),
            ("response_submitted_at", "datetime", ""),
            ("status", "Enum", ""),
            ("resolution_note", "text", ""),
            ("resolved_by", "int -> users", "FK"),
            ("resolved_at", "datetime", ""),
            ("created_at", "datetime", ""),
        ],
    },
    "ParkingSlot": {
        "domain": "Feature Modules", "table": "parking_slots",
        "fields": [
            ("id", "int", "PK"),
            ("slot_number", "str(20)", "U"),
            ("status", "Enum", ""),
            ("occupied_by_apartment_id", "int -> apartments", "FK"),
            ("occupied_since", "datetime", ""),
            ("expected_arrival_time", "datetime", ""),
            ("visitor_name", "str(100)", ""),
            ("visitor_vehicle_number", "str(20)", ""),
            ("updated_by", "int -> users", "FK"),
            ("updated_at", "datetime", ""),
        ],
    },
}

# ---------------------------------------------------------------------------
# Strong relationships (back_populates + cascade delete-orphan, or 1-1).
# (parent, child, parent_card, child_card, label)
# ---------------------------------------------------------------------------
STRONG_RELS = [
    ("User", "Resident", "1", "1", "has profile"),
    ("Apartment", "Resident", "1", "*", "houses"),
    ("Apartment", "Invoice", "1", "*", "billed"),
    ("Apartment", "Complaint", "1", "*", "has"),
    ("Resident", "Payment", "1", "*", "makes"),
    ("Invoice", "Payment", "1", "*", "settled by"),
    ("Complaint", "ComplaintUpdate", "1", "*", "timeline"),
    ("Vote", "VoteOption", "1", "*", "offers"),
    ("Vote", "VoteResponse", "1", "*", "collects"),
    ("VoteOption", "VoteResponse", "1", "*", "chosen in"),
    ("Equipment", "EquipmentServiceLog", "1", "*", "serviced"),
]

# ---------------------------------------------------------------------------
# Foreign-key reference edges to User (creator / assignee / logger / etc.)
# and to Apartment (one-directional). Rendered dashed to reduce clutter.
# (source_model, target_model, role_label)
# ---------------------------------------------------------------------------
REF_RELS = [
    ("Complaint", "User", "raised_by / worker"),
    ("ComplaintUpdate", "User", "updated_by"),
    ("Invoice", "User", "generated_by"),
    ("Expense", "User", "paid_by / logged_by"),
    ("MaintenanceTask", "User", "created_by / assigned_to"),
    ("Announcement", "User", "published_by"),
    ("Vote", "User", "created_by"),
    ("VoteResponse", "User", "voter"),
    ("Equipment", "User", "created_by"),
    ("EquipmentServiceLog", "User", "logged_by"),
    ("ConflictReport", "User", "reporter / resolver"),
    ("ParkingSlot", "User", "updated_by"),
    ("ConflictReport", "Apartment", "reported_flat"),
    ("ParkingSlot", "Apartment", "occupied_by"),
]

# ---------------------------------------------------------------------------
# Component / architecture design.
# ---------------------------------------------------------------------------
FRONTEND_SCREENS = [
    ("Home", "/"),
    ("LoginPage", "/login"),
    ("RegisterPage", "/register"),
    ("AssociationManager", "/association_manager"),
    ("AddAnnouncement", "/add-announcement"),
]

# 12 Flask blueprints (name, url prefix, one-line responsibility)
BLUEPRINTS = [
    ("auth", "/api/auth", "register, login, /me, change-password"),
    ("members", "/api/members", "apartments + residents CRUD"),
    ("complaints", "/api/complaints", "raise / assign / status workflow"),
    ("invoices", "/api/invoices", "invoices, bulk-gen, pay, receipt"),
    ("expenses", "/api/expenses", "expense log + monthly P&L"),
    ("notices", "/api/notices", "announcements CRUD"),
    ("polls", "/api/polls", "votes, options, cast, results"),
    ("maintenance", "/api/maintenance", "scheduled task CRUD"),
    ("equipment", "/api/equipment", "predictor: risk + forecast"),
    ("health", "/api/health", "society health score /100"),
    ("conflicts", "/api/conflicts", "anonymous conflict resolver"),
    ("parking", "/api/parking", "live visitor parking slots"),
]

# Which blueprints the frontend actually calls today.
WIRED_BLUEPRINTS = {"auth", "notices"}

# ---------------------------------------------------------------------------
# Gantt chart data - official project schedule.  (task, start, end)
# dates are "YYYY-MM-DD"; status (done / in-progress / planned) is derived
# from TODAY at render time.
# ---------------------------------------------------------------------------
TODAY = "2026-07-08"

GANTT_TASKS = [
    ("Identify User Requirements",                        "2026-06-18", "2026-06-28"),
    ("Wireframes, Page Specifications and System Design",  "2026-06-29", "2026-07-05"),
    ("Database Schema and Frontend Development",           "2026-07-06", "2026-07-22"),
    ("Backend APIs and Integration",                       "2026-07-23", "2026-08-02"),
    ("Testing and Review",                                 "2026-08-03", "2026-08-11"),
    ("Final Submission Preparation",                       "2026-08-12", "2026-08-23"),
]

# ---------------------------------------------------------------------------
# Kanban board data.  column -> list of (card, owner)
# ---------------------------------------------------------------------------
KANBAN = {
    "Done": [
        ("Design docs (class / DB / component)", "Mathijey"),
        ("DB schema - 19 SQLAlchemy models", "Nikhilesh"),
        ("12 backend API blueprints", "Mani Shankar"),
        ("Auth: register / login / JWT", "Nikhilesh"),
        ("Login & Register UI", "pratik0613"),
        ("Home landing page", "pratik0613"),
        ("Association Manager dashboard", "pratik0613"),
        ("Add Announcement page", "pratik0613"),
        ("Frontend <-> Backend auth integration", "team"),
    ],
    "In Progress": [
        ("Announcements management UI\n(edit-announcement route broken)", "pratik0613"),
        ("Home dashboard\n(placeholder / dead stats)", "pratik0613"),
    ],
    "To Do": [
        ("Members UI", "TBD"),
        ("Complaints UI", "TBD"),
        ("Invoices UI", "TBD"),
        ("Expenses UI", "TBD"),
        ("Polls UI", "TBD"),
        ("Maintenance tasks UI", "TBD"),
        ("Equipment predictor dashboard", "TBD"),
        ("Health score dashboard", "TBD"),
        ("Conflicts UI", "TBD"),
        ("Parking board UI", "TBD"),
        ("Emergency-Contacts API", "TBD"),
        ("JWT / security hardening", "TBD"),
        ("Remove HelloWorld.vue boilerplate", "TBD"),
        ("Docs <-> code reconciliation", "TBD"),
    ],
}

KANBAN_COLORS = {
    "Done":        ("#16a34a", "#f0fdf4"),
    "In Progress": ("#d97706", "#fffbeb"),
    "To Do":       ("#2563eb", "#eff6ff"),
}

PROJECT_TITLE = "SocietyEase - Apartment Association Management System"
TEAM = "MAY2026 - Team 084"
