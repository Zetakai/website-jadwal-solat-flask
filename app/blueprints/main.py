"""Halaman publik + halaman fitur (perlu login)."""
from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from ..models import ZIKIR_TYPES

main_bp = Blueprint("main", __name__)


# --- Halaman publik (tanpa login) ---
@main_bp.route("/")
def index():
    return render_template("index.html")


@main_bp.route("/doa")
def doa():
    return render_template("doa.html")


@main_bp.route("/surat")
def surat():
    return render_template("surat.html")


@main_bp.route("/surat/<int:nomor>")
def detail_surat(nomor):
    return render_template("detail_surat.html", nomor=nomor)


@main_bp.route("/qibla")
def qibla():
    # Kiblat kini menyatu di halaman peta.
    return redirect(url_for("main.masjid", mode="kiblat"))


@main_bp.route("/masjid")
def masjid():
    return render_template("masjid.html")


# --- Halaman fitur (perlu login) ---
@main_bp.route("/zikir")
@login_required
def zikir():
    return render_template("zikir.html", zikir_types=ZIKIR_TYPES)


@main_bp.route("/ibadah")
@login_required
def ibadah():
    prayers = [
        {"key": "subuh", "label": "Subuh", "emoji": "🌙"},
        {"key": "dzuhur", "label": "Dzuhur", "emoji": "☀️"},
        {"key": "ashar", "label": "Ashar", "emoji": "🌤️"},
        {"key": "maghrib", "label": "Maghrib", "emoji": "🌅"},
        {"key": "isya", "label": "Isya", "emoji": "✨"},
    ]
    return render_template("ibadah.html", prayers=prayers)


@main_bp.route("/profile")
@login_required
def profile():
    return render_template("profile.html")
