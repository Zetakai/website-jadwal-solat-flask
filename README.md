# Jadwal Shalat

Aplikasi web jadwal shalat Indonesia menggunakan Flask dan API dari [equran.id](https://equran.id).

## Fitur

- Pilihan provinsi dan kabupaten/kota
- Jadwal shalat harian otomatis sesuai tanggal hari ini
- UI modern dengan tema hijau Islami
- Responsive design

## Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript
- **API**: [equran.id](https://equran.id/apidev/shalat)

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
│   └── index.html      # Frontend HTML/CSS/JS
├── .gitignore
└── README.md
```
