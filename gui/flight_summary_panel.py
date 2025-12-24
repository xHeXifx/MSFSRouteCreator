from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFrame, QLineEdit, QStackedWidget, QMessageBox, QTextEdit)
from PySide6.QtCore import Qt, Signal, QThread
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PySide6.QtCore import QUrl
import json
import os
import re


class FlightSummaryPanel(QWidget):
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.network_manager = QNetworkAccessManager()
        self.init_ui()
    
    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setMinimumSize(400, 300)
        
        self.empty_view = self._create_empty_view()
        
        self.summary_view = self._create_summary_view()
        
        self.stacked_widget.addWidget(self.empty_view)
        self.stacked_widget.addWidget(self.summary_view)
        
        self.stacked_widget.setCurrentIndex(0)
        
        main_layout.addWidget(self.stacked_widget)
        self.setLayout(main_layout)
        
        self.load_user_id()
    
    def _create_empty_view(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        layout.addStretch()
        
        # Icon/Message
        message = QLabel("No flight plan generated")
        message.setStyleSheet("font-size: 20px; color: gray;")
        message.setAlignment(Qt.AlignCenter)
        layout.addWidget(message)
        
        # Fetch from SimBrief section
        fetch_label = QLabel("Fetch from SimBrief?")
        fetch_label.setStyleSheet("font-size: 16px; font-weight: bold; margin-top: 20px;")
        fetch_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(fetch_label)
        
        # User ID input
        user_id_layout = QHBoxLayout()
        user_id_label = QLabel("SimBrief User ID:")
        user_id_label.setStyleSheet("font-weight: bold;")
        self.user_id_input = QLineEdit()
        self.user_id_input.setPlaceholderText("Enter your SimBrief User ID...")
        self.user_id_input.setMaximumWidth(300)
        user_id_layout.addStretch()
        user_id_layout.addWidget(user_id_label)
        user_id_layout.addWidget(self.user_id_input)
        user_id_layout.addStretch()
        layout.addLayout(user_id_layout)
        
        # Fetch button
        self.fetch_button = QPushButton("Fetch Flight Plan")
        self.fetch_button.setStyleSheet("""
            QPushButton {
                background-color: #0066cc;
                color: white;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
                max-width: 200px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
            }
        """)
        self.fetch_button.clicked.connect(self.on_fetch_clicked)
        
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.fetch_button)
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        widget.setMinimumSize(300, 200)
        return widget
    
    def _create_summary_view(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        title = QLabel("Flight Summary")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #0066cc;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        self.subtitle = QLabel("")
        self.subtitle.setStyleSheet("font-size: 14px; color: gray; margin-bottom: 10px;")
        self.subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.subtitle)

        self.flight_details_text = QTextEdit()
        self.flight_details_text.setReadOnly(True)
        self.flight_details_text.setStyleSheet("""
            QTextEdit {
                background-color: transparent;
                color: #ffffff;
                border: none;
                padding: 15px;
                font-size: 14px;
                font-family: 'Courier New', monospace;
            }
        """)
        layout.addWidget(self.flight_details_text)
        
        self.clear_button = QPushButton("Clear Flight Plan")
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #cc6600;
                color: white;
                padding: 12px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #a35200;
            }
            QPushButton:pressed {
                background-color: #7a3d00;
            }
        """)
        self.clear_button.clicked.connect(self.clear_flight_plan)
        layout.addWidget(self.clear_button)
        
        widget.setLayout(layout)
        widget.setMinimumSize(300, 200)
        return widget
    
    def load_user_id(self):
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'userData.json')
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    user_id = data.get('simbrief_user_id', '')
                    self.user_id_input.setText(user_id)
            except Exception as e:
                print(f"Error loading user ID: {e}")
        else:
            print('No config found')
    
    def save_user_id(self):
        config_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config')
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, 'userData.json')
        
        user_id = self.user_id_input.text().strip()
        try:
            with open(config_path, 'w') as f:
                json.dump({'simbrief_user_id': user_id}, f, indent=2)
        except Exception as e:
            print(f"Error saving user ID: {e}")
    
    def on_fetch_clicked(self):
        user_id = self.user_id_input.text().strip()
        if not user_id:
            QMessageBox.warning(self, "Missing User ID", "Please enter your SimBrief User ID")
            return
        
        self.save_user_id()

        self.fetch_button.setEnabled(False)
        self.fetch_button.setText("Fetching...")
        
        url = f"https://www.simbrief.com/api/xml.fetcher.php?userid={user_id}&json=1"
        request = QNetworkRequest(QUrl(url))
        reply = self.network_manager.get(request)
        reply.finished.connect(lambda: self.on_fetch_finished(reply))
    
    def on_fetch_finished(self, reply):
        self.fetch_button.setEnabled(True)
        self.fetch_button.setText("Fetch Flight Plan")
        
        if reply.error() != QNetworkReply.NoError:
            QMessageBox.critical(self, "Error", f"Failed to fetch from SimBrief: {reply.errorString()}")
            reply.deleteLater()
            return
        
        try:
            data = json.loads(reply.readAll().data().decode())
            reply.deleteLater()
            
            flight_data = self.parse_simbrief_data(data)
            if flight_data:
                self.update_flight_summary(flight_data, from_simbrief=True)
            else:
                QMessageBox.warning(self, "No Data", "No flight plan found in SimBrief")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to parse SimBrief data: {str(e)}")
            reply.deleteLater()
    
    def parse_simbrief_data(self, data):
        try:
            origin = data.get('origin', {})
            destination = data.get('destination', {})
            general = data.get('general', {})
            aircraft_data = data.get('aircraft', {})
            atc = data.get('atc', {})
            
            departure_icao = origin.get('icao_code', '')
            departure_name = origin.get('name', '')
            arrival_icao = destination.get('icao_code', '')
            arrival_name = destination.get('name', '')
            
            airline_icao = general.get('icao_airline', '')
            flight_number_only = general.get('flight_number', '')
            flight_number = f"{airline_icao}{flight_number_only}" if airline_icao and flight_number_only else flight_number_only
            
            aircraft = aircraft_data.get('icao_code', '')

            callsign = self.get_callsign_for_airline(airline_icao)
            
            distance = general.get('gc_distance', '')
            if distance:
                distance = f"{distance} nm"
            
            time_enroute = data.get('times', {}).get('est_time_enroute', '')
            if time_enroute:
                try:
                    total_seconds = int(time_enroute)
                    hours = total_seconds // 3600
                    minutes = (total_seconds % 3600) // 60
                    time = f"{hours}h {minutes}m"
                except:
                    time = time_enroute
            else:
                time = ''
            
            airline_name = self.get_airline_name_for_icao(airline_icao)
            
            return {
                'airline': airline_name or airline_icao,
                'callsign': callsign,
                'aircraft': aircraft,
                'flight_number': flight_number,
                'departure_icao': departure_icao,
                'departure_name': departure_name,
                'arrival_icao': arrival_icao,
                'arrival_name': arrival_name,
                'distance': distance,
                'time': time
            }
        except Exception as e:
            return None
    
    def get_callsign_for_airline(self, airline_icao):
        if not airline_icao:
            return ''
        
        try:
            from core.route_loader import get_airline_files, load_airline_data
            
            airline_files = get_airline_files()
            for airline_name in airline_files.keys():
                try:
                    airline_data = load_airline_data(airline_name)
                    if airline_data.get('icao', '').upper() == airline_icao.upper():
                        return airline_data.get('callsign', '')
                except:
                    continue
        except Exception as e:
            print(f"Error getting callsign: {e}")
        
        return ''
    
    def get_airline_name_for_icao(self, airline_icao):
        if not airline_icao:
            return ''
        
        try:
            from core.route_loader import get_airline_files, load_airline_data
            
            airline_files = get_airline_files()
            for airline_name in airline_files.keys():
                try:
                    airline_data = load_airline_data(airline_name)
                    if airline_data.get('icao', '').upper() == airline_icao.upper():
                        return airline_name
                except:
                    continue
        except Exception as e:
            print(f"Error getting airline name: {e}")
        
        return ''
    
    def fetch_vatsim_controllers(self, departure_icao, departure_iata, arrival_icao, arrival_iata):
        try:
            import requests
            VATSIM_DATA_URL = "https://data.vatsim.net/v3/vatsim-data.json"
            
            response = requests.get(VATSIM_DATA_URL, timeout=10)
            response.raise_for_status()
            data = response.json()

            dep_pattern = re.compile(
                rf"^({departure_icao}|{departure_iata})_.*?(DEL|GND|TWR|APP|DEP|CTR)",
                re.IGNORECASE
            )
            arr_pattern = re.compile(
                rf"^({arrival_icao}|{arrival_iata})_.*?(DEL|GND|TWR|APP|DEP|CTR)",
                re.IGNORECASE
            )
            
            dep_controllers = []
            arr_controllers = []
            
            for controller in data.get("controllers", []):
                callsign = controller.get("callsign", "")
                frequency = controller.get("frequency", "N/A")
                
                if dep_pattern.search(callsign):
                    dep_controllers.append(f"{callsign:<20} {frequency}")
                elif arr_pattern.search(callsign):
                    arr_controllers.append(f"{callsign:<20} {frequency}")
            
            return dep_controllers, arr_controllers
            
        except Exception as e:
            return [], []
    
    def get_iata_for_icao(self, icao_code, airline_name=None):
        """Get IATA code for an ICAO code by looking up routes"""
        if not icao_code:
            return icao_code
        
        try:
            from core.route_loader import get_airline_files, load_airline_data
            
            airlines_to_search = []
            if airline_name:
                airlines_to_search.append(airline_name)

            airline_files = get_airline_files()
            airlines_to_search.extend([name for name in airline_files.keys() if name != airline_name])
            
            for airline in airlines_to_search:
                try:
                    airline_data = load_airline_data(airline)
                    routes = airline_data.get('routes', [])
                    
                    for route in routes:
                        if route.get('from_icao', '').upper() == icao_code.upper():
                            return route.get('from', icao_code)
                        elif route.get('to_icao', '').upper() == icao_code.upper():
                            return route.get('to', icao_code)
                except:
                    continue
        except Exception as e:
            pass
        
        return icao_code
    
    def update_flight_summary(self, flight_data, from_simbrief=False):
        callsign = flight_data.get('callsign', '')
        flight_num_only = flight_data.get('flight_number', '').split()[-1] if flight_data.get('flight_number') else ''
        spoken_callsign = f"{callsign} {flight_num_only}" if callsign and flight_num_only else "N/A"
        
        airline_name = flight_data.get('airline', '')
        departure_icao = flight_data.get('departure_icao', '')
        arrival_icao = flight_data.get('arrival_icao', '')
        departure_iata = flight_data.get('departure_iata', '') or self.get_iata_for_icao(departure_icao, airline_name)
        arrival_iata = flight_data.get('arrival_iata', '') or self.get_iata_for_icao(arrival_icao, airline_name)
        
        dep_controllers, arr_controllers = self.fetch_vatsim_controllers(
            departure_icao, departure_iata, arrival_icao, arrival_iata
        )
        
        dep_controllers_text = "\n  ".join(dep_controllers) if dep_controllers else "  No active controllers"
        arr_controllers_text = "\n  ".join(arr_controllers) if arr_controllers else "  No active controllers"
        
        details_text = f"""
