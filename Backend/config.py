import os

class Config:
    SQLALCHEMY_DATABASE_URI = "sqlite:///societyease.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "societyease-secret-key-change-in-production")
    JWT_ACCESS_TOKEN_EXPIRES = False  # tokens don't expire — change in production
