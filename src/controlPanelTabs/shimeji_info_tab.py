from PyQt5.QtWidgets import (QWidget, QVBoxLayout,QLabel)
from PyQt5.QtCore import Qt

class ShimejiInfoTab(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()

    def setup_ui(self):
        """
        Tab 1: Shimeji Settings
        Untuk pengaturan pet behavior, sprites, etc.
        """
        layout = QVBoxLayout(self)
        
        # Tab title
        title = QLabel("Shimeji Settings")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin: 10px;")
        layout.addWidget(title)
        
        # Construction message
        construction_label = QLabel("🚧 ON CONSTRUCTION")
        construction_label.setAlignment(Qt.AlignCenter)
        construction_label.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #e67e22;
                background-color: #fef9e7;
                border: 2px dashed #f39c12;
                border-radius: 10px;
                padding: 40px;
                margin: 20px;
            }
        """)
        layout.addWidget(construction_label)
        
        # Description
        description = QLabel("""
        Future features akan include:
        • Pet behavior settings
        • Sprite pack selection  
        • Animation speed control
        • Pet interaction settings
        • Spawn location preferences
        """)
        description.setAlignment(Qt.AlignCenter)
        description.setStyleSheet("color: #7f8c8d; margin: 20px; line-height: 1.5;")
        layout.addWidget(description)
        
        layout.addStretch()  # Push content to top
        return layout

