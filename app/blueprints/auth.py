"""Autentikasi: daftar, masuk, keluar."""
from urllib.parse import urlparse

from flask import (
    Blueprint, render_template, redirect, url_for, flash, request,
)
from flask_login import login_user, logout_user, login_required, current_user

from ..extensions import db
from ..models import User
from ..forms import RegisterForm, LoginForm

auth_bp = Blueprint("auth", __name__)


def _safe_next(target):
    """Hanya izinkan redirect relatif satu situs (cegah open-redirect)."""
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.netloc == "" and parsed.scheme == "" and target.startswith("/"):
        return target
    return None


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        if User.query.filter_by(email=email).first():
            flash("Email sudah terdaftar.", "error")
        else:
            user = User(email=email, name=form.name.data.strip())
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash("Akun berhasil dibuat. Selamat datang!", "success")
            return redirect(url_for("main.index"))
    return render_template("auth/register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data.strip().lower()
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            nxt = _safe_next(request.args.get("next"))
            return redirect(nxt or url_for("main.index"))
        flash("Email atau kata sandi salah.", "error")
    return render_template("auth/login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
@login_required
def logout():
    logout_user()
    flash("Anda telah keluar.", "info")
    return redirect(url_for("main.index"))
