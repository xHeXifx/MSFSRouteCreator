import json
import os
import csv

_airline_files = None
_aircraft_support = None
_aircraft_data = None

def _load_airline_files():
    global _airline_files
    if _airline_files is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'airline_files.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            _airline_files = json.load(f)
    return _airline_files

def _load_aircraft_support():
    global _aircraft_support
    if _aircraft_support is None:
        support_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rawdata', 'aircraft_support.json')
        if os.path.exists(support_path):
            with open(support_path, 'r', encoding='utf-8') as f:
                _aircraft_support = json.load(f)
        else:
            _aircraft_support = {}
    return _aircraft_support

def _load_aircraft_data():
    global _aircraft_data
    if _aircraft_data is None:
        aircraft_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'rawdata', 'aircraft.dat')
        _aircraft_data = []
        if os.path.exists(aircraft_path):
            with open(aircraft_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) >= 3:
                        name = row[0].strip().strip('"')
                        iata = row[1].strip().strip('"')
                        icao = row[2].strip().strip('"')
                        if icao and icao != r'\N':
                            _aircraft_data.append({
                                'name': name,
                                'iata': iata if iata != r'\N' else '',
                                'icao': icao
                            })
    return _aircraft_data

AIRLINE_FILES = property(lambda self: _load_airline_files())

def get_airline_files():
    return _load_airline_files()

def get_all_aircraft():
    return _load_aircraft_data()

def get_airline_aircraft(airline_name):
    support_data = _load_aircraft_support()
    airline_data = support_data.get(airline_name, {})
    return airline_data.get('validAircraft', [])

def airline_supports_aircraft(airline_name, aircraft_code):
    valid_aircraft = get_airline_aircraft(airline_name)
    return aircraft_code in valid_aircraft


def load_routes(airline_name):
    airline_files = _load_airline_files()
    with open(airline_files[airline_name], "r", encoding="utf-8") as f:
        return json.load(f)["routes"]


def load_airline_data(airline_name):
    airline_files = _load_airline_files()
    with open(airline_files[airline_name], "r", encoding="utf-8") as f:
        return json.load(f)


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
