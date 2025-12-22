import random


def genFlightNum(airline, departure_icao):
    airline = airline.strip().lower()
    departure_icao = departure_icao.strip().upper()

    if airline == 'british airways':
        prefix = "BAW"
        if departure_icao == 'EGLL':  # Heathrow
            flight_no = random.randint(1, 999)
        elif departure_icao == 'EGKK':  # Gatwick
            flight_no = random.randint(2000, 2899)
        elif departure_icao in ['EGLC', 'EGHQ']:
            flight_no = random.randint(3000, 4500)
        else:
            flight_no = random.randint(1300, 1499)

    elif airline == 'easyjet':
        prefix = "EZY"
        if departure_icao == 'EGKK':  # Gatwick
            flight_no = random.choice([random.randint(6000, 6999), random.randint(8000, 8999)])
        elif departure_icao == 'EGGW':  # Luton
            flight_no = random.randint(1, 1999)
        elif departure_icao == 'EGSS':  # Stansted
            flight_no = random.randint(3000, 3999)
        else:
            flight_no = random.randint(7000, 7999)
    else:
        return "Unknown Airline"

    return [prefix, flight_no]


def filter_routes(routes, origin_iata, aircraft, max_time=None):
    filtered = []

    for r in routes:
        if r["from"] != origin_iata:
            continue

        if aircraft == "A320N" and not r["supports_a320"]:
            continue

        if aircraft == "A388" and not r["supports_a380"]:
            continue

        if max_time and r["estimated_time_min"] > max_time:
            continue

        filtered.append(r)

    return filtered


def generate_random_route(routes, origin_iata, aircraft, max_time=None):
    filtered = filter_routes(routes, origin_iata, aircraft, max_time)
    
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
