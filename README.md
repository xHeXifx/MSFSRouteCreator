<h1 align="center">MSFS Route Creator</h1>
<p align="center">A CLI tool for generating random realistic flight routes for MSFS with direct integration to SimBrief Dispatch for flight planning.</p>

### [IMPORTANT NOTE FOR THE A380X](#some-notes)
### [Current airlines and aircrafts](docs/currentAirlinesAndAircraft.md)

## Features

- **Random Route Generation**: Select from real-world airline routes
- **Aircraft Compatibility**: Filter routes based on aircraft capabilities
- **SimBrief Integration**: Automatically open generated routes in SimBrief Dispatch with realistic flight numbers

## Installation

1. Clone this repository:
```bash
git clone https://github.com/xHeXifx/MSFSRouteCreator
cd MSFSRouteCreator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Build data:
```bash
python buildData.py
```

## Usage

### Generate a Random Route

Run the main application:
```bash
python main.py
```

1. Select an airline
2. Choose your aircraft
3. Pick a departure airport
4. Set a maximum flight time

The tool will randomly select a valid route and display:
- Airline and aircraft type
- Departure and arrival airports with ICAO codes
- Distance in kilometers
- Estimated flight time

You can then choose to:
- Open the route in SimBrief Dispatch
- Generate another route
- Exit

## Data Structure

- `rawdata/`: Raw source data
  - `airline_routes.json`: Complete airline route network
  - `airports.csv`: Airport codes (IATA/ICAO mapping)
- `data/`: Processed airline-specific routes
  - `british_airways_routes.json`
  - `easyjet_routes.json`

## Flight Number Logic

The tool generates realistic flight numbers:

**British Airways (BAW)**:
- Heathrow (EGLL): 1-999
- Gatwick (EGKK): 2000-2899
- London City/Newquay: 3000-4500
- Other airports: 1300-1499

**easyJet (EZY)**:
- Gatwick (EGKK): 6000-6999 or 8000-8999
- Luton (EGGW): 1-1999
- Stansted (EGSS): 3000-3999
- Other airports: 7000-7999

## Some Notes

- Currently the A380X has NO valid routes with easyJet, this is mainly because easyJet doesnt fly far enough for a valid A380 flight but IRL they also just don't fly the A380 anyways.
- Not 1000% sure if everything generated is 100% valid in a real world scenario. Flight numbers may also be wrong but i've gone off data i could find around the internet and hoped for the best. 
- I do plan on adding more airlines at some point, easyJet and British Airways are my personal prefference of airlines on MSFS so thats the 2 I've gone with for now however hopefully more soon.
- As well as airlines do plan on more aircraft, again i mainly use the A320N and the A380 so haven't added more.

## Requirements

- InquirerPy

## [LICENSE](LICENSE.md)