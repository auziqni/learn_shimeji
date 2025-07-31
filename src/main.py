# main.py - Simple Control Panel dengan 4 Tabs

from PyQt5.QtWidgets import QApplication
import sys

from control_panel import ControlPanel


def main():
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Teknisee Shimeji TikTok")
    app.setApplicationVersion("0.1.0")
    
    # Create dan show window
    window = ControlPanel()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
