import json
import random
from InquirerPy import inquirer
import webbrowser
import sys

# config

AIRLINE_FILES = {
    "British Airways": "data/british_airways_routes.json",
    "easyJet": "data/easyjet_routes.json"
}

# load json

def load_routes(airline_name):
    with open(AIRLINE_FILES[airline_name], "r", encoding="utf-8") as f:
        return json.load(f)["routes"]

# helpers

def build_airport_index(routes):
    airports = {}
    for r in routes:
        airports[r["from"]] = f"{r['from_name']} ({r.get('from_icao','')})"
        airports[r["to"]] = f"{r['to_name']} ({r.get('to_icao','')})"
    return airports

def airport_choices(airport_index):
    return [
        f"{code} — {name}"
        for code, name in sorted(airport_index.items())
    ]

def extract_iata(choice):
    return choice.split(" — ")[0]

def genFlightNum(airline, departure_icao):
    
    airline = airline.strip().lower()
    departure_icao = departure_icao.strip().upper()

    if airline == 'british airways':
        prefix = "BAW"
        if departure_icao == 'EGLL': # Heathrow
            flight_no = random.randint(1, 999)
        elif departure_icao == 'EGKK': # Gatwick
            flight_no = random.randint(2000, 2899)
        elif departure_icao in ['EGLC', 'EGHQ']:
            flight_no = random.randint(3000, 4500)
        else:
            flight_no = random.randint(1300, 1499)

    elif airline == 'easyjet':
        prefix = "EZY"
        if departure_icao == 'EGKK': # Gatwick
            flight_no = random.choice([random.randint(6000, 6999), random.randint(8000, 8999)])
        elif departure_icao == 'EGGW': # Luton
            flight_no = random.randint(1, 1999)
        elif departure_icao == 'EGSS': # Stansted
            flight_no = random.randint(3000, 3999)
        else:
            flight_no = random.randint(7000, 7999)
    
    else:
        return "Unknown Airline"

    return [prefix, flight_no]


# main
def main():
    while True:
        airline = inquirer.select(
            message="Select airline:",
            choices=list(AIRLINE_FILES.keys())
        ).execute()

        routes = load_routes(airline)
        airport_index = build_airport_index(routes)

        aircraft = inquirer.select(
            message="Select aircraft:",
            choices=["A20N", "A388"]
        ).execute()

        origin_choice = inquirer.fuzzy(
            message="Select departure airport:",
            choices=airport_choices(airport_index),
            max_height="70%"
        ).execute()

        origin_iata = extract_iata(origin_choice)

        max_time = inquirer.text(
            message="Maximum flight time in minutes (leave blank for no limit):",
            validate=lambda x: x.isdigit() or x == ""
        ).execute()
        max_time = int(max_time) if max_time else None

        # filter

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

        if not filtered:
            print("\n❌ No valid routes found with current filters.")
            return

        route = random.choice(filtered)

        # ----------------------------------------

        print("\n✈️  Random Route Found\n")
        print(f" Airline:   {airline}")
        print(f" Aircraft:  {aircraft}")
        print(f" From:      {route['from']} — {route['from_name']} ({route.get('from_icao','')})")
        print(f" To:        {route['to']} — {route['to_name']} ({route.get('to_icao','')})")
        print(f" Distance:  {route['distance_km']} km")

        if "estimated_time" in route:
            t = route["estimated_time"]
            print(f" Time:      {t['hours']}h {t['minutes']}m")
        else:
            print(f" Time:      {route['estimated_time_min']} min")

        simbriefQ = inquirer.select(
            message='Start plan in Simbrief Dispatch?',
            choices=["Yes", "No (Generate Again)", "No"]
            ).execute()
        
        if simbriefQ == "Yes":
            flightIdentDetails = genFlightNum(airline, route.get('from_icao'))

            builtURL = (
                "https://dispatch.simbrief.com/options/custom?"
                f"airline={flightIdentDetails[0]}&"
                f"fltnum={flightIdentDetails[1]}&"
                f"type={aircraft}&"
                f"orig={route.get('from_icao')}&"
                f"dest={route.get('to_icao')}&"
                "altn_count=0"
            )
            webbrowser.open(builtURL)
            break
        elif simbriefQ == "No (Generate Again)":
            continue
        else:
            break


if __name__ == "__main__":
    main()
