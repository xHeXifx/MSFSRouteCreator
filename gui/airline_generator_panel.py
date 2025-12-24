from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QLineEdit, QComboBox, QPushButton, QTextEdit, QCompleter)
from PySide6.QtCore import Qt, Signal, QStringListModel
from core.route_loader import get_all_aircraft, get_airline_files, load_routes


class AirlineGeneratorPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.all_airports = set()
        self.init_ui()
        self.load_all_airports()
        self.load_aircraft_list()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        title = QLabel("Airline Generator")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        main_layout.addWidget(title)
        
        instructions = QLabel("Find airlines that fly a specific route with a specific aircraft")
        instructions.setStyleSheet("color: gray; margin-bottom: 20px;")
        main_layout.addWidget(instructions)
        
        aircraft_label = QLabel("Aircraft:")
        aircraft_label.setStyleSheet("font-weight: bold;")
        self.aircraft_combo = QComboBox()
        self.aircraft_combo.addItem("-- Select Aircraft --", None)
        main_layout.addWidget(aircraft_label)
        main_layout.addWidget(self.aircraft_combo)
        
        departure_label = QLabel("Departure Airport (ICAO):")
        departure_label.setStyleSheet("font-weight: bold;")
        self.departure_input = QLineEdit()
        self.departure_input.setPlaceholderText("Type ICAO code to search...")
        
        self.departure_completer = QCompleter()
        self.departure_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.departure_completer.setFilterMode(Qt.MatchContains)
        self.departure_input.setCompleter(self.departure_completer)
        
        main_layout.addWidget(departure_label)
        main_layout.addWidget(self.departure_input)
        
        arrival_label = QLabel("Arrival Airport (ICAO):")
        arrival_label.setStyleSheet("font-weight: bold;")
        self.arrival_input = QLineEdit()
        self.arrival_input.setPlaceholderText("Type ICAO code to search...")
        
        self.arrival_completer = QCompleter()
        self.arrival_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.arrival_completer.setFilterMode(Qt.MatchContains)
        self.arrival_input.setCompleter(self.arrival_completer)
        
        main_layout.addWidget(arrival_label)
        main_layout.addWidget(self.arrival_input)
        
        # Search button
        self.search_button = QPushButton("Find Airlines")
        self.search_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
        """)
        self.search_button.clicked.connect(self.on_search_clicked)
        main_layout.addWidget(self.search_button)
        
        results_label = QLabel("Results:")
        results_label.setStyleSheet("font-weight: bold; margin-top: 20px;")
        main_layout.addWidget(results_label)
        
        self.results_text = QTextEdit()
        self.results_text.setReadOnly(True)
        self.results_text.setPlaceholderText("Results will appear here...")
        main_layout.addWidget(self.results_text)
        
        self.setLayout(main_layout)
    
    def load_all_airports(self):
        try:
            airline_files = get_airline_files()
            for airline_name in airline_files.keys():
                try:
                    routes = load_routes(airline_name)
                    for route in routes:
                        if route.get('from_icao'):
                            self.all_airports.add(route['from_icao'])
                        if route.get('to_icao'):
                            self.all_airports.add(route['to_icao'])
                except Exception:
                    continue
            
            airport_list = sorted(list(self.all_airports))
            model = QStringListModel(airport_list)
            self.departure_completer.setModel(model)
            self.arrival_completer.setModel(model)
            
        except Exception as e:
            print(f"Error loading airports: {e}")
    
    def load_aircraft_list(self):
        try:
            all_aircraft = get_all_aircraft()
            aircraft_codes = sorted([ac['icao'] for ac in all_aircraft if ac['icao']])
            self.aircraft_combo.addItems(aircraft_codes)
        except Exception as e:
            print(f"Error loading aircraft: {e}")
    
    def on_search_clicked(self):
        aircraft = self.aircraft_combo.currentText()
        departure = self.departure_input.text().strip().upper()
        arrival = self.arrival_input.text().strip().upper()
        
        if aircraft == "-- Select Aircraft --" or not aircraft:
            self.results_text.setHtml("<p style='color: red;'>❌ Please select an aircraft</p>")
            return
        
        if not departure:
            self.results_text.setHtml("<p style='color: red;'>❌ Please enter a departure airport</p>")
            return
        
        if not arrival:
            self.results_text.setHtml("<p style='color: red;'>❌ Please enter an arrival airport</p>")
            return
        
        self.results_text.setHtml("<p>Searching...</p>")
        matching_airlines = self.find_matching_airlines(aircraft, departure, arrival)
        
        if matching_airlines:
            result_html = f"<h3 style='color: green;'>✅ Found {len(matching_airlines)} airline(s)</h3>"
            result_html += f"<p><b>Route:</b> {departure} → {arrival}</p>"
            result_html += f"<p><b>Aircraft:</b> {aircraft}</p>"
            result_html += "<hr>"
            result_html += "<ul>"
            for airline_info in matching_airlines:
                result_html += f"<li><b>{airline_info['airline']}</b>"
                if airline_info.get('route_details'):
                    details = airline_info['route_details']
                    result_html += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;From: {details.get('from_name', departure)}"
                    result_html += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;To: {details.get('to_name', arrival)}"
                    if details.get('distance_km'):
                        result_html += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;Distance: {details['distance_km']} km"
                    if details.get('estimated_time_min'):
                        hours = details['estimated_time_min'] // 60
                        minutes = details['estimated_time_min'] % 60
                        result_html += f"<br>&nbsp;&nbsp;&nbsp;&nbsp;Flight Time: {hours}h {minutes}m"
                result_html += "</li>"
            result_html += "</ul>"
            self.results_text.setHtml(result_html)
        else:
            result_html = "<h3 style='color: orange;'>❌ No airlines found</h3>"
            result_html += f"<p>No airlines fly the route <b>{departure} → {arrival}</b> with aircraft <b>{aircraft}</b></p>"
            result_html += "<p>Try:</p>"
            result_html += "<ul>"
            result_html += "<li>Different aircraft type</li>"
            result_html += "<li>Different airports</li>"
            result_html += "<li>Check ICAO codes are correct</li>"
            result_html += "</ul>"
            self.results_text.setHtml(result_html)
    
    def find_matching_airlines(self, aircraft_code, departure_icao, arrival_icao):
        matching_airlines = []
        
        try:
            airline_files = get_airline_files()
            aircraft_field = f"supports_{aircraft_code.lower()}"
            
            for airline_name in airline_files.keys():
                try:
                    routes = load_routes(airline_name)
                    
                    for route in routes:
                        if (route.get('from_icao') == departure_icao and 
                            route.get('to_icao') == arrival_icao):

                            if route.get(aircraft_field, False):
                                matching_airlines.append({
                                    'airline': airline_name,
                                    'route_details': route
                                })
                                break
                
                except Exception as e:
                    continue
            
        except Exception as e:
            print(f"Error searching airlines: {e}")
        
        return matching_airlines
