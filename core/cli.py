# CLI version
from InquirerPy import inquirer
import webbrowser
from core.route_loader import load_routes, build_airport_index, get_airport_choices, extract_iata, get_airline_files, get_all_aircraft, get_airline_aircraft
from core.logic import generate_random_route, build_simbrief_url


def run_cli():
    while True:
        airline = inquirer.fuzzy(
            message="Select airline:",
            choices=list(get_airline_files().keys())
        ).execute()

        routes = load_routes(airline)
        airport_index = build_airport_index(routes)

        airline_aircraft = get_airline_aircraft(airline)
        all_aircraft = get_all_aircraft()
        
        if airline_aircraft:
            aircraft_choices = [ac['icao'] for ac in all_aircraft if ac['icao'] in airline_aircraft]
        else:
            aircraft_choices = [ac['icao'] for ac in all_aircraft]
        
        if not aircraft_choices:
            aircraft_choices = ["A320N", "A388"]
        aircraft = inquirer.select(
            message="Select aircraft:",
            choices=aircraft_choices
        ).execute()

        origin_choice = inquirer.fuzzy(
            message="Select departure airport:",
            choices=get_airport_choices(airport_index),
            max_height="70%"
        ).execute()

        origin_iata = extract_iata(origin_choice)

        max_time = inquirer.text(
            message="Maximum flight time in minutes (leave blank for no limit):",
            validate=lambda x: x.isdigit() or x == ""
        ).execute()
        max_time = int(max_time) if max_time else None

        route = generate_random_route(routes, origin_iata, aircraft, airline, max_time)

        if not route:
            print("\nNo valid routes found with current filters.")
            return

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

        simbrief_q = inquirer.select(
            message='Start plan in Simbrief Dispatch?',
            choices=["Yes", "No (Generate Again)", "No"]
        ).execute()

        if simbrief_q == "Yes":
            built_url = build_simbrief_url(airline, aircraft, route)
            webbrowser.open(built_url)
            break
        elif simbrief_q == "No (Generate Again)":
            continue
        else:
            break
