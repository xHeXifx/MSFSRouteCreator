<p align="center">
  <img src="/assets/icon.png" alt="MSFS Route Creator Logo" width="200">
</p>
<h1 align="center">MSFS Route Creator</h1>
<p align="center">A GUI and CLI tool for generating random realistic flight routes for MSFS with direct integration to SimBrief Dispatch for flight planning.</p>

### [IMPORTANT NOTE FOR THE A380X](#some-notes)
### [Current airlines and aircrafts](docs/currentAirlinesAndAircraft.md)

## Features

- **Random Route Generation**: Select from real world airline routes
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
buildData.py contains a few arguments to make things a big smoother.
```bash
python buildData.py --no-media # Sets up routing but doesnt download images
```
```bash
python buildData.py --fix-media # Checks for missing images and attempts a fix.
```
```bash
python buildData.py --verify # Checks which airlines are missing route files.
```
I reccomend running with ``--no-media`` first time round then ``--fix-media`` afterwards.
 
## Usage

### GUI Mode (Default)

Run the application without arguments to launch the GUI:
```bash
python main.py
```
### CLI Mode

Run with the `-cli` flag for the original command-line interface:
```bash
python main.py -cli
```

### Generate a Random Route

Run the main application:
```bash
python main.py
```

## Adding assets, routes or airlines

This will get complicated if you wish to add your own routes and airlines, assets is easy. I know that the repo which contains the logos doesnt have them all so heres how to fix that.

### Add an airline
1. Under ```/config/flight_numbers.json``` add your airline, should look something like:
```json
  "{AIRLINE}": {
    "prefix": "{ICAO}",
    "icao_ranges": {},
    "default_range": [ // Flight number range 
      0,
      9999
    ]
  },
```
2. Thats pretty much it, for these airlines to actually make a difference though you will need to add an asset and routes for them. An asset is not required just dont add a pointer in airline_logos.json to it.

### Add an asset
1. Find the exact airline name, you can do this by running buildData with --fix-media, it will say ```Error downloading logo for {your_airline}```  
2. Place your file in /assets named {your_airline}.{extention}. You might notice all the others are in .png, this is not required it can be any image extention (to my knowledge).
3. Open ```config/airline_logos.json```. In this file simply add a new item to the list with ```{your_airline}: {filename}``` replacing your_airline with the one from earlier and filename with the exact filename (including extension).

### Add a route. (You must add an airline to add routes for it.)
As mentioned this will be more difficult so best of luck.
1. Create your file under /data named ```{airline}_routes.json```
2. I would reccomend looking at the other routes to see the structure, add your airline name, iata and icao as well as a routes array.
3. Again as before, look how routes array is structured in other routes files and fill yours out.  
**Note:** The logic behind ```supports_a320/a380``` is that if the route distance is less than 4800km the 320 can fly it. A380 gets a bit more complicated, it can only land at select airports due to its size. Therefore it has to takeoff and land from certain airports and the route has to be more than 5500km.


## Some Notes

- Real world fleet applies, airlines which dont fly the A380 wont return any valid flights when selecting the A380.
- The majority of flight numbers will be invalid in a real world scenario, theres like 600 airlines and finding logic for them would be hell.
- I do plan on adding more aircraft, i mainly use the A320N and the A380 so haven't added more.


## Data Structure

The project is now modular with clear separation:

- `core/`: Core logic
  - `route_loader.py`: Route data loading and airport indexing
  - `logic.py`: Flight number generation, route filtering, SimBrief URLs
  - `cli.py`: CLI interface implementation
- `gui/`: GUI components
  - `main_window.py`: Main application window
  - `top_left_panel.py`: Input controls
  - `top_right_panel.py`: Airline logo display
  - `bottom_left_panel.py`: Flight plan details output
  - `bottom_right_panel.py`: Action buttons
- `data/`: Processed airline-specific routes
  - `{airline}_routes.json`
- `rawdata/`: Raw source data
  - `airline_routes.json`: Complete airline route network
  - `airports.csv`: Airport codes (Provided by [OurAirports](https://ourairports.com/data/))
  - `airlines.json`: List of airlines with their IATA, ICAO, etc data.
  - `ValidAirlines.json`: Simple list of the airlines which have routes present in `airline_routes.json`
  - `fleetDataForAirlines.csv`: List of airlines and their fleet
  - `airline_support.json`: Similar to fleetDataForAirlines but structured better.
  - `aircraft.dat`: Used to match aircraft fullname to code.
- `assets/`: Airline logo images for GUI



## Requirements

- InquirerPy (for CLI)
- PySide6 (for GUI)

## Credits
- Airport Data: [OurAirports](https://ourairports.com/data/)
- Airline Route Data: [Jonty's Airline Route Data](https://github.com/Jonty/airline-route-data)
- Airline Data: [openflights GitHub](https://github.com/jpatokal/openflights)
- Airline Logos: [Jxck-S's airline-logos](https://github.com/Jxck-S/airline-logos)
- Program Development: [Me Me Me](https://hexif.vercel.app)

## [LICENSE](LICENSE.md)