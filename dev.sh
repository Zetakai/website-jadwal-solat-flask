#!/usr/bin/env bash
# Jalankan aplikasi secara lokal (setup venv + deps + migrasi + server).
set -euo pipefail
cd "$(dirname "$0")"

VENV=venv

# 1. venv
if [ ! -d "$VENV" ]; then
    echo "==> Membuat virtual environment..."
    python3 -m venv "$VENV"
fi
# shellcheck disable=SC1090
source "$VENV/bin/activate"

# 2. dependencies
echo "==> Menginstall dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# 3. .env (buat dari contoh + generate SECRET_KEY bila belum ada)
if [ ! -f .env ]; then
    echo "==> Membuat .env dengan SECRET_KEY baru..."
    KEY=$(python -c "import secrets; print(secrets.token_hex(32))")
    printf 'SECRET_KEY=%s\nFLASK_CONFIG=development\n' "$KEY" > .env
fi

# 4. database (migrasi)
echo "==> Menjalankan migrasi database..."
export FLASK_APP=run.py
flask db upgrade

# 5. server
echo "==> Menjalankan server di http://127.0.0.1:5000"
python run.py
