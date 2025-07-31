# main.py - Simple Control Panel dengan 4 Tabs

from PyQt5.QtWidgets import QApplication
import sys

from control_panel import ControlPanel
from utils.xml_parser import XMLParser


def main():
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Teknisee Shimeji TikTok")
    app.setApplicationVersion("0.1.0")
    
    # Create dan show window
    window = ControlPanel()
    window.show()
    
    parser = XMLParser()
    sprite_packs = parser.load_all_sprite_packs()
    parser.print_summary()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
