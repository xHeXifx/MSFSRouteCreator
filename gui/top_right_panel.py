from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QIcon
import os


class TopRightPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.logo_label = QLabel()
        self.logo_label.setAlignment(Qt.AlignCenter)
        self.logo_label.setMinimumSize(200, 150)
        self.logo_label.setStyleSheet("border: 0px solid #1E1E1E;")
        self.logo_label.setScaledContents(False)
        self.logo_label.setWordWrap(True)
        
        layout.addWidget(self.logo_label)
        layout.addStretch()
        
        self.setLayout(layout)
        
        self.show_no_selection()
    
    def show_no_selection(self):
        self.logo_label.clear()
        self.logo_label.setStyleSheet("border: 0px solid #ccc; background-color: #1E1E1E;")
        self.logo_label.setText("⚠️\n\nNo Airline Selected")
        self.logo_label.setAlignment(Qt.AlignCenter)
    
    def update_logo(self, airline_name):
        if not airline_name or airline_name.startswith("--"):
            self.show_no_selection()
            return
        
        logo_map = {
            "British Airways": "British Airways.png",
            "easyJet": "easyJet.png",
            "Ryanair": "Ryanair.jpg",
            "Emirates": "Emirates.png",
            "Lufthansa": "Lufthansa.png",
            "Singapore Airlines": "Singapore Airlines.png",
            "Qatar Airways": "Qatar Airways.jpg"
        }
        
        logo_filename = logo_map.get(airline_name)
        if not logo_filename:
            self.show_no_selection()
            return
        
        logo_path = os.path.join("assets", logo_filename)
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            scaled_pixmap = pixmap.scaled(
                self.logo_label.width() - 20,
                self.logo_label.height() - 20,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.logo_label.setStyleSheet("border: 0px solid #ccc; padding: 10px;")
            self.logo_label.setPixmap(scaled_pixmap)
        else:
            self.logo_label.clear()
            self.logo_label.setStyleSheet("border: 0px solid #ccc; background-color: #1E1E1E;")
            self.logo_label.setText(f"{airline_name}\nLogo")
            self.logo_label.setAlignment(Qt.AlignCenter)
