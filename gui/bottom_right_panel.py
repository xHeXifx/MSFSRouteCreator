from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton
from PySide6.QtCore import Signal


class BottomRightPanel(QWidget):
    generate_clicked = Signal()
    simbrief_clicked = Signal()
    close_clicked = Signal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.generate_btn = QPushButton("Generate Flight Plan")
        self.generate_btn.clicked.connect(self.generate_clicked.emit)
        layout.addWidget(self.generate_btn)
        
        self.simbrief_btn = QPushButton("Open in SimBrief")
        self.simbrief_btn.setEnabled(False)
        self.simbrief_btn.clicked.connect(self.simbrief_clicked.emit)
        layout.addWidget(self.simbrief_btn)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.close_clicked.emit)
        layout.addWidget(self.close_btn)
        
        layout.addStretch()
        self.setLayout(layout)
    
    def enable_simbrief(self, enabled=True):
        self.simbrief_btn.setEnabled(enabled)
