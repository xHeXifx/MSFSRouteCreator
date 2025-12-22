import json
import csv
from math import ceil

# -----------------------------
# Config
# -----------------------------

INPUT_FILE = "rawdata/airline_routes.json"
AIRPORTS_CSV = "rawdata/airports.csv"

OUTPUT_BA = "data/british_airways_routes.json"
OUTPUT_EZY = "data/easyjet_routes.json"

CRUISE_SPEED_KTS = 290
CRUISE_SPEED_KMH = CRUISE_SPEED_KTS * 1.852

MAX_A320_RANGE_KM = 4800
MIN_A380_RANGE_KM = 5500

A380_AIRPORTS = {
    "LHR", "JFK", "LAX", "SFO", "MIA", "IAD", "BOS",
    "DXB", "SIN", "HKG", "SYD", "MEL",
    "JNB", "NRT", "HND", "ICN", "DOH"
}

# -----------------------------
# Helpers
# -----------------------------

def estimate_time_minutes(distance_km: float) -> int:
    hours = distance_km / CRUISE_SPEED_KMH
    return ceil(hours * 60)

def split_time(minutes: int) -> dict | None:
    if minutes < 60:
        return None
    return {
        "hours": minutes // 60,
        "minutes": minutes % 60
    }

def supports_a320(distance_km: float) -> bool:
    return distance_km <= MAX_A320_RANGE_KM

def supports_a380(origin: str, dest: str, distance_km: float) -> bool:
    return (
        distance_km >= MIN_A380_RANGE_KM and
        origin in A380_AIRPORTS and
        dest in A380_AIRPORTS
    )

# -----------------------------
# Load airport mapping
# -----------------------------

iata_to_icao = {}
with open(AIRPORTS_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        iata = row.get("iata_code")
        icao = row.get("icao_code")
        if iata and icao:
            iata_to_icao[iata] = icao

# -----------------------------
# Load routes
# -----------------------------

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

ba_routes = []
ezy_routes = []

# -----------------------------
# Process routes
# -----------------------------

for origin_iata, origin_data in data.items():
    origin_name = origin_data.get("name", origin_iata)
    origin_icao = iata_to_icao.get(origin_iata, "")

    for route in origin_data.get("routes", []):
        dest_iata = route["iata"]
        dest_data = data.get(dest_iata, {})
        dest_name = dest_data.get("name", dest_iata)
        dest_icao = iata_to_icao.get(dest_iata, "")

        distance_km = route["km"]
        carriers = {c["iata"] for c in route.get("carriers", [])}

        time_min = estimate_time_minutes(distance_km)
        time_split = split_time(time_min)

        base_entry = {
            "from": origin_iata,
            "from_name": origin_name,
            "from_icao": origin_icao,
            "to": dest_iata,
            "to_name": dest_name,
            "to_icao": dest_icao,
            "distance_km": distance_km,
            "estimated_time_min": time_min
        }

        if time_split:
            base_entry["estimated_time"] = time_split

        # British Airways
        if "BA" in carriers:
            ba_routes.append({
                **base_entry,
                "supports_a320": supports_a320(distance_km),
                "supports_a380": supports_a380(origin_iata, dest_iata, distance_km)
            })

        # easyJet
        if "U2" in carriers:
            ezy_routes.append({
                **base_entry,
                "supports_a320": supports_a320(distance_km),
                "supports_a380": False
            })

# -----------------------------
# Write output
# -----------------------------

with open(OUTPUT_BA, "w", encoding="utf-8") as f:
    json.dump({
        "airline": "British Airways",
        "iata": "BA",
        "icao": "BAW",
        "routes": ba_routes
    }, f, indent=2)

with open(OUTPUT_EZY, "w", encoding="utf-8") as f:
    json.dump({
        "airline": "easyJet",
        "iata": "U2",
        "icao": "EZY",
        "routes": ezy_routes
    }, f, indent=2)
