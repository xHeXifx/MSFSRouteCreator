import json
import csv
import os
import requests
import re
import logging
import argparse
from math import ceil
from datetime import datetime
from pathlib import Path

parser = argparse.ArgumentParser(description='Build airline route data and configurations')
parser.add_argument('-nomedia', '--no-media', action='store_true',
                    help='Skip downloading logos from GitHub')
parser.add_argument('-verify', '--verify', action='store_true',
                    help='Verify route coverage and exit')
parser.add_argument('-fixmedia', '--fix-media', action='store_true',
                    help='Attempts to find missing media for present routes.')
args = parser.parse_args()


os.makedirs("logs", exist_ok=True)
log_filename = f"logs/buildData_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

#region config

INPUT_FILE = "rawdata/airline_routes.json"
AIRPORTS_CSV = "rawdata/airports.csv"
VALID_AIRLINES_FILE = "rawdata/ValidAirlines.json"
AIRLINES_DATABASE_FILE = "rawdata/airlines.json"

CONFIG_FLIGHT_NUMBERS = "config/flight_numbers.json"
CONFIG_AIRLINE_FILES = "config/airline_files.json"
CONFIG_AIRLINE_LOGOS = "config/airline_logos.json"

DEFAULT_FLIGHT_NUMBER_RANGE = [1000, 9999]

CRUISE_SPEED_KTS = {
    "A21N": 470, "A30B": 470, "A310": 470, "A318": 470, "A319": 470, "A320": 470, "A321": 470,
    "A332": 490, "A342": 490, "A359": 470, "A35K": 470, "A388": 510,
    "AN12": 400, "B37M": 480, "B712": 840, "B721": 880, "B752": 830, "B762": 840,
    "B772": 905, "B78X": 905, "BCS1": 460, "BCS3": 460, "BLCF": 460, "CONC": 2175,
    "DC10": 890, "DHC6": 160, "L101": 800, "MD11": 890, "MD90": 840, "SB20": 160,
    "SU95": 860, "T134": 850, "T204": 280, "YK42": 600
}

CRUISE_SPEED_KMH = {k: v * 1.852 for k, v in CRUISE_SPEED_KTS.items()}

MAX_RANGE_KM = {
    "A21N": 7400, "A30B": 7400, "A310": 9600, "A318": 5700, "A319": 6700, "A320": 6100, "A321": 7400,
    "A332": 13450, "A342": 15700, "A359": 8100, "A35K": 8300, "A388": 15200,
    "AN12": 3800, "B37M": 1500, "B712": 9000, "B721": 6100, "B752": 9350, "B762": 10400,
    "B772": 13900, "B78X": 15700, "BCS1": 3100, "BCS3": 4600, "BLCF": 4700, "CONC": 7250,
    "DC10": 6800, "DHC6": 900, "L101": 4400, "MD11": 12000, "MD90": 3700, "SB20": 700,
    "SU95": 3600, "T134": 5400, "T204": 1600, "YK42": 2500
}

MIN_RANGE_KM = {
    # Airbus widebodies
    "A310": 1800,
    "A332": 2500,
    "A342": 3000,
    "A359": 2800,
    "A35K": 3200,
    "A388": 4000,

    # Boeing widebodies
    "B762": 2200,
    "B772": 3000,
    "B78X": 3500,
    "BLCF": 3500,

    # Classics
    "DC10": 2500,
    "L101": 2200,
    "MD11": 2800,

    # Supersonic
    "CONC": 3000,

    # Heavy military / cargo
    "AN12": 800,
}

MAJOR_AIRPORTS = {
    "A35K": {"CDG", "LHR", "JFK", "ORD", "HND", "SIN"},
    "A388": {"LHR", "JFK", "LAX", "DXB", "SIN", "SYD"},
    "B772": {"LHR", "JFK", "LAX", "DXB", "SIN"},
    "B78X": {"LHR", "JFK", "LAX", "DXB", "SIN", "SYD"},
    "CONC": {"LHR", "JFK"},
    "MD11": {"FRA", "JFK", "LAX", "AMS"},
    "B752": {"LHR", "JFK", "LAX", "ORD"},
    "DHC6": {"YVR", "YYC", "SEA", "ANC"},
    "SB20": {"LED", "MSQ", "KBP"},
    "T204": {"VKO", "LED"}
}

