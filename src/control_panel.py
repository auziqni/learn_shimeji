from PyQt5.QtWidgets import ( QMainWindow, QWidget, QVBoxLayout, 
                           QTabWidget, QLabel)
from PyQt5.QtCore import Qt

from controlPanelTabs import ShimejiSettingsTab,GeneralSettingsTab,ShimejiInfoTab,TiktokSettingsTab


class ControlPanel(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        """Setup UI components"""
        self.setWindowTitle("Shimeji Control Panel")
        self.setGeometry(300, 300, 1000, 600)
        self.setMinimumSize(400, 300)
        
        # Central widget (required untuk QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # Header
        header = self.create_header()
        main_layout.addWidget(header)
        
        # Tab widget (main content)
        tab_widget = self.create_tab_widget()
        main_layout.addWidget(tab_widget, 1)  # stretch factor = 1
        
    def create_header(self):
        """
        Create header section
        Simple title untuk control panel
        """
        header_label = QLabel("🎮 Teknisee Shimeji TikTok Control Panel")
        header_label.setAlignment(Qt.AlignCenter)
        header_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-bottom: 2px solid #bdc3c7;
            }
        """)
        return header_label
        
    def create_tab_widget(self):
        """
        Create tab widget dengan 4 tabs
        HTML equivalent: <nav><ul class="tabs">
        """
        tab_widget = QTabWidget()
        
        # Tab styling
        tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #bdc3c7;
                background-color: white;
            }
            
            QTabBar::tab {
                background-color: #ecf0f1;
                color: #2c3e50;
                padding: 10px 15px;
                margin-right: 2px;
                border: 1px solid #bdc3c7;
                border-bottom: none;
            }
            
            QTabBar::tab:selected {
                background-color: white;
                color: #e74c3c;
                font-weight: bold;
            }
            
            QTabBar::tab:hover {
                background-color: #d5dbdb;
            }
        """)
        ShimajiSettingTab = ShimejiSettingsTab()
        create_general_settings_tab = GeneralSettingsTab()
        create_shimeji_info_tab = ShimejiInfoTab()
        create_tiktok_settings_tab = TiktokSettingsTab()
        
        
         # Create dan add tabs
        tab_widget.addTab(ShimajiSettingTab, "🐾 Shimeji Settings")
        tab_widget.addTab(create_general_settings_tab, "⚙️ General Settings") 
        tab_widget.addTab(create_shimeji_info_tab, "📊 Shimeji Info")
        tab_widget.addTab(create_tiktok_settings_tab, "🎵 TikTok Settings")
        
        return tab_widget

    def MockTabWidget(self):
        """
        Mock tab widget untuk testing purposes
        """
        mock_tab_widget = QTabWidget()
        mock_tab_widget.addTab(QWidget(), "Mock Tab 1")
        mock_tab_widget.addTab(QWidget(), "Mock Tab 2")
        return mock_tab_widget