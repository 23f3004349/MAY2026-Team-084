import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent / "instance" / "societyease.db"

class Config:
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DB_PATH.as_posix()}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "societyease-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = False 
