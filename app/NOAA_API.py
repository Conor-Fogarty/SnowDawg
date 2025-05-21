import requests
from flask import Flask, jsonify, request
from datetime import datetime

app = Flask(__name__)

# Sample coordinates for Northeast Ikon Pass mountains
RESORT_COORDINATES = {
    "Stratton": (43.11472, -72.90694),
    "Sugarbush": (44.1366, -72.9044),
    "Killington": (43.6267, -72.7962),
    "Sunday River": (44.4744, -70.8564),
    "Sugarloaf": (45.0311, -70.3139),
    "Loon": (44.0364, -71.6212),
    "Windham": (42.3002, -74.2525),
    "Jiminy Peak": (42.5567, -73.2906),
    "Cranmore": (44.0584, -71.1248)
}

def get_forecast_url(lat, lon):
    point_url = f"https://api.weather.gov/points/{lat},{lon}"
    r = requests.get(point_url)
    if r.status_code != 200:
        return None
    return r.json().get("properties", {}).get("forecast")

def get_forecast(forecast_url):
    r = requests.get(forecast_url)
    if r.status_code != 200:
        return None
    periods = r.json().get("properties", {}).get("periods", [])
    return periods

@app.route("/api/forecast/<resort>", methods=["GET"])
def forecast(resort):
    resort = resort.title()
    if resort not in RESORT_COORDINATES:
        return jsonify({"error": "Resort not found"}), 404
    lat, lon = RESORT_COORDINATES[resort]
    forecast_url = get_forecast_url(lat, lon)
    if not forecast_url:
        return jsonify({"error": "Could not get forecast URL"}), 500
    forecast_data = get_forecast(forecast_url)
    if not forecast_data:
        return jsonify({"error": "Could not retrieve forecast"}), 500
    return jsonify({"resort": resort, "forecast": forecast_data})

if __name__ == "__main__":
    app.run(debug=True)
