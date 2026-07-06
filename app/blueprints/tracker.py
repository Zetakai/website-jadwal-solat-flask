"""API fitur per-pengguna (perlu login). Semua data dibatasi ke current_user."""
from datetime import date, timedelta

from flask import Blueprint, jsonify, request
from flask_login import login_required, current_user

from ..extensions import db
from ..models import (
    QuranProgress, SuratRead, ZikirLog, PrayerLog,
    ZIKIR_KEYS, PRAYER_FIELDS, TOTAL_SURAT,
)

tracker_bp = Blueprint("tracker", __name__, url_prefix="/api/me")


def _trailing_streak(day_set):
    """Jumlah hari berturut-turut (berakhir hari ini/kemarin) yang ada di set.
    Hari ini yang belum terpenuhi diberi kelonggaran (streak dihitung dari kemarin)."""
    today = date.today()
    d = today if today in day_set else today - timedelta(days=1)
    n = 0
    while d in day_set:
        n += 1
        d -= timedelta(days=1)
    return n


@tracker_bp.before_request
@login_required
def require_login():
    """Wajibkan login untuk seluruh endpoint di blueprint ini."""
    pass


def _parse_date(value):
    if not value:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return date.today()


# ----------------------------------------------------------------------------
# Preferensi lokasi
# ----------------------------------------------------------------------------
@tracker_bp.get("/location")
def get_location():
    return jsonify({
        "provinsi": current_user.pref_provinsi,
        "kabkota": current_user.pref_kabkota,
    })


@tracker_bp.put("/location")
def save_location():
    data = request.get_json(silent=True) or {}
    current_user.pref_provinsi = (data.get("provinsi") or "").strip() or None
    current_user.pref_kabkota = (data.get("kabkota") or "").strip() or None
    db.session.commit()
    return jsonify({"status": "ok"})


@tracker_bp.delete("/location")
def clear_location():
    current_user.pref_provinsi = None
    current_user.pref_kabkota = None
    db.session.commit()
    return jsonify({"status": "ok"})


# ----------------------------------------------------------------------------
# Al-Qur'an: posisi baca terakhir + khatam (surat selesai)
# ----------------------------------------------------------------------------
@tracker_bp.get("/quran/progress")
def get_progress():
    p = current_user.quran_progress
    reads = sorted(r.surat_no for r in current_user.surat_reads)
    return jsonify({
        "progress": p.to_dict() if p else None,
        "reads": reads,
        "total_surat": TOTAL_SURAT,
        "khatam_percent": current_user.khatam_percent,
    })


@tracker_bp.put("/quran/progress")
def save_progress():
    data = request.get_json(silent=True) or {}
    try:
        surat = int(data.get("surat"))
        ayat = int(data.get("ayat", 1))
    except (TypeError, ValueError):
        return jsonify({"error": "surat/ayat tidak valid"}), 400
    if not (1 <= surat <= TOTAL_SURAT) or ayat < 1:
        return jsonify({"error": "surat/ayat di luar rentang"}), 400

    p = current_user.quran_progress
    if p is None:
        p = QuranProgress(user_id=current_user.id, last_surat=surat, last_ayat=ayat)
        db.session.add(p)
    else:
        p.last_surat, p.last_ayat = surat, ayat
    db.session.commit()
    return jsonify(p.to_dict())


@tracker_bp.post("/quran/reads/<int:surat_no>")
def mark_surat_read(surat_no):
    if not (1 <= surat_no <= TOTAL_SURAT):
        return jsonify({"error": "Nomor surat tidak valid"}), 400
    existing = SuratRead.query.filter_by(
        user_id=current_user.id, surat_no=surat_no).first()
    if not existing:
        db.session.add(SuratRead(user_id=current_user.id, surat_no=surat_no))
        db.session.commit()
    return jsonify({"status": "ok", "surat_no": surat_no, "read": True})


@tracker_bp.delete("/quran/reads/<int:surat_no>")
def unmark_surat_read(surat_no):
    SuratRead.query.filter_by(
        user_id=current_user.id, surat_no=surat_no).delete()
    db.session.commit()
    return jsonify({"status": "ok", "surat_no": surat_no, "read": False})


# ----------------------------------------------------------------------------
# Zikir: penghitung per hari
# ----------------------------------------------------------------------------
def _get_or_create_zikir(key, day):
    row = ZikirLog.query.filter_by(
        user_id=current_user.id, zikir_key=key, log_date=day).first()
    if row is None:
        row = ZikirLog(user_id=current_user.id, zikir_key=key, count=0, log_date=day)
        db.session.add(row)
    return row


@tracker_bp.get("/zikir")
def get_zikir():
    day = _parse_date(request.args.get("date"))
    rows = ZikirLog.query.filter_by(user_id=current_user.id, log_date=day).all()
    counts = {r.zikir_key: r.count for r in rows}
    return jsonify({"date": day.isoformat(), "counts": counts})


