# Jadwal Shalat

Aplikasi web Islami menggunakan Flask dan API dari [equran.id](https://equran.id) untuk menampilkan jadwal shalat, kumpulan doa, dan bacaan Al-Qur'an.

## Nama Kelompok

- Nama kelompok: Kelompok 3 
- Anggota:
  - Muhammad Farid Zaki (1003240010)
  - Badrudin (1003240051)
  - Ratih Zahra Nur Aulia (1003240046)


## Tema Website

Tema website ini adalah layanan Islami digital. Website menyediakan informasi ibadah harian seperti jadwal shalat berdasarkan wilayah Indonesia, kumpulan doa harian, dan bacaan Al-Qur'an digital.

## API yang Digunakan

Website ini menggunakan API dari [equran.id](https://equran.id). Semua request dari frontend diarahkan ke endpoint lokal Flask (blueprint `app/blueprints/api.py`), lalu backend meneruskan request ke API equran.id. Peta masjid memakai [OpenStreetMap](https://www.openstreetmap.org) via Overpass API (tanpa API key).

Endpoint lokal yang digunakan frontend:

- `/api/provinces` untuk mengambil daftar provinsi
- `/api/cities` untuk mengambil daftar kabupaten/kota berdasarkan provinsi
- `/api/schedule` untuk mengambil jadwal shalat
- `/api/doa` untuk mengambil kumpulan doa
- `/api/surat` untuk mengambil daftar surat Al-Qur'an
- `/api/surat/{nomor}` untuk mengambil detail ayat dalam surat

Endpoint equran.id yang dipanggil oleh backend:

- `https://equran.id/api/v2/shalat/provinsi` untuk mengambil daftar provinsi
- `https://equran.id/api/v2/shalat/kabkota` untuk mengambil daftar kabupaten/kota berdasarkan provinsi
- `https://equran.id/api/v2/shalat` untuk mengambil jadwal shalat
- `https://equran.id/api/doa` untuk mengambil kumpulan doa
- `https://equran.id/api/v2/surat` untuk mengambil daftar surat Al-Qur'an
- `https://equran.id/api/v2/surat/{nomor}` untuk mengambil detail ayat dalam surat

## Fitur

**Publik (tanpa login):**
- Jadwal shalat harian per provinsi/kabupaten
- Kumpulan doa harian dengan pencarian dan kategori
- Al-Qur'an digital (Arab, latin, terjemahan) + filter surat pendek
- Halaman **Peta** dengan dua mode:
  - **Masjid** — peta masjid sekitar (OpenStreetMap/Overpass) + daftar jarak
  - **Kiblat** — kompas arah kiblat + garis great-circle ke Ka'bah di peta
- Lokasi bisa via GPS, pencarian tempat (Nominatim), seret penanda, atau klik peta

**Perlu login (data per pengguna):**
- Simpan lokasi favorit → jadwal termuat otomatis
- Progres baca Al-Qur'an: auto-track saat menggulir + tombol tandai manual,
  lanjut-otomatis (resume), persen khatam berbobot ayat, posisi juz, streak baca
- Tasbih/zikir digital + kalender riwayat harian
- Ceklis shalat lima waktu + **kalender bulanan** (tandai shalat terlewat)
- **Streak, statistik & lencana** (gamifikasi) di halaman profil
- Home: **hitung mundur shalat berikutnya** + sorot waktu sekarang + **tanggal Hijriah**

**Penanganan error:** handler kustom 404/403/500 → halaman error ramah
pengguna (`templates/error.html`) untuk halaman, respons JSON untuk path `/api`.

UI modern tema hijau Islami, responsif — mode mobile (bottom nav) & desktop (top nav).
Tanggal Hijriah pakai kalender Islam bawaan browser (`Intl`), tanpa API eksternal.

## Penjelasan Fitur

1. **Jadwal Shalat** — pilih provinsi/kota, tampil jadwal hari ini. Pengguna login dapat menyimpan lokasi agar termuat otomatis.

2. **Kumpulan Doa** — daftar doa dari equran.id dengan pencarian, kategori, dan detail (Arab/latin/terjemahan).

3. **Al-Qur'an Digital** — daftar surat + pencarian & filter surat pendek. Pengguna login: simpan posisi baca terakhir dan tandai surat khatam (progres persen).

4. **Peta (Masjid & Kiblat)** — satu halaman, dua mode. Masjid: cari masjid di radius 3 km. Kiblat: kompas sensor perangkat + garis kiblat ke Ka'bah.

5. **Zikir** — tasbih digital, hitungan tersimpan per hari.

6. **Ceklis Shalat** — centang 5 waktu; kalender menandai hari lengkap/sebagian/terlewat, bisa mundur ke tanggal lampau.

7. **Akun** — daftar/masuk (email + kata sandi), halaman profil merangkum progres.

8. **Responsif** — layout menyesuaikan mobile dan desktop.

## Tech Stack

- **Backend**: Flask (application factory + blueprints)
- **Database**: SQLAlchemy (SQLite default, siap Postgres) + Flask-Migrate
- **Auth**: Flask-Login + Werkzeug password hashing, Flask-WTF (CSRF)
- **Frontend**: HTML, CSS, JavaScript (tanpa build step)
- **Peta**: Leaflet + OpenStreetMap (tiles, Overpass masjid, Nominatim pencarian)
- **API eksternal**: [equran.id](https://equran.id)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: .\venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # isi SECRET_KEY (wajib)

flask --app run db upgrade          # buat/migrasi database
flask --app run run                 # atau: python run.py
```

Buka browser di `http://127.0.0.1:5000`.

> Fitur kiblat & peta masjid butuh izin lokasi/sensor browser dan idealnya
> diakses via HTTPS (atau `localhost`).

## API Lokal

Proxy publik (`app/blueprints/api.py`): `/api/provinces`, `/api/cities`,
`/api/schedule`, `/api/doa`, `/api/surat`, `/api/surat/<nomor>`.

Fitur per-pengguna, perlu login (`app/blueprints/tracker.py`, prefix `/api/me`).

**Pemetaan operasi CRUD → HTTP method:**

| CRUD | Operasi | HTTP Method |
|------|---------|-------------|
| **C**reate | Tambah data baru | `POST` |
| **R**ead | Baca / ambil data | `GET` |
| **U**pdate | Ubah data | `PUT` |
| **D**elete | Hapus / reset data | `DELETE` |

**Operasi CRUD per resource** (✓ = didukung):

| Resource | Endpoint dasar | C `POST` | R `GET` | U `PUT` | D `DELETE` |
|----------|----------------|:---:|:---:|:---:|:---:|
| Lokasi | `/location` | — | ✓ | ✓ | ✓ |
| Progres Qur'an | `/quran/progress` | — | ✓ | ✓ | — |
| Khatam surat | `/quran/reads/<no>` | ✓ | — | — | ✓ |
| Zikir | `/zikir`, `/zikir/<key>` | ✓ | ✓ | — | ✓ |
| Ceklis shalat | `/prayer` | — | ✓ | ✓ | — |

Endpoint baca tambahan (Read): `GET /zikir/history`, `GET /prayer/history`,
`GET /stats` (streak, statistik, lencana) — semua menerima `?year=&month=` bila relevan.

## Struktur Proyek

```
├── run.py                  # entrypoint (create_app)
├── requirements.txt
├── .env.example
├── migrations/             # Alembic (Flask-Migrate)
├── app/
│   ├── __init__.py         # application factory
│   ├── config.py           # konfigurasi via environment
│   ├── extensions.py       # db, login_manager, migrate, csrf
│   ├── models.py           # User, QuranProgress, SuratRead, ZikirLog, PrayerLog
│   ├── forms.py            # form login/daftar (WTForms)
│   └── blueprints/
│       ├── main.py         # halaman
│       ├── auth.py         # daftar/masuk/keluar
│       ├── api.py          # proxy equran.id (publik)
│       └── tracker.py      # fitur per-pengguna (perlu login)
├── templates/              # base, index, doa, surat, detail_surat, zikir,
│                           #   ibadah, masjid (peta+kiblat), profile, error, auth/
├── .gitignore
└── README.md
```
