# CLI version
from InquirerPy import inquirer
import webbrowser
from core.route_loader import load_routes, build_airport_index, get_airport_choices, extract_iata, AIRLINE_FILES
from core.logic import generate_random_route, build_simbrief_url


def run_cli():
    while True:
        airline = inquirer.select(
            message="Select airline:",
            choices=list(AIRLINE_FILES.keys())
        ).execute()

        routes = load_routes(airline)
        airport_index = build_airport_index(routes)

        aircraft = inquirer.select(
            message="Select aircraft:",
            choices=["A320N", "A388"]
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

        route = generate_random_route(routes, origin_iata, aircraft, max_time)

        if not route:
            print("\n❌ No valid routes found with current filters.")
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
