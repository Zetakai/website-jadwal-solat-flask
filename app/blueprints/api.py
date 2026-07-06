"""Proxy API publik ke layanan equran.id (base URL & timeout di sisi server)."""
import requests
from flask import Blueprint, jsonify, request, current_app

api_bp = Blueprint("api", __name__, url_prefix="/api")


def _base():
    return current_app.config["EQURAN_API_BASE"]


def _timeout():
    return current_app.config["REQUEST_TIMEOUT"]


def _proxy(method, path, **kwargs):
    """Teruskan permintaan ke upstream dan seragamkan penanganan error."""
    try:
        resp = requests.request(method, f"{_base()}{path}", timeout=_timeout(), **kwargs)
        return jsonify(resp.json()), resp.status_code
    except requests.Timeout:
        return jsonify({"error": "Permintaan ke server sumber melebihi batas waktu."}), 504
    except requests.RequestException as exc:
        current_app.logger.warning("Upstream request failed: %s", exc)
        return jsonify({"error": "Gagal menghubungi server sumber."}), 502
    except ValueError:
        return jsonify({"error": "Respons dari server sumber tidak valid."}), 502


@api_bp.get("/provinces")
def get_provinces():
    return _proxy("GET", "/api/v2/shalat/provinsi")


@api_bp.post("/cities")
def get_cities():
    province = (request.json or {}).get("provinsi")
    if not province:
        return jsonify({"error": "Provinsi diperlukan"}), 400
    return _proxy("POST", "/api/v2/shalat/kabkota", json={"provinsi": province})


@api_bp.post("/schedule")
def get_schedule():
    data = request.json or {}
    provinsi, kabkota = data.get("provinsi"), data.get("kabkota")
    if not provinsi or not kabkota:
        return jsonify({"error": "Provinsi dan kabkota diperlukan"}), 400

    payload = {"provinsi": provinsi, "kabkota": kabkota}
    for key in ("bulan", "tahun"):
        if data.get(key):
            payload[key] = data[key]
    return _proxy("POST", "/api/v2/shalat", json=payload)


@api_bp.get("/doa")
def get_doa():
    return _proxy("GET", "/api/doa")


@api_bp.get("/surat")
def get_surat():
    return _proxy("GET", "/api/v2/surat")


@api_bp.get("/surat/<int:nomor>")
def get_detail_surat(nomor):
    return _proxy("GET", f"/api/v2/surat/{nomor}")
