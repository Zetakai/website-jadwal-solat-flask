"""Konfigurasi aplikasi. Nilai dibaca dari environment (.env)."""
import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-insecure-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or (
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "app.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = timedelta(days=30)

    EQURAN_API_BASE = os.environ.get("EQURAN_API_BASE", "https://equran.id")
    REQUEST_TIMEOUT = int(os.environ.get("REQUEST_TIMEOUT", "10"))


class ProductionConfig(Config):
    SESSION_COOKIE_SECURE = True
    REMEMBER_COOKIE_SECURE = True


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False


config_by_name = {
    "development": Config,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
