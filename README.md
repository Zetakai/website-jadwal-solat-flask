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

Website ini menggunakan API dari [equran.id](https://equran.id). Semua request dari frontend diarahkan ke endpoint lokal Flask di `app.py`, lalu backend meneruskan request ke API equran.id.

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

- Pilihan provinsi dan kabupaten/kota
- Jadwal shalat harian otomatis sesuai tanggal hari ini
- Daftar doa harian dengan pencarian dan kategori
- Daftar surat Al-Qur'an dengan fitur pencarian
- Filter surat pendek
- Detail surat berisi ayat Arab, latin, dan terjemahan Indonesia
- UI modern dengan tema hijau Islami
- Responsive design

## Penjelasan Fitur

1. **Jadwal Shalat**
   Pengguna dapat memilih provinsi dan kabupaten/kota, lalu website akan menampilkan jadwal shalat hari ini untuk lokasi tersebut.

2. **Kumpulan Doa**
   Website menampilkan daftar doa dari API equran.id. Pengguna dapat mencari doa berdasarkan kata kunci, memilih kategori doa, membuka detail doa, dan melihat teks Arab, latin, serta terjemahannya.

3. **Al-Qur'an Digital**
   Website menyediakan daftar surat Al-Qur'an. Pengguna dapat mencari surat berdasarkan nama atau arti, memfilter surat pendek, dan membuka detail surat untuk membaca ayat Arab, latin, serta terjemahan Indonesia.

4. **Tampilan Responsif**
   Antarmuka dibuat responsif sehingga dapat digunakan pada layar desktop maupun perangkat mobile.

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **API eksternal**: [equran.id](https://equran.id)
- **API lokal**: Route Flask di `app.py`

## Setup

```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate  # Linux/Mac
# atau
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Jalankan aplikasi
python app.py
```

Buka browser di `http://127.0.0.1:5000`

## Project Structure

```
├── app.py              # Flask backend
├── requirements.txt    # Python dependencies
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── doa.html
│   ├── surat.html
│   └── detail_surat.html
├── .gitignore
└── README.md
```
