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


def verify_route(routes, departure_iata, arrival_iata, aircraft, airline_name):
    result = {
        'valid': False,
        'airline': airline_name,
        'aircraft': aircraft,
        'departure': departure_iata.upper(),
        'arrival': arrival_iata.upper(),
        'reason': '',
        'suggestions': []
    }
    
    matching_route = None
    departure_icao = None
    arrival_icao = None
    
    for route in routes:
        if route['from'] == departure_iata.upper() and route['to'] == arrival_iata.upper():
            matching_route = route
            departure_icao = route.get('from_icao', departure_iata.upper())
            arrival_icao = route.get('to_icao', arrival_iata.upper())
            break
        if route['from'] == departure_iata.upper() and not departure_icao:
            departure_icao = route.get('from_icao', departure_iata.upper())
    
    if not departure_icao:
        departure_icao = departure_iata.upper()
    if not arrival_icao:
        arrival_icao = arrival_iata.upper()
    
    if not matching_route:
        result['reason'] = f"No route found from {departure_icao} to {arrival_icao} for {airline_name}"
        
        departure_exists = any(r['from'] == departure_iata.upper() for r in routes)
        arrival_exists = any(r['to'] == arrival_iata.upper() for r in routes)
        
        if not departure_exists:
            result['suggestions'].append(f"{departure_icao} is not a departure airport for {airline_name}")
        else:
            possible_routes = [r for r in routes if r['from'] == departure_iata.upper()]
            if possible_routes:
                sample_size = min(5, len(possible_routes))
                sampled_routes = random.sample(possible_routes, sample_size)
                dest_details = []
                for route in sampled_routes:
                    to_icao = route.get('to_icao', route['to'])
                    time = route['estimated_time_min']
                    dest_details.append(f"{to_icao} (~{time}min)")
                
                dest_sample = ', '.join(dest_details)
                result['suggestions'].append(f"Possible destinations from {departure_icao}: {dest_sample}")
        
        if not arrival_exists:
            result['suggestions'].append(f"{arrival_icao} is not an arrival airport for {airline_name}")
        
        return result
    
    support_key = f"supports_{aircraft.lower()}"
    aircraft_supported = True
    aircraft_note = None
    
    if support_key in matching_route:
        if not matching_route[support_key]:
            aircraft_supported = False
            aircraft_note = f"{aircraft} may not be typically used on this route"
    
    result['valid'] = True
    result['route_info'] = {
        'from_name': matching_route['from_name'],
        'from_icao': matching_route.get('from_icao', ''),
        'to_name': matching_route['to_name'],
        'to_icao': matching_route.get('to_icao', ''),
        'distance_km': matching_route['distance_km'],
        'estimated_time_min': matching_route['estimated_time_min']
    }
    
    if not aircraft_supported and aircraft_note:
        result['aircraft_notes'] = aircraft_note
    
    return result
