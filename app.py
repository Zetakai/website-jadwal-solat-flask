from flask import Flask, render_template, jsonify, request
import requests

app = Flask(__name__)

API_BASE = "https://equran.id"


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/provinces")
def get_provinces():
    try:
        response = requests.get(f"{API_BASE}/api/v2/shalat/provinsi")
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/cities", methods=["POST"])
def get_cities():
    province = request.json.get("provinsi")
    if not province:
        return jsonify({"error": "Provinsi diperlukan"}), 400

    try:
        response = requests.post(
            f"{API_BASE}/api/v2/shalat/kabkota",
            json={"provinsi": province}
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/schedule", methods=["POST"])
def get_schedule():
    data = request.json
    provinsi = data.get("provinsi")
    kabkota = data.get("kabkota")
    bulan = data.get("bulan")
    tahun = data.get("tahun")

    if not provinsi or not kabkota:
        return jsonify({"error": "Provinsi dan kabkota diperlukan"}), 400

    payload = {"provinsi": provinsi, "kabkota": kabkota}
    if bulan:
        payload["bulan"] = bulan
    if tahun:
        payload["tahun"] = tahun

    try:
        response = requests.post(
            f"{API_BASE}/api/v2/shalat",
            json=payload
        )
        return jsonify(response.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
