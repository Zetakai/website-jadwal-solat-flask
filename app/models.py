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

# Jumlah ayat tiap surat (Hafs). Indeks 0 tak dipakai (surat 1..114).
AYAT_COUNTS = [
    0, 7, 286, 200, 176, 120, 165, 206, 75, 129, 109, 123, 111, 43, 52, 99,
    128, 111, 110, 98, 135, 112, 78, 118, 64, 77, 227, 93, 88, 69, 60, 34, 30,
    73, 54, 45, 83, 182, 88, 75, 85, 54, 53, 89, 59, 37, 35, 38, 29, 18, 45,
    60, 49, 62, 55, 78, 96, 29, 22, 24, 13, 14, 11, 11, 18, 12, 12, 30, 52, 52,
    44, 28, 28, 20, 56, 40, 31, 50, 40, 46, 42, 29, 19, 36, 25, 22, 17, 19, 26,
    30, 20, 15, 21, 11, 8, 8, 19, 5, 8, 8, 11, 11, 8, 3, 9, 5, 4, 7, 3, 6, 3,
    5, 4, 5, 6,
]
TOTAL_AYAT = sum(AYAT_COUNTS)  # 6236

# Awal tiap juz (surat, ayat) — 30 juz.
JUZ_STARTS = [
    (1, 1), (2, 142), (2, 253), (3, 93), (4, 24), (4, 148), (5, 82), (6, 111),
    (7, 88), (8, 41), (9, 93), (11, 6), (12, 53), (15, 1), (17, 1), (18, 75),
    (21, 1), (23, 1), (25, 21), (27, 56), (29, 46), (33, 31), (36, 28),
    (39, 32), (41, 47), (46, 1), (51, 31), (58, 1), (67, 1), (78, 1),
]
TOTAL_JUZ = 30


def global_ayat_index(surat, ayat):
    """Nomor ayat global (1..6236) dari posisi surat:ayat."""
    return sum(AYAT_COUNTS[1:surat]) + ayat


# Indeks global awal tiap juz (untuk pencarian cepat).
_JUZ_START_INDEX = [global_ayat_index(s, a) for s, a in JUZ_STARTS]


def juz_of(surat, ayat):
    """Juz (1..30) yang memuat posisi surat:ayat."""
    idx = global_ayat_index(surat, ayat)
    juz = 1
    for j, start in enumerate(_JUZ_START_INDEX, start=1):
        if idx >= start:
            juz = j
    return juz


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
    reading_logs = db.relationship(
        "ReadingLog", backref="user", cascade="all, delete-orphan",
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @property
    def khatam_percent(self):
        # Berbobot jumlah ayat (lebih akurat daripada jumlah surat).
        read_ayat = sum(AYAT_COUNTS[r.surat_no] for r in self.surat_reads)
        return round(read_ayat / TOTAL_AYAT * 100, 1)

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
            "juz": juz_of(self.last_surat, self.last_ayat),
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class SuratRead(db.Model):
    __tablename__ = "surat_reads"
    __table_args__ = (db.UniqueConstraint("user_id", "surat_no"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    surat_no = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ReadingLog(db.Model):
    """Satu baris per hari saat pengguna membaca Al-Qur'an (untuk streak)."""
    __tablename__ = "reading_logs"
    __table_args__ = (db.UniqueConstraint("user_id", "log_date"),)

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    log_date = db.Column(db.Date, nullable=False, default=date.today)


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
