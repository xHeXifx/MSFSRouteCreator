import random
import json
import os
from core.route_loader import airline_supports_aircraft

_flight_number_config = None

def _load_flight_number_config():
    global _flight_number_config
    if _flight_number_config is None:
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'flight_numbers.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            _flight_number_config = json.load(f)
    return _flight_number_config


def genFlightNum(airline, departure_icao):
    airline = airline.strip().lower()
    departure_icao = departure_icao.strip().upper()
    
    config = _load_flight_number_config()

    if airline not in config:
        return "Unknown Airline"
    
    airline_config = config[airline]
    prefix = airline_config["prefix"]
    
    if departure_icao in airline_config["icao_ranges"]:
        range_data = airline_config["icao_ranges"][departure_icao]
        
        if isinstance(range_data[0], list):
            selected_range = random.choice(range_data)
            flight_no = random.randint(selected_range[0], selected_range[1])
        else:
            flight_no = random.randint(range_data[0], range_data[1])
    else:
        default_range = airline_config["default_range"]
        flight_no = random.randint(default_range[0], default_range[1])
    
    return [prefix, flight_no]


def filter_routes(routes, origin_iata, aircraft, airline_name, max_time=None):
    filtered = []

    for r in routes:
        if r["from"] != origin_iata:
            continue

        support_key = f"supports_{aircraft.lower()}"
        if support_key in r and not r[support_key]:
            continue

        if max_time and r["estimated_time_min"] > max_time:
            continue

        filtered.append(r)

    return filtered


def generate_random_route(routes, origin_iata, aircraft, airline_name, max_time=None):
    filtered = filter_routes(routes, origin_iata, aircraft, airline_name, max_time)
    
    if not filtered:
        return None
    
    return random.choice(filtered)


def build_simbrief_url(airline, aircraft, route):
    flight_ident_details = genFlightNum(airline, route.get('from_icao'))
    
    url = (
        "https://dispatch.simbrief.com/options/custom?"
        f"airline={flight_ident_details[0]}&"
        f"fltnum={flight_ident_details[1]}&"
        f"type={aircraft}&"
        f"orig={route.get('from_icao')}&"
        f"dest={route.get('to_icao')}&"
        "altn_count=0"
    )
    return url


def format_route_details(airline, aircraft, route):
    time_str = ""
    if "estimated_time" in route:
        t = route["estimated_time"]
        time_str = f"{t['hours']}h {t['minutes']}m"
    else:
        time_str = f"{route['estimated_time_min']} min"
    
    return {
        "airline": airline,
        "aircraft": aircraft,
        "from_code": route['from'],
        "from_name": route['from_name'],
        "from_icao": route.get('from_icao', ''),
        "to_code": route['to'],
        "to_name": route['to_name'],
        "to_icao": route.get('to_icao', ''),
        "distance": f"{route['distance_km']} km",
        "time": time_str
    }
