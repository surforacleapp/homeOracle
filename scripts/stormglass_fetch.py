#!/usr/bin/env python3
import os
import json
import requests
from datetime import datetime, timedelta

# ================================
# API Key (GitHub Secret)
# ================================
api_key = os.environ.get("STORMGLASS_API_KEY")
if not api_key:
    raise ValueError("API key StormGlass não encontrada! Configure o secret STORMGLASS_API_KEY no GitHub.")

HEADERS = {"Authorization": api_key}

# ================================
# Coordenadas dos spots
# ================================
SPOTS = {
    "nazare":         {"lat": 39.601, "lng": -9.071},
    "peniche":        {"lat": 39.363, "lng": -9.415},
    "ericeira":       {"lat": 38.966, "lng": -9.425},
    "lisboa":         {"lat": 38.646, "lng": -9.330},
    "cascais":        {"lat": 38.697, "lng": -9.423},
    "costa_caparica": {"lat": 38.642, "lng": -9.235},
    "sines":          {"lat": 37.851, "lng": -8.806},
}

# ================================
# Parâmetros StormGlass
# ================================
PARAMS_FORECAST = [
    "windSpeed", "windDirection",
    "swellHeight", "swellPeriod", "swellDirection",
    "secondarySwellHeight", "secondarySwellPeriod", "secondarySwellDirection",
    "waveHeight", "wavePeriod", "waveDirection",
    "windWaveHeight", "windWavePeriod", "windWaveDirection",
    "airTemperature", "waterTemperature",
    "cloudCover", "precipitation", "visibility"
]

# ================================
# Intervalo temporal (UTC)
# ================================
start = datetime.utcnow().isoformat() + "Z"
end   = (datetime.utcnow() + timedelta(days=5)).isoformat() + "Z"

# ================================
# Criar pasta docs/ se não existir
# ================================
os.makedirs("docs", exist_ok=True)

# ================================
# Loop por cada spot
# ================================
for name, spot in SPOTS.items():
    lat = spot["lat"]
    lng = spot["lng"]

    print(f"🌊 Obtendo forecast para {name}…")

    # --- Forecast (weather/point)
    forecast_url = (
        "https://api.stormglass.io/v2/weather/point"
        f"?lat={lat}&lng={lng}"
        f"&params={','.join(PARAMS_FORECAST)}"
        f"&start={start}&end={end}"
    )

    resp_forecast = requests.get(forecast_url, headers=HEADERS)
    resp_forecast.raise_for_status()
    forecast_data = resp_forecast.json().get("hours", [])

    # --- Tide extremes (tide/extremes/point)
    tide_url = "https://api.stormglass.io/v2/tide/extremes/point"
    tide_params = {"lat": lat, "lng": lng, "start": start, "end": end}

    resp_tide = requests.get(tide_url, headers=HEADERS, params=tide_params)
    resp_tide.raise_for_status()
    tide_data = resp_tide.json().get("data", [])

    # --- Estrutura final do JSON
    output = {
        "spot": name,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "forecast": forecast_data,
        "tide": tide_data
    }

    # --- Salvar arquivo
    file_path = f"docs/{name}.json"
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"✅ {file_path} atualizado")
