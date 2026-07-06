"""Model database: User, QuranProgress, SuratRead, ZikirLog, PrayerLog."""
from datetime import datetime, date

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from .extensions import db, login_manager

TOTAL_SURAT = 114

# Daftar dzikir. `key` = identitas tetap di DB; label/target hanya tampilan.
ZIKIR_TYPES = [
    {"key": "subhanallah", "label": "Subhanallah", "arabic": "سُبْحَانَ اللَّهِ", "target": 33},
    {"key": "alhamdulillah", "label": "Alhamdulillah", "arabic": "الْحَمْدُ لِلَّهِ", "target": 33},
    {"key": "allahuakbar", "label": "Allahu Akbar", "arabic": "اللَّهُ أَكْبَر", "target": 34},
    {"key": "lailahaillallah", "label": "La ilaha illallah", "arabic": "لَا إِلَٰهَ إِلَّا اللَّه", "target": 100},
    {"key": "astaghfirullah", "label": "Astaghfirullah", "arabic": "أَسْتَغْفِرُ اللَّه", "target": 100},
]
ZIKIR_KEYS = {z["key"] for z in ZIKIR_TYPES}

PRAYER_FIELDS = ("subuh", "dzuhur", "ashar", "maghrib", "isya")


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


class User(UserMixin, db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    name = db.Column(db.String(120), nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Preferensi lokasi tersimpan (nama provinsi/kota dari equran.id).
    pref_provinsi = db.Column(db.String(120))
    pref_kabkota = db.Column(db.String(120))

    quran_progress = db.relationship(
        "QuranProgress", backref="user", uselist=False,
        cascade="all, delete-orphan",
    )
    surat_reads = db.relationship(
        "SuratRead", backref="user", cascade="all, delete-orphan",
    )
    zikir_logs = db.relationship(
        "ZikirLog", backref="user", cascade="all, delete-orphan",
    )
    prayer_logs = db.relationship(
        "PrayerLog", backref="user", cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def khatam_percent(self):
        return round(len(self.surat_reads) / TOTAL_SURAT * 100, 1)

    def __repr__(self):
        return f"<User {self.email}>"


class QuranProgress(db.Model):
    __tablename__ = "quran_progress"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.id"), unique=True, nullable=False,
    )
    last_surat = db.Column(db.Integer, nullable=False)
    last_ayat = db.Column(db.Integer, nullable=False, default=1)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow,
    )

    def to_dict(self):
        return {
            "last_surat": self.last_surat,
            "last_ayat": self.last_ayat,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SuratRead(db.Model):
    __tablename__ = "surat_reads"
    __table_args__ = (db.UniqueConstraint("user_id", "surat_no"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    surat_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ZikirLog(db.Model):
    __tablename__ = "zikir_logs"
    __table_args__ = (db.UniqueConstraint("user_id", "zikir_key", "log_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    zikir_key = db.Column(db.String(40), nullable=False)
    count = db.Column(db.Integer, nullable=False, default=0)
    log_date = db.Column(db.Date, nullable=False, default=date.today)


class PrayerLog(db.Model):
    __tablename__ = "prayer_logs"
    __table_args__ = (db.UniqueConstraint("user_id", "log_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False, default=date.today)
    subuh = db.Column(db.Boolean, default=False, nullable=False)
    dzuhur = db.Column(db.Boolean, default=False, nullable=False)
    ashar = db.Column(db.Boolean, default=False, nullable=False)
    maghrib = db.Column(db.Boolean, default=False, nullable=False)
    isya = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        data = {"date": self.log_date.isoformat()}
        data.update({f: getattr(self, f) for f in PRAYER_FIELDS})
        data["completed"] = sum(bool(getattr(self, f)) for f in PRAYER_FIELDS)
        return data
