from PySide6.QtWidgets import (QWidget, QVBoxLayout, QLabel, 
                               QComboBox, QLineEdit, QCompleter)
from PySide6.QtCore import Qt, Signal


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
        self.aircraft_combo.addItems(["A320N", "A388"])
        self.aircraft_combo.setCurrentIndex(0)
        layout.addWidget(aircraft_label)
        layout.addWidget(self.aircraft_combo)
        
        airline_label = QLabel("Airline:")
        airline_label.setStyleSheet("font-weight: bold;")
        self.airline_combo = QComboBox()
        self.airline_combo.addItem("-- Select Airline --", None)
        self.airline_combo.addItems(["British Airways", "easyJet"])
        self.airline_combo.currentTextChanged.connect(self.airline_changed.emit)
        layout.addWidget(airline_label)
        layout.addWidget(self.airline_combo)
        
        departure_label = QLabel("Departure Airport:")
        departure_label.setStyleSheet("font-weight: bold;")
        self.departure_input = QLineEdit()
        self.departure_input.setPlaceholderText("Type to search...")
        
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
    
    def get_selected_aircraft(self):
        return self.aircraft_combo.currentText()
    
    def get_selected_airline(self):
        return self.airline_combo.currentText()
    
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
        
        if not self.get_selected_airline() or self.airline_combo.currentIndex() == 0:
            return False, "Please select an airline"
        
        if not self.get_departure_airport():
            return False, "Please select a departure airport"
        
        text = self.max_time_input.text().strip()
        if text and not text.isdigit():
            return False, "Max flight time must be a number"
        
        return True, ""
