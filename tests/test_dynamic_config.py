import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.logic import genFlightNum
from core.route_loader import get_airline_files, load_routes

print("=" * 60)
print("Testing Dynamic Configuration Loading")
print("=" * 60)

print("\n1. Testing airline files loading...")
try:
    airline_files = get_airline_files()
    print(f" Successfully loaded {len(airline_files)} airlines:")
    for airline in airline_files.keys():
        print(f"  - {airline}")
except Exception as e:
    print(f" Failed to load airline files: {e}")
    sys.exit(1)

print("\n2. Testing flight number generation...")
test_cases = [
    ("British Airways", "EGLL"),
    ("British Airways", "EGKK"),
    ("easyJet", "EGKK"),
    ("Emirates", "OMDB"),
    ("Lufthansa", "EDDF"),
    ("Singapore Airlines", "WSSS"),
    ("Qatar Airways", "OTHH"),
    ("Ryanair", "EGSS"),
]

for airline, icao in test_cases:
    try:
        result = genFlightNum(airline, icao)
        if isinstance(result, list) and len(result) == 2:
            prefix, flight_no = result
            print(f" {airline} from {icao}: {prefix}{flight_no}")
        else:
            print(f" {airline} from {icao}: Invalid result format")
    except Exception as e:
        print(f" {airline} from {icao}: {e}")

print("\n3. Testing default flight number ranges...")
default_test_cases = [
    ("British Airways", "KJFK"),
    ("easyJet", "LFPG"),
]

for airline, icao in default_test_cases:
    try:
        result = genFlightNum(airline, icao)
        if isinstance(result, list) and len(result) == 2:
            prefix, flight_no = result
            print(f" {airline} from {icao} (default): {prefix}{flight_no}")
        else:
            print(f" {airline} from {icao}: Invalid result format")
    except Exception as e:
        print(f" {airline} from {icao}: {e}")

print("\n4. Testing route loading...")
try:
    routes = load_routes("British Airways")
    print(f" Successfully loaded {len(routes)} routes for British Airways")
    if routes:
        sample = routes[0]
        print(f"  Sample route: {sample['from']} -> {sample['to']}")
except Exception as e:
    print(f" Failed to load routes: {e}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