@tracker_bp.get("/zikir/history")
def zikir_history():
    """Total zikir per hari dalam satu bulan (untuk kalender)."""
    today = date.today()
    year = request.args.get("year", type=int) or today.year
    month = request.args.get("month", type=int) or today.month
    if not (1 <= month <= 12):
        return jsonify({"error": "Bulan tidak valid"}), 400

    start = date(year, month, 1)
    end = date(year + (month == 12), (month % 12) + 1, 1)
    rows = ZikirLog.query.filter(
        ZikirLog.user_id == current_user.id,
        ZikirLog.log_date >= start,
        ZikirLog.log_date < end,
    ).all()
    days = {}
    for r in rows:
        days[r.log_date.isoformat()] = days.get(r.log_date.isoformat(), 0) + r.count
    return jsonify({"year": year, "month": month, "days": days})


@tracker_bp.post("/zikir/<key>")
def increment_zikir(key):
    if key not in ZIKIR_KEYS:
        return jsonify({"error": "Jenis dzikir tidak dikenal"}), 400
    step = (request.get_json(silent=True) or {}).get("step", 1)
    try:
        step = int(step)
    except (TypeError, ValueError):
        step = 1
    day = date.today()
    row = _get_or_create_zikir(key, day)
    row.count = max(0, row.count + step)
    db.session.commit()
    return jsonify({"key": key, "count": row.count})


@tracker_bp.delete("/zikir/<key>")
def reset_zikir(key):
    if key not in ZIKIR_KEYS:
        return jsonify({"error": "Jenis dzikir tidak dikenal"}), 400
    row = _get_or_create_zikir(key, date.today())
    row.count = 0
    db.session.commit()
    return jsonify({"key": key, "count": 0})


# ----------------------------------------------------------------------------
# Ceklis shalat: catatan 5 waktu per hari
# ----------------------------------------------------------------------------
def _get_or_create_prayer(day):
    row = PrayerLog.query.filter_by(user_id=current_user.id, log_date=day).first()
    if row is None:
        row = PrayerLog(user_id=current_user.id, log_date=day)
        db.session.add(row)
    return row


@tracker_bp.get("/prayer")
def get_prayer():
    day = _parse_date(request.args.get("date"))
    row = PrayerLog.query.filter_by(user_id=current_user.id, log_date=day).first()
    if row is None:
        empty = {"date": day.isoformat(), "completed": 0}
        empty.update({f: False for f in PRAYER_FIELDS})
        return jsonify(empty)
    return jsonify(row.to_dict())


@tracker_bp.put("/prayer")
def update_prayer():
    data = request.get_json(silent=True) or {}
    day = _parse_date(data.get("date"))
    row = _get_or_create_prayer(day)
    for field in PRAYER_FIELDS:
        if field in data:
            setattr(row, field, bool(data[field]))
    db.session.commit()
    return jsonify(row.to_dict())


@tracker_bp.get("/prayer/history")
def prayer_history():
    """Riwayat ceklis shalat satu bulan (untuk kalender)."""
    today = date.today()
    year = request.args.get("year", type=int) or today.year
    month = request.args.get("month", type=int) or today.month
    if not (1 <= month <= 12):
        return jsonify({"error": "Bulan tidak valid"}), 400

    start = date(year, month, 1)
    end = date(year + (month == 12), (month % 12) + 1, 1)  # awal bulan berikutnya
    rows = PrayerLog.query.filter(
        PrayerLog.user_id == current_user.id,
        PrayerLog.log_date >= start,
        PrayerLog.log_date < end,
    ).all()
    return jsonify({
        "year": year,
        "month": month,
        "days": {r.log_date.isoformat(): r.to_dict() for r in rows},
    })


# ----------------------------------------------------------------------------
# Statistik & streak (gamifikasi)
# ----------------------------------------------------------------------------
@tracker_bp.get("/stats")
def stats():
    uid = current_user.id
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Senin minggu ini

    # Shalat
    prayer_rows = PrayerLog.query.filter_by(user_id=uid).all()
    full_days = {r.log_date for r in prayer_rows
                 if all(getattr(r, f) for f in PRAYER_FIELDS)}
    prayer_week = sum(
        sum(bool(getattr(r, f)) for f in PRAYER_FIELDS)
        for r in prayer_rows if r.log_date >= week_start
    )

    # Zikir
    zikir_rows = ZikirLog.query.filter_by(user_id=uid).all()
    zikir_days = {r.log_date for r in zikir_rows if r.count > 0}
    zikir_total = sum(r.count for r in zikir_rows)

    return jsonify({
        "prayer_streak": _trailing_streak(full_days),
        "prayer_full_days": len(full_days),
        "prayer_week": prayer_week,          # dari 35 (7 hari x 5)
        "zikir_streak": _trailing_streak(zikir_days),
        "zikir_active_days": len(zikir_days),
        "zikir_total": zikir_total,
        "khatam_percent": current_user.khatam_percent,
        "reads_count": len(current_user.surat_reads),
        "total_surat": TOTAL_SURAT,
        "member_since": current_user.created_at.date().isoformat(),
    })