LOGO_REPO_URL = "https://raw.githubusercontent.com/Jxck-S/airline-logos/refs/heads/main/avcodes_banners/{icao}.png"
HEADERS = {"User-Agent": "MSFSRouteCreator/1.0 (contact: @hexif)"}
#endregion

#region Logo Fetching
def check_existing_logo(airline_name):
    try:
        os.makedirs("assets", exist_ok=True)
        assets_dir = Path("assets")
        
        for ext in ['png', 'jpg', 'jpeg', 'svg', 'gif']:
            logo_file = assets_dir / f"{airline_name}.{ext}"
            if logo_file.exists():
                return logo_file.name
        
        return None
    except Exception as e:
        logger.warning(f"Error checking existing logo for {airline_name}: {e}")
        return None


def download_logo(url, airline_name):
    try:
        os.makedirs("assets", exist_ok=True)
        
        filename = f"{airline_name}.png"
        filepath = os.path.join("assets", filename)
        
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(r.content)
        
        return filename
    except Exception as e:
        logger.error(f"Error downloading logo for {airline_name}: {e}")
        return None


def fetch_airline_logo(airline_name, airline_icao):
    if not airline_icao or airline_icao == '-' or airline_icao == 'N/A':
        return None
    
    url = LOGO_REPO_URL.format(icao=airline_icao)
    return download_logo(url, airline_name)
#endregion

#region Helpers

def estimate_time_minutes(distance_km: float, aircraft: str = None) -> int:
    if aircraft and aircraft in CRUISE_SPEED_KMH:
        speed = CRUISE_SPEED_KMH[aircraft]
    else:
        speed = 470 * 1.852
    hours = distance_km / speed
    return ceil(hours * 60)

def split_time(minutes: int) -> dict | None:
    if minutes < 60:
        return None
    return {
        "hours": minutes // 60,
        "minutes": minutes % 60
    }

def supports_dist(distance_km: float, aircraft: str) -> bool:
    if aircraft not in MAX_RANGE_KM:
        return True
    return distance_km <= MAX_RANGE_KM[aircraft]

def supports_large(origin: str, dest: str, distance_km: float, aircraft: str) -> bool:
    if aircraft in MIN_RANGE_KM:
        if distance_km < MIN_RANGE_KM[aircraft]:
            return False
    
    if aircraft in MAJOR_AIRPORTS:
        major_airports = MAJOR_AIRPORTS[aircraft]
        if origin not in major_airports or dest not in major_airports:
            return False
    
    if aircraft in MAX_RANGE_KM:
        if distance_km > MAX_RANGE_KM[aircraft]:
            return False
    
    return True


def load_aircraft_support():
    support_path = "rawdata/aircraft_support.json"
    if not os.path.exists(support_path):
        logger.warning("aircraft_support.json not found, using minimal aircraft set")
        return ["A320", "A388"]
    
    with open(support_path, 'r', encoding='utf-8') as f:
        support_data = json.load(f)
    
    all_aircraft = set()
    for airline_data in support_data.values():
        all_aircraft.update(airline_data.get('validAircraft', []))
    
    return sorted(list(all_aircraft))


def load_airlines_database():
    logger.info("Loading airlines database...")
    with open(AIRLINES_DATABASE_FILE, 'r', encoding='utf-8') as f:
        airlines_db = json.load(f)
    
    name_to_airline = {}
    for airline in airlines_db:
        if airline.get('name'):
            normalized_name = airline['name'].lower().strip()
            name_to_airline[normalized_name] = airline
    
    logger.info(f"Loaded {len(airlines_db)} airlines from database")
    return name_to_airline


def find_airline_icao(airline_name, name_to_airline):
    normalized = airline_name.lower().strip()

    if normalized in name_to_airline:
        airline = name_to_airline[normalized]
        icao = airline.get('icao')
        if icao and icao != 'N/A' and icao:
            return icao
    
    for db_name, airline in name_to_airline.items():
        if normalized in db_name or db_name in normalized:
            icao = airline.get('icao')
            if icao and icao != 'N/A' and icao:
                return icao
    
    return None


