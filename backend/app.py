import json
import os
import re
from datetime import datetime
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS
from scraper import scrape_inmobiliaria
from excel_generator import generate_excel
from html_generator import generate_html

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*", "methods": ["GET", "POST", "OPTIONS"], "allow_headers": ["Content-Type"]}})

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TARGET_FILE = os.path.join(BASE_DIR, "target.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output")

os.makedirs(OUTPUT_DIR, exist_ok=True)


@app.route("/api/targets", methods=["GET"])
def get_targets():
    with open(TARGET_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify(data)


@app.route("/api/scrape", methods=["POST"])
def scrape():
    body = request.get_json()
    nombre = body.get("nombre")
    web = body.get("web")
    regiones = body.get("regiones", [])
    precio_max = body.get("precio_max")
    if precio_max:
        try:
            precio_max = int(precio_max)
        except (ValueError, TypeError):
            precio_max = None

    if not nombre or not web:
        return jsonify({"error": "Faltan parámetros nombre o web"}), 400

    try:
        resultados = scrape_inmobiliaria(nombre, web, regiones, precio_max=precio_max)

        if not resultados:
            return jsonify({"error": f"No se encontraron resultados para {nombre}"}), 404

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_name = re.sub(r'[^\w]', '_', nombre)

        xlsx_filename = f"{safe_name}_{timestamp}.xlsx"
        html_filename = f"{safe_name}_{timestamp}.html"
        xlsx_path = os.path.join(OUTPUT_DIR, xlsx_filename)
        html_path = os.path.join(OUTPUT_DIR, html_filename)

        generate_excel(resultados, xlsx_path, nombre)
        generate_html(resultados, html_path, nombre)

        return jsonify({
            "message": f"Se encontraron {len(resultados)} propiedades",
            "xlsx_filename": xlsx_filename,
            "html_filename": html_filename,
            "count": len(resultados)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/download/<filename>", methods=["GET"])
def download(filename):
    filepath = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "Archivo no encontrado"}), 404
    return send_file(filepath, as_attachment=True, download_name=filename)


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
