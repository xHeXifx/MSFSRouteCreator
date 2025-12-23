import json
import os
from pathlib import Path

VALID_AIRLINES_FILE = "rawdata/ValidAirlines.json"
DATA_FOLDER = "data"

def sanitize_airline_name(name):
    return name.strip().lower().replace(' ', '_').replace('\r', '').replace('\n', '')

def get_existing_route_files():
    if not os.path.exists(DATA_FOLDER):
        return set()
    
    existing = set()
    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith('_routes.json'):
            airline_name = filename.replace('_routes.json', '')
            existing.add(airline_name)
    
    return existing

def main():
    print("=" * 70)
    print("Checking for Missing Airline Route Files")
    print("=" * 70)
    
    try:
        with open(VALID_AIRLINES_FILE, 'r', encoding='utf-8') as f:
            valid_airlines = json.load(f)
        print(f"\n Loaded {len(valid_airlines)} airlines from ValidAirlines.json")
    except Exception as e:
        print(f" Error loading ValidAirlines.json: {e}")
        return
    
    existing_routes = get_existing_route_files()
    print(f" Found {len(existing_routes)} route files in {DATA_FOLDER}/ folder")
    
    missing_airlines = []
    present_airlines = []
    
    for airline_name in valid_airlines:
        sanitized_name = sanitize_airline_name(airline_name)
        if sanitized_name in existing_routes:
            present_airlines.append(airline_name)
        else:
            missing_airlines.append(airline_name)
    
    print("\n" + "=" * 70)
    print(f"Present: {len(present_airlines)}/{len(valid_airlines)} airlines have route files")
    print(f"Missing: {len(missing_airlines)}/{len(valid_airlines)} airlines are missing route files")
    print("=" * 70)
    
    if missing_airlines:
        print(f"\n⚠️  Missing Route Files ({len(missing_airlines)} airlines):")
        print("-" * 70)
        for i, airline in enumerate(missing_airlines, 1):
            expected_filename = f"{sanitize_airline_name(airline)}_routes.json"
            print(f"{i:3}. {airline:50} -> {expected_filename}")
    
    if present_airlines:
        print(f"\n Airlines with Route Files ({len(present_airlines)} airlines):")
        print("-" * 70)
        for i, airline in enumerate(present_airlines, 1):
            filename = f"{sanitize_airline_name(airline)}_routes.json"
            print(f"{i:3}. {airline:50} -> {filename}")
    
    print("\n" + "=" * 70)
    coverage_pct = (len(present_airlines) / len(valid_airlines)) * 100 if valid_airlines else 0
    print(f"Coverage: {coverage_pct:.1f}% of valid airlines have route data")
    print("=" * 70)

if __name__ == "__main__":
    main()
