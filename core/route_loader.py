import json

AIRLINE_FILES = {
    "British Airways": "data/british_airways_routes.json",
    "easyJet": "data/easyjet_routes.json",
    "Ryanair": "data/ryanair_routes.json",
    "Emirates": "data/emirates_routes.json",
    "Lufthansa": 'data/lufthansa_routes.json',
    "Singapore Airlines": "data/singapore_airlines_routes.json",
    "Qatar Airways": 'data/qatar_airways_routes.json'
}


def load_routes(airline_name):
    with open(AIRLINE_FILES[airline_name], "r", encoding="utf-8") as f:
        return json.load(f)["routes"]


def build_airport_index(routes):
    airports = {}
    for r in routes:
        airports[r["from"]] = f"{r['from_name']} ({r.get('from_icao','')})"
        airports[r["to"]] = f"{r['to_name']} ({r.get('to_icao','')})"
    return airports


def get_airport_choices(airport_index):
    return [
        f"{code} — {name}"
        for code, name in sorted(airport_index.items())
    ]


def extract_iata(choice):
    return choice.split(" — ")[0]
