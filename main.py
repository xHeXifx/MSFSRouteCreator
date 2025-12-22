import sys
import os

def main():    
    dataFiles = ['british_airways_routes.json', 'easyjet_routes.json', 'emirates_routes.json', 'ryanair_routes.json', 'lufthansa_routes.json', 'singapore_airlines_routes.json', 'qatar_airways_routes.json']
    assetFiles = ['British Airways.png', 'easyJet.png', 'Emirates.png', 'Lufthansa.png', 'Ryanair.jpg', 'Singapore Airlines.png', 'Qatar Airways.jpg']
    for file in dataFiles:
        if not os.path.exists(f'data/{file}'):
            print(f"Missing file {file}! Run buildData.py to fix.")
            sys.exit()
        
    for file in assetFiles:
        if not os.path.exists(f'assets/{file}') and (len(sys.argv) > 1 and sys.argv[1] == '-cli'):
            print(f'Missing asset {file}! This will affect GUI usage, you can still use CLI.')
    

    if len(sys.argv) > 1 and sys.argv[1] == '-cli':
        from core.cli import run_cli
        run_cli()
    else:
        from PySide6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("MSFS Route Creator")
        
        window = MainWindow()
        window.show()
        
        sys.exit(app.exec())


if __name__ == "__main__":
    main()
