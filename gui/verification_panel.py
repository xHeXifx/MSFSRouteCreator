from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QComboBox, QLineEdit, QPushButton, QTextEdit,
                               QCompleter, QGroupBox)
from PySide6.QtCore import Qt, Signal, QStringListModel
from core.route_loader import get_airline_files, get_all_aircraft, get_airline_aircraft


class VerificationPanel(QWidget):
    verify_clicked = Signal(str, str, str, str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.airport_choices = []
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        
        input_group = QGroupBox("Route Details")
        input_layout = QVBoxLayout()
        
        airline_label = QLabel("Airline:")
        airline_label.setStyleSheet("font-weight: bold;")
        self.airline_input = QLineEdit()
        self.airline_input.setPlaceholderText("Type to search airline...")
        
        self.airline_completer = QCompleter()
        self.airline_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.airline_completer.setFilterMode(Qt.MatchContains)
        self.airline_input.setCompleter(self.airline_completer)
        self.airline_completer.activated.connect(self.update_aircraft_list)
        
        airline_model = QStringListModel(list(get_airline_files().keys()))
        self.airline_completer.setModel(airline_model)
        
        input_layout.addWidget(airline_label)
        input_layout.addWidget(self.airline_input)
        
        aircraft_label = QLabel("Aircraft:")
        aircraft_label.setStyleSheet("font-weight: bold;")
        self.aircraft_combo = QComboBox()
        self.aircraft_combo.addItem("-- Select Aircraft --", None)
        self.aircraft_combo.setCurrentIndex(0)
        
        input_layout.addWidget(aircraft_label)
        input_layout.addWidget(self.aircraft_combo)
        
        departure_label = QLabel("Departure Airport:")
        departure_label.setStyleSheet("font-weight: bold;")
        self.departure_input = QLineEdit()
        self.departure_input.setPlaceholderText("Type to search airports...")
        
        self.departure_completer = QCompleter()
        self.departure_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.departure_completer.setFilterMode(Qt.MatchContains)
        self.departure_input.setCompleter(self.departure_completer)
        
        input_layout.addWidget(departure_label)
        input_layout.addWidget(self.departure_input)
        
        arrival_label = QLabel("Arrival Airport:")
        arrival_label.setStyleSheet("font-weight: bold;")
        self.arrival_input = QLineEdit()
        self.arrival_input.setPlaceholderText("Type to search airports...")
        
        self.arrival_completer = QCompleter()
        self.arrival_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.arrival_completer.setFilterMode(Qt.MatchContains)
        self.arrival_input.setCompleter(self.arrival_completer)
        
        input_layout.addWidget(arrival_label)
        input_layout.addWidget(self.arrival_input)
        
        # Verify Button
        self.verify_button = QPushButton("Verify Route")
        self.verify_button.clicked.connect(self.on_verify_clicked)
        self.verify_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        
        input_layout.addWidget(self.verify_button)
        input_group.setLayout(input_layout)
        
        results_group = QGroupBox("Verification Results")
        results_layout = QVBoxLayout()
        
        self.results_display = QTextEdit()
        self.results_display.setReadOnly(True)
        self.results_display.setPlaceholderText("Verification results will appear here...")
        
        results_layout.addWidget(self.results_display)
        results_group.setLayout(results_layout)
        
        main_layout.addWidget(input_group, stretch=1)
        main_layout.addWidget(results_group, stretch=2)
        
        self.setLayout(main_layout)
    
    def update_aircraft_list(self, airline_name=None):
        if airline_name is None:
            airline_name = self.airline_input.text().strip()
        
        self.aircraft_combo.clear()
        self.aircraft_combo.addItem("-- Select Aircraft --", None)
        
        if airline_name:
            airline_aircraft = get_airline_aircraft(airline_name)
            all_aircraft = get_all_aircraft()
            
            if airline_aircraft:
                valid_codes = [ac['icao'] for ac in all_aircraft if ac['icao'] in airline_aircraft]
                self.aircraft_combo.addItems(valid_codes)
            else:
                self.aircraft_combo.addItems([ac['icao'] for ac in all_aircraft])
        
        self.aircraft_combo.setCurrentIndex(0)
    
    def set_airport_choices(self, choices):
        self.airport_choices = choices
        
        self.departure_completer.setModel(None)
        departure_model = QStringListModel(choices)
        self.departure_completer.setModel(departure_model)

        self.arrival_completer.setModel(None)
        arrival_model = QStringListModel(choices)
        self.arrival_completer.setModel(arrival_model)
    
    def on_verify_clicked(self):
        airline = self.airline_input.text().strip()
        aircraft = self.aircraft_combo.currentText()
        departure = self.departure_input.text().strip().upper()
        arrival = self.arrival_input.text().strip().upper()
        
        if not airline:
            self.display_error("Please select an airline")
            return
        
        if not aircraft or aircraft.startswith("--"):
            self.display_error("Please select an aircraft")
            return
        
        if not departure:
            self.display_error("Please enter a departure airport")
            return
        
        if not arrival:
            self.display_error("Please enter an arrival airport")
            return
        
        if departure == arrival:
            self.display_error("Departure and arrival airports cannot be the same")
            return
        
        self.verify_clicked.emit(airline, aircraft, departure, arrival)
    
    def display_result(self, result):
        html = "<style>"
        html += "body { font-family: Arial, sans-serif; }"
        html += ".valid { color: #4CAF50; font-weight: bold; }"
        html += ".invalid { color: #f44336; font-weight: bold; }"
        html += ".warning { color: #ff9800; font-weight: bold; }"
        html += ".info { margin: 10px 0; }"
        html += ".section { margin: 15px 0; }"
        html += "</style>"
        
        if result['valid']:
            html += f"<div class='section'><span class='valid'>✅ ROUTE IS VALID</span></div>"
            html += f"<div class='info'><strong>Airline:</strong> {result['airline']}</div>"
            html += f"<div class='info'><strong>Aircraft:</strong> {result['aircraft']}</div>"
            html += f"<div class='info'><strong>Route:</strong> {result['route_info']['from_icao']} → {result['route_info']['to_icao']}</div>"
            html += "<hr>"
            html += "<div class='section'><strong>Route Details:</strong></div>"
            html += f"<div class='info'><strong>From:</strong> {result['route_info']['from_name']} ({result['route_info']['from_icao']})</div>"
            html += f"<div class='info'><strong>To:</strong> {result['route_info']['to_name']} ({result['route_info']['to_icao']})</div>"
            html += f"<div class='info'><strong>Distance:</strong> {result['route_info']['distance_km']} km</div>"
            html += f"<div class='info'><strong>Estimated Time:</strong> {result['route_info']['estimated_time_min']} minutes</div>"
            
            if result.get('aircraft_notes'):
                html += f"<div class='section'><span class='warning'>⚠️ {result['aircraft_notes']}</span></div>"
        else:
            html += f"<div class='section'><span class='invalid'>❌ ROUTE IS INVALID</span></div>"
            html += f"<div class='info'><strong>Reason:</strong> {result['reason']}</div>"
            
            if result.get('suggestions'):
                html += "<div class='section'><strong>Suggestions:</strong></div>"
                for suggestion in result['suggestions']:
                    html += f"<div class='info'>• {suggestion}</div>"
        
        self.results_display.setHtml(html)
    
    def display_error(self, message):
        html = f"<div style='color: #f44336; font-weight: bold;'>❌ {message}</div>"
        self.results_display.setHtml(html)