def build_flight_numbers_config(valid_airlines, name_to_airline):
    logger.info("Building flight numbers configuration...")
    
    existing_config = {}
    if os.path.exists(CONFIG_FLIGHT_NUMBERS):
        try:
            with open(CONFIG_FLIGHT_NUMBERS, 'r', encoding='utf-8') as f:
                existing_config = json.load(f)
            logger.info(f"Loaded {len(existing_config)} existing flight number configurations")
        except Exception as e:
            logger.warning(f"Could not load existing config: {e}")
    
    flight_numbers = {}
    found_count = 0
    not_found = []
    preserved_count = 0
    
    for airline_name in valid_airlines:
        normalized_key = airline_name.lower()
        
        if normalized_key in existing_config:
            if existing_config[normalized_key].get("icao_ranges"):
                flight_numbers[normalized_key] = existing_config[normalized_key]
                preserved_count += 1
                found_count += 1
                continue
        
        icao = find_airline_icao(airline_name, name_to_airline)
        
        if icao:
            flight_numbers[normalized_key] = {
                "prefix": icao,
                "icao_ranges": {},
                "default_range": DEFAULT_FLIGHT_NUMBER_RANGE
            }
            found_count += 1
        else:
            not_found.append(airline_name)
    
    logger.info(f" Found ICAO codes for {found_count}/{len(valid_airlines)} airlines")
    logger.info(f" Preserved {preserved_count} manually configured airlines")
    logger.info(f" Missing ICAO codes for {len(not_found)} airlines")
    
    os.makedirs("config", exist_ok=True)
    with open(CONFIG_FLIGHT_NUMBERS, 'w', encoding='utf-8') as f:
        json.dump(flight_numbers, f, indent=2)
    
    logger.info(f" Saved flight numbers configuration to {CONFIG_FLIGHT_NUMBERS}")
    return flight_numbers


def update_airline_files_config(airline_name, route_file):
    if os.path.exists(CONFIG_AIRLINE_FILES):
        with open(CONFIG_AIRLINE_FILES, 'r', encoding='utf-8') as f:
            airline_files = json.load(f)
    else:
        airline_files = {}
    
    airline_files[airline_name] = route_file
    
    with open(CONFIG_AIRLINE_FILES, 'w', encoding='utf-8') as f:
        json.dump(airline_files, f, indent=2)


def update_airline_logos_config(airline_name, logo_filename):
    if os.path.exists(CONFIG_AIRLINE_LOGOS):
        with open(CONFIG_AIRLINE_LOGOS, 'r', encoding='utf-8') as f:
            airline_logos = json.load(f)
    else:
        airline_logos = {}
    
    airline_logos[airline_name] = logo_filename
    
    with open(CONFIG_AIRLINE_LOGOS, 'w', encoding='utf-8') as f:
        json.dump(airline_logos, f, indent=2)


def save_airline_routes(airline_name, iata, icao, routes, output_file, skip_media=False):
    os.makedirs("data", exist_ok=True)
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "airline": airline_name,
            "iata": iata,
            "icao": icao,
            "routes": routes
        }, f, indent=2)
    
    update_airline_files_config(airline_name, output_file)
    
    if skip_media:
        return
    
    existing_logo = check_existing_logo(airline_name)
    if existing_logo:
        update_airline_logos_config(airline_name, existing_logo)
    else:
        logo_filename = fetch_airline_logo(airline_name, icao)
        if logo_filename:
            update_airline_logos_config(airline_name, logo_filename)

#endregion

#region main

logger.info("=" * 60)
logger.info("Starting MSFS Route Creator Data Build")
logger.info("=" * 60)

logger.info("Loading valid airlines list...")
with open(VALID_AIRLINES_FILE, 'r', encoding='utf-8') as f:
    valid_airlines = json.load(f)
logger.info(f"Loaded {len(valid_airlines)} valid airlines")

