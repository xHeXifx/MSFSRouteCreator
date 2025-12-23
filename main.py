import sys
import os

def main():    
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
