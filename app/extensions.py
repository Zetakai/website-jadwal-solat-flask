"""Instance ekstensi Flask, di-bind ke app di dalam create_app()."""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_wtf import CSRFProtect

db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
csrf = CSRFProtect()

login_manager.login_view = "auth.login"
login_manager.login_message = "Silakan masuk untuk mengakses fitur ini."
login_manager.login_message_category = "info"