name_to_airline = load_airlines_database()
flight_numbers_config = build_flight_numbers_config(valid_airlines, name_to_airline)

logger.info("Building airline routes structure...")
airline_routes = {}
iata_to_airline_name = {}

for airline_name in valid_airlines:
    airline_name = airline_name.strip()

    airline_data = None
    normalized_name = airline_name.lower().strip()
    
    if normalized_name in name_to_airline:
        airline_data = name_to_airline[normalized_name]
    else:
        for db_name, data in name_to_airline.items():
            if normalized_name in db_name or db_name in normalized_name:
                airline_data = data
                break
    
    if airline_data and airline_data.get('iata') and airline_data.get('icao'):
        iata = airline_data['iata']
        icao = airline_data['icao']
        
        if iata and iata != '-' and iata != 'N/A':
            airline_routes[airline_name] = {
                "iata": iata,
                "icao": icao,
                "routes": []
            }
            iata_to_airline_name[iata] = airline_name

logger.info(f"Built route structure for {len(airline_routes)} airlines with valid IATA codes")
#endregion

#region --verify argument

if args.verify:
    logger.info("=" * 60)
    logger.info("VERIFY MODE - Checking route coverage")
    logger.info("=" * 60)
    
    # Check which airlines have route files
    present_airlines = []
    missing_airlines = []
    
    for airline_name in airline_routes.keys():
        safe_name = airline_name.strip().lower().replace(' ', '_').replace('\r', '').replace('\n', '')
        filename = f"data/{safe_name}_routes.json"
        
        if os.path.exists(filename):
            present_airlines.append(airline_name)
        else:
            missing_airlines.append(airline_name)
    
    logger.info(f"\n Routes Present: {len(present_airlines)}")
    logger.info(f" Routes Missing: {len(missing_airlines)}")
    
    if missing_airlines:
        logger.info(f"\nMissing airlines:")
        for airline in missing_airlines[:10]:
            logger.info(f"  - {airline}")
        if len(missing_airlines) > 10:
            logger.info(f"  ... and {len(missing_airlines) - 10} more")
    
    coverage_pct = (len(present_airlines) / len(airline_routes)) * 100 if airline_routes else 0
    logger.info(f"\nCoverage: {coverage_pct:.1f}%")
    logger.info("=" * 60)
    logger.info("Verify complete - exiting without building routes")
    logger.info("=" * 60)
    exit(0)
#endregion

#region --fix-media argument

if args.fix_media:
    logger.info("=" * 60)
    logger.info("FIX MEDIA MODE - Checking for missing airline logos")
    logger.info("=" * 60)
    
    data_dir = Path("data")
    if not data_dir.exists():
        logger.error("data/ folder does not exist!")
        exit(1)
    
    route_files = list(data_dir.glob("*_routes.json"))
    logger.info(f"Found {len(route_files)} route files in data/")
    
    airlines_with_routes = []
    airlines_missing_logos = []
    airlines_with_logos = []
    
    airlines_data = {}
    
    for route_file in route_files:
        try:
            with open(route_file, 'r', encoding='utf-8') as f:
                route_data = json.load(f)
                airline_name = route_data.get("airline")
                airline_icao = route_data.get("icao")
                
                if airline_name:
                    airlines_with_routes.append(airline_name)
                    airlines_data[airline_name] = airline_icao
                    
                    existing_logo = check_existing_logo(airline_name)
                    if existing_logo:
                        airlines_with_logos.append(airline_name)
                    else:
                        airlines_missing_logos.append(airline_name)
        except Exception as e:
            logger.warning(f"Error reading {route_file.name}: {e}")
    
    logger.info(f"\n Airlines with routes: {len(airlines_with_routes)}")
    logger.info(f" Airlines with logos: {len(airlines_with_logos)}")
    logger.info(f" Airlines missing logos: {len(airlines_missing_logos)}")

    if airlines_missing_logos:
        logger.info(f"\nAttempting to fetch {len(airlines_missing_logos)} missing logos from GitHub repository...")
        
        successful_downloads = 0
        failed_downloads = 0
        total_to_download = len(airlines_missing_logos)
        
        for idx, airline_name in enumerate(airlines_missing_logos, 1):
            existing = check_existing_logo(airline_name)
            if existing:
                continue
            
            airline_icao = airlines_data.get(airline_name)
            
            logo_filename = fetch_airline_logo(airline_name, airline_icao)
            
            if logo_filename:
                update_airline_logos_config(airline_name, logo_filename)
                successful_downloads += 1
                
                if successful_downloads % 10 == 0:
                    logger.info(f"Assets downloaded: {successful_downloads}/{total_to_download}")
            else:
                failed_downloads += 1
                logger.error(f" Failed to download logo for: {airline_name}")
        
        logger.info("\n" + "=" * 60)
        logger.info(f"Download Summary:")
        logger.info(f"   Successful: {successful_downloads}")
        logger.info(f"   Failed: {failed_downloads}")
        logger.info("=" * 60)
    else:
        logger.info("\nAll airlines with routes already have logos!")
    
    logger.info("Fix media mode complete - exiting")
    logger.info("=" * 60)
    exit(0)

