"""Development entrypoint.

Run:  flask --app run run          (uses FLASK_DEBUG / .env)
  or:  python run.py
"""
from app import create_app

app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
