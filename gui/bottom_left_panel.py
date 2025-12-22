from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox
from PySide6.QtCore import Qt


class BottomLeftPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()

        group_box = QGroupBox("Flight Plan Details")
        group_layout = QVBoxLayout()
        
        self.airline_label = QLabel("Airline: -")
        self.aircraft_label = QLabel("Aircraft: -")
        self.from_label = QLabel("From: -")
        self.to_label = QLabel("To: -")
        self.distance_label = QLabel("Distance: -")
        self.time_label = QLabel("Time: -")
        
        for label in [self.airline_label, self.aircraft_label, self.from_label,
                     self.to_label, self.distance_label, self.time_label]:
            label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        
        group_layout.addWidget(self.airline_label)
        group_layout.addWidget(self.aircraft_label)
        group_layout.addWidget(self.from_label)
        group_layout.addWidget(self.to_label)
        group_layout.addWidget(self.distance_label)
        group_layout.addWidget(self.time_label)
        group_layout.addStretch()
        
        group_box.setLayout(group_layout)
        layout.addWidget(group_box)
        
        self.setLayout(layout)
    
    def update_details(self, details):
        self.airline_label.setText(f"Airline: {details['airline']}")
        self.aircraft_label.setText(f"Aircraft: {details['aircraft']}")
        self.from_label.setText(
            f"From: {details['from_code']} — {details['from_name']} ({details['from_icao']})"
        )
        self.to_label.setText(
            f"To: {details['to_code']} — {details['to_name']} ({details['to_icao']})"
        )
        self.distance_label.setText(f"Distance: {details['distance']}")
        self.time_label.setText(f"Time: {details['time']}")
    
    def clear_details(self):
        self.airline_label.setText("Airline: -")
        self.aircraft_label.setText("Aircraft: -")
        self.from_label.setText("From: -")
        self.to_label.setText("To: -")
        self.distance_label.setText("Distance: -")
        self.time_label.setText("Time: -")