#endregion

#region routing

logger.info("Loading airport mappings...")
iata_to_icao = {}
with open(AIRPORTS_CSV, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        iata = row.get("iata_code")
        icao = row.get("icao_code")
        if iata and icao:
            iata_to_icao[iata] = icao
logger.info(f" Loaded {len(iata_to_icao)} airport mappings")


logger.info("Loading airline routes...")
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)
logger.info(f" Loaded routes for {len(data)} airports")

logger.info("Processing routes...")
route_count = 0

all_aircraft_codes = load_aircraft_support()
logger.info(f"Generating support fields for {len(all_aircraft_codes)} aircraft types")

for origin_iata, origin_data in data.items():
    origin_name = origin_data.get("name", origin_iata)
    origin_icao = iata_to_icao.get(origin_iata, "")

    for route in origin_data.get("routes", []):
        dest_iata = route["iata"]
        dest_data = data.get(dest_iata, {})
        dest_name = dest_data.get("name", dest_iata)
        dest_icao = iata_to_icao.get(dest_iata, "")

        distance_km = route["km"]
        carriers = {c["iata"] for c in route.get("carriers", [])}

        time_min = estimate_time_minutes(distance_km)
        time_split = split_time(time_min)

        base_entry = {
            "from": origin_iata,
            "from_name": origin_name,
            "from_icao": origin_icao,
            "to": dest_iata,
            "to_name": dest_name,
            "to_icao": dest_icao,
            "distance_km": distance_km,
            "estimated_time_min": time_min
        }

        if time_split:
            base_entry["estimated_time"] = time_split

        for carrier_iata in carriers:
            if carrier_iata in iata_to_airline_name:
                airline_name = iata_to_airline_name[carrier_iata]
                
                route_entry = {**base_entry}

                for aircraft_code in all_aircraft_codes:
                    support_key = f"supports_{aircraft_code.lower()}"

                    if aircraft_code in MIN_RANGE_KM or aircraft_code in MAJOR_AIRPORTS:
                        route_entry[support_key] = supports_large(origin_icao, dest_icao, distance_km, aircraft_code)
                    else:
                        route_entry[support_key] = supports_dist(distance_km, aircraft_code)
                
                airline_routes[airline_name]["routes"].append(route_entry)
                route_count += 1

logger.info(f" Processed {route_count} total routes across all airlines")
#endregion

#region savedata

logger.info("Saving airline route files and fetching logos...")

if args.no_media:
    logger.info("--no-media flag set: Skipping GitHub logo downloads")

for airline_name, airline_data in airline_routes.items():
    if airline_data["routes"]:
        safe_name = airline_name.strip().lower().replace(' ', '_').replace('\r', '').replace('\n', '')
        filename = f"data/{safe_name}_routes.json"
        
        save_airline_routes(
            airline_name,
            airline_data["iata"],
            airline_data["icao"],
            airline_data["routes"],
            filename,
            skip_media=args.no_media
        )

#endregion

logger.info("=" * 60)
logger.info("Build complete!")
logger.info(f"Log file saved to: {log_filename}")
logger.info("=" * 60)