╔══════════════════════════════════════════════════════════════╗
║                      FLIGHT INFORMATION                      ║
╚══════════════════════════════════════════════════════════════╝

  Airline:           {flight_data.get('airline', 'N/A')}
  Callsign:          {flight_data.get('callsign', 'N/A')}
  Aircraft:          {flight_data.get('aircraft', 'N/A')}
  Flight Number:     {flight_data.get('flight_number', 'N/A')}

╔══════════════════════════════════════════════════════════════╗
║                         ROUTE DETAILS                        ║
╚══════════════════════════════════════════════════════════════╝

  Departure:         {flight_data.get('departure_icao', '')} - {flight_data.get('departure_name', '')}
  Arrival:           {flight_data.get('arrival_icao', '')} - {flight_data.get('arrival_name', '')}
  Distance:          {flight_data.get('distance', 'N/A')}
  Estimated Time:    {flight_data.get('time', 'N/A')}

╔══════════════════════════════════════════════════════════════╗
║                            VATSIM                            ║
╚══════════════════════════════════════════════════════════════╝

  Spoken Callsign:   {spoken_callsign}

  Active Controllers at {departure_icao}:
  {dep_controllers_text}

  Active Controllers at {arrival_icao}:
  {arr_controllers_text}

  Note: VATSIM controller data may be inaccurate. Please verify
        on vatsim-radar for the most up-to-date information.
"""
        
        self.flight_details_text.setPlainText(details_text)
        
        if from_simbrief:
            self.subtitle.setText("Flight plan fetched from SimBrief")
        else:
            self.subtitle.setText("Your flight plan has been sent to SimBrief")
        
        self.stacked_widget.setCurrentIndex(1)
    
    def clear_flight_plan(self):
        self.stacked_widget.setCurrentIndex(0)
    
    def show_empty_state(self):
        self.stacked_widget.setCurrentIndex(0)
