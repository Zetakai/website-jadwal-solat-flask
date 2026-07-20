"""Application factory."""  # pabrik aplikasi Flask
import os

from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

from .config import config_by_name, Config
from .extensions import db, migrate, login_manager, csrf

load_dotenv()


def create_app(config_name=None):
    config_name = config_name or os.environ.get("FLASK_CONFIG", "development")
    config_class = config_by_name.get(config_name, Config)

    # Template/static tetap di root repo (mengikuti layout awal).
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_class)

    _ensure_sqlite_dir(app)

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)

    from . import models  # noqa: F401  (daftarkan model + user_loader)
    _register_blueprints(app)
    _register_error_handlers(app)
    _register_cli(app)

    return app


def _register_error_handlers(app):
    """Halaman error ramah pengguna (HTML) + JSON untuk endpoint /api."""
    messages = {
        404: "Halaman yang Anda cari tidak ditemukan.",
        403: "Anda tidak memiliki akses ke halaman ini.",
        500: "Terjadi kesalahan pada server. Silakan coba lagi.",
    }

    def handler(err):
        code = getattr(err, "code", 500) or 500
        if request.path.startswith("/api/"):
            return jsonify({"error": messages.get(code, "Kesalahan")}), code
        return render_template(
            "error.html", code=code, message=messages.get(code, "Terjadi kesalahan.")
        ), code

    for code in (403, 404, 500):
        app.register_error_handler(code, handler)


def _ensure_sqlite_dir(app):
    """Buat folder untuk file SQLite bila belum ada."""
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    prefix = "sqlite:///"
    if uri.startswith(prefix) and ":memory:" not in uri:
        os.makedirs(os.path.dirname(uri[len(prefix):]), exist_ok=True)


def _register_blueprints(app):
    from .blueprints.main import main_bp
    from .blueprints.auth import auth_bp
    from .blueprints.api import api_bp
    from .blueprints.tracker import tracker_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    app.register_blueprint(tracker_bp)

    # Endpoint JSON pakai cookie sesi SameSite=Lax; token CSRF form akan
    # mematahkan fetch(), jadi blueprint JSON dikecualikan.
    csrf.exempt(api_bp)
    csrf.exempt(tracker_bp)


def _register_cli(app):
    @app.cli.command("init-db")
    def init_db():
        """Buat semua tabel (untuk dev; gunakan migrasi di produksi)."""
        db.create_all()
        print("Database initialized.")
