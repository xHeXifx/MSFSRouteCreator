from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QComboBox, QLineEdit, QCompleter)
from PySide6.QtCore import Qt, Signal
from core.route_loader import get_airline_files, get_all_aircraft, get_airline_aircraft


class TopLeftPanel(QWidget):
    airline_changed = Signal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.airport_choices = []
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        aircraft_label = QLabel("Aircraft:")
        aircraft_label.setStyleSheet("font-weight: bold;")
        self.aircraft_combo = QComboBox()
        self.aircraft_combo.addItem("-- Select Aircraft --", None)
        self.aircraft_combo.setCurrentIndex(0)
        layout.addWidget(aircraft_label)
        layout.addWidget(self.aircraft_combo)
        
        airline_label = QLabel("Airline:")
        airline_label.setStyleSheet("font-weight: bold;")
        self.airline_input = QLineEdit()
        self.airline_input.setPlaceholderText("Type to search...")
        
        self.airline_completer = QCompleter()
        self.airline_completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.airline_completer.setFilterMode(Qt.MatchContains)
        self.airline_input.setCompleter(self.airline_completer)
        self.airline_completer.activated.connect(self.airline_changed.emit)
        self.airline_completer.activated.connect(self.update_aircraft_list)
        
        from PySide6.QtCore import QStringListModel
        airline_model = QStringListModel(list(get_airline_files().keys()))
        self.airline_completer.setModel(airline_model)
        
        layout.addWidget(airline_label)
        layout.addWidget(self.airline_input)
        
        departure_label = QLabel("Departure Airport:")
        departure_label.setStyleSheet("font-weight: bold;")
        self.departure_input = QLineEdit()
        self.departure_input.setPlaceholderText("Type to search (or leave blank for random)...")
        
        self.completer = QCompleter()
        self.completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.completer.setFilterMode(Qt.MatchContains)
        self.departure_input.setCompleter(self.completer)
        
        layout.addWidget(departure_label)
        layout.addWidget(self.departure_input)

        max_time_label = QLabel("Max Flight Time (minutes):")
        max_time_label.setStyleSheet("font-weight: bold;")
        self.max_time_input = QLineEdit()
        self.max_time_input.setPlaceholderText("Optional - leave blank for no limit")
        layout.addWidget(max_time_label)
        layout.addWidget(self.max_time_input)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def set_airport_choices(self, choices):
        self.airport_choices = choices
        self.completer.setModel(None)
        from PySide6.QtCore import QStringListModel
        model = QStringListModel(choices)
        self.completer.setModel(model)
    
    def update_aircraft_list(self, airline_name=None):
        if airline_name is None:
            airline_name = self.get_selected_airline()
        
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
    
    def get_selected_aircraft(self):
        return self.aircraft_combo.currentText()
    
    def get_selected_airline(self):
        return self.airline_input.text().strip()
    
    def get_departure_airport(self):
        return self.departure_input.text().strip()
    
    def get_max_time(self):
        text = self.max_time_input.text().strip()
        if text and text.isdigit():
            return int(text)
        return None
    
    def validate_inputs(self):
        if not self.get_selected_aircraft() or self.aircraft_combo.currentIndex() == 0:
            return False, "Please select an aircraft"
        
        if not self.get_selected_airline():
            return False, "Please select an airline"
        
        text = self.max_time_input.text().strip()
        if text and not text.isdigit():
            return False, "Max flight time must be a number"
        
        return True, ""
