from PySide6.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, 
                               QVBoxLayout, QMessageBox, QTabWidget)
from PySide6.QtCore import Qt
import webbrowser

from gui.top_left_panel import TopLeftPanel
from gui.top_right_panel import TopRightPanel
from gui.bottom_left_panel import BottomLeftPanel
from gui.bottom_right_panel import BottomRightPanel
from gui.verification_panel import VerificationPanel
from gui.airline_generator_panel import AirlineGeneratorPanel
from gui.flight_summary_panel import FlightSummaryPanel
from core.route_loader import load_routes, load_airline_data, build_airport_index, get_airport_choices, extract_iata, get_airline_files
from core.logic import generate_random_route, build_simbrief_url, format_route_details, verify_route, genFlightNum


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_route = None
        self.current_airline = None
        self.current_aircraft = None
        self.current_airline_data = None
        self.routes = []
        self.init_ui()
        self.load_initial_data()
    
    def init_ui(self):
        self.setWindowTitle("MSFS Route Creator")
        self.setMinimumSize(800, 600)
        
        central_widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create Generator tab
        generator_tab = QWidget()
        generator_layout = QVBoxLayout()
        
        top_layout = QHBoxLayout()
        
        self.top_left = TopLeftPanel()
        self.top_right = TopRightPanel()
        
        top_layout.addWidget(self.top_left, stretch=2)
        top_layout.addWidget(self.top_right, stretch=1)
        
        bottom_layout = QHBoxLayout()
        
        self.bottom_left = BottomLeftPanel()
        self.bottom_right = BottomRightPanel()
        
        bottom_layout.addWidget(self.bottom_left, stretch=2)
        bottom_layout.addWidget(self.bottom_right, stretch=1)
        
        generator_layout.addLayout(top_layout, stretch=1)
        generator_layout.addLayout(bottom_layout, stretch=1)
        generator_tab.setLayout(generator_layout)
        
        self.verification_panel = VerificationPanel()
        
        self.airline_generator_panel = AirlineGeneratorPanel()

        self.flight_summary_panel = FlightSummaryPanel()
        
        self.tab_widget.addTab(generator_tab, "Route Generator")
        self.tab_widget.addTab(self.verification_panel, "Route Verifier")
        self.tab_widget.addTab(self.airline_generator_panel, "Airline Finder")
        self.tab_widget.addTab(self.flight_summary_panel, "Flight Summary")
        
        main_layout.addWidget(self.tab_widget)
        
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        self.top_left.airline_changed.connect(self.on_airline_changed)
        self.bottom_right.generate_clicked.connect(self.on_generate_clicked)
        self.bottom_right.simbrief_clicked.connect(self.on_simbrief_clicked)
        self.bottom_right.close_clicked.connect(self.close)
        self.verification_panel.verify_clicked.connect(self.on_verify_route)
        self.verification_panel.airline_input.textChanged.connect(self.on_verification_airline_changed)
    
    def load_initial_data(self):
        pass
    
    def load_airline_data(self, airline_name):
        if not airline_name or airline_name.startswith("--"):
            return
        
        try:
            self.current_airline_data = load_airline_data(airline_name)
            self.routes = self.current_airline_data["routes"]
            airport_index = build_airport_index(self.routes)
            airport_choices = get_airport_choices(airport_index)
            self.top_left.set_airport_choices(airport_choices)
        except Exception as e:
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to load airline data: {str(e)}"
            )
    
    def on_airline_changed(self, airline_name):
        if not airline_name or airline_name.startswith("--"):
            self.routes = []
            self.top_left.set_airport_choices([])
            return
        
        self.load_airline_data(airline_name)
        self.top_right.update_logo(airline_name)
        self.current_route = None
        self.bottom_left.clear_details()
        self.bottom_right.enable_simbrief(False)
    
    def on_generate_clicked(self):
        valid, error_msg = self.top_left.validate_inputs()
        if not valid:
            QMessageBox.warning(self, "Validation Error", error_msg)
            return
        
        airline = self.top_left.get_selected_airline()
        aircraft = self.top_left.get_selected_aircraft()
        departure_text = self.top_left.get_departure_airport()
        max_time = self.top_left.get_max_time()

        if not departure_text:
            import random
            support_key = f"supports_{aircraft.lower()}"
            valid_departures = list(set(
                r['from'] for r in self.routes 
                if r.get(support_key, False)
            ))
            
            if not valid_departures:
                QMessageBox.warning(
                    self,
                    "No Routes Available",
                    f"No routes available for this airline with {aircraft} support."
                )
                return
            origin_iata = random.choice(valid_departures)
        else:
            try:
                origin_iata = extract_iata(departure_text)
            except:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please select a valid departure airport from the list"
                )
                return
        
        route = generate_random_route(self.routes, origin_iata, aircraft, airline, max_time)
        
        if not route:
            QMessageBox.information(
                self,
                "No Routes Found",
                "❌ No valid routes found with current filters.\n\n"
                "Try adjusting your filters or selecting a different departure airport."
            )
            return
        
        self.current_route = route
        self.current_airline = airline
        self.current_aircraft = aircraft
        
        details = format_route_details(airline, aircraft, route)
        self.bottom_left.update_details(details)
        self.bottom_right.enable_simbrief(True)
    
    def on_simbrief_clicked(self):
        if not self.current_route:
            return
        
        flight_ident = genFlightNum(self.current_airline, self.current_route.get('from_icao'))
        flight_number = f"{flight_ident[0]} {flight_ident[1]}"
        
        callsign = ""
        if self.current_airline_data:
            callsign = self.current_airline_data.get('callsign', '')
        
        time_str = ""
        if "estimated_time" in self.current_route:
            t = self.current_route["estimated_time"]
            time_str = f"{t['hours']}h {t['minutes']}m"
        else:
            time_str = f"{self.current_route['estimated_time_min']} min"
        
        flight_data = {
            'airline': self.current_airline,
            'callsign': callsign,
            'aircraft': self.current_aircraft,
            'flight_number': flight_number,
            'departure_icao': self.current_route.get('from_icao', ''),
            'departure_name': self.current_route.get('from_name', ''),
            'arrival_icao': self.current_route.get('to_icao', ''),
            'arrival_name': self.current_route.get('to_name', ''),
            'distance': f"{self.current_route['distance_km']} km",
            'time': time_str
        }
        
        self.flight_summary_panel.update_flight_summary(flight_data, from_simbrief=False)
        
        self.tab_widget.setCurrentWidget(self.flight_summary_panel)
        
        url = build_simbrief_url(
            self.current_airline,
            self.current_aircraft,
            self.current_route
        )
        webbrowser.open(url)
    
    def on_verify_route(self, airline, aircraft, departure, arrival):
        try:
            routes = load_routes(airline)
            
            try:
                departure_iata = extract_iata(departure)
            except:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please select a valid departure airport from the list"
                )
                return
            
            try:
                arrival_iata = extract_iata(arrival)
            except:
                QMessageBox.warning(
                    self,
                    "Invalid Input",
                    "Please select a valid arrival airport from the list"
                )
                return
            
            result = verify_route(routes, departure_iata, arrival_iata, aircraft, airline)
            
            self.verification_panel.display_result(result)
            
        except Exception as e:
            QMessageBox.critical(
                self,
                "Verification Error",
                f"Failed to verify route: {str(e)}"
            )
    
    def on_verification_airline_changed(self):
        airline_text = self.verification_panel.airline_input.text().strip()
        
        airline_files = get_airline_files()
        if airline_text in airline_files:
            try:
                routes = load_routes(airline_text)
                airport_index = build_airport_index(routes)
                airport_choices = get_airport_choices(airport_index)
                self.verification_panel.set_airport_choices(airport_choices)
            except Exception as e:
                self.verification_panel.set_airport_choices([])
