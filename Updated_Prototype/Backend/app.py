from flask import Flask
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from config import Config
from models import db

# imports all route blueprints 
from auth.routes import auth_bp
from api.members import members_bp
from api.complaints import complaints_bp
from api.invoices import invoices_bp
from api.expenses import expenses_bp
from api.notices import notices_bp
from api.polls import polls_bp
from api.maintenance import maintenance_bp
from api.equipment import equipment_bp
from api.health import health_bp
from api.conflicts import conflicts_bp
from api.parking import parking_bp
from api.features import features_bp


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    JWTManager(app)
  

    CORS(
        app,
        resources={r"/api/*": {"origins": [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://localhost:5175",
            "http://localhost:5176",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
            "http://127.0.0.1:5175",
            "http://127.0.0.1:5176",
            "http://0.0.0.0:5173",
            "http://0.0.0.0:5174",
            "http://0.0.0.0:5175",
            "http://0.0.0.0:5176",
        ]}},
    )

    #  register all blueprints
    app.register_blueprint(auth_bp,        url_prefix="/api/auth")
    app.register_blueprint(members_bp,     url_prefix="/api/members")
    app.register_blueprint(complaints_bp,  url_prefix="/api/complaints")
    app.register_blueprint(invoices_bp,    url_prefix="/api/invoices")
    app.register_blueprint(expenses_bp,    url_prefix="/api/expenses")
    app.register_blueprint(notices_bp,     url_prefix="/api/notices")
    app.register_blueprint(polls_bp,       url_prefix="/api/polls")
    app.register_blueprint(maintenance_bp, url_prefix="/api/maintenance")
    app.register_blueprint(equipment_bp,   url_prefix="/api/equipment")
    app.register_blueprint(health_bp,      url_prefix="/api/health")
    app.register_blueprint(conflicts_bp,   url_prefix="/api/conflicts")
    app.register_blueprint(parking_bp,     url_prefix="/api/parking")
    app.register_blueprint(features_bp,    url_prefix="/api/features")
    
    with app.app_context():
        db.create_all()

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
