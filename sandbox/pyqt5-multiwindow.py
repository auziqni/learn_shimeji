# main.py - QApplication & QMainWindow Explained
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QPushButton, QLabel, QMenuBar, QStatusBar, QToolBar, QAction)
from PyQt5.QtCore import Qt
import sys

class SimpleWidget(QWidget):
    """
    QWidget Example (Basic Container)
    HTML equivalent: <div> dengan basic content
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Simple QWidget Window")
        self.setGeometry(100, 100, 300, 200)
        
        # Simple layout
        layout = QVBoxLayout()
        layout.addWidget(QLabel("This is a basic QWidget"))
        layout.addWidget(QPushButton("Simple Button"))
        
        self.setLayout(layout)

class FullMainWindow(QMainWindow):
    """
    QMainWindow Example (Full Application Structure)
    HTML equivalent: Complete webpage dengan header, main, footer
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Full QMainWindow Application")
        self.setGeometry(200, 200, 600, 400)
        
        # Setup all components
        self.setup_menu_bar()      # <header> dengan navigation
        self.setup_tool_bar()      # <nav> dengan quick actions  
        self.setup_central_widget() # <main> content area
        self.setup_status_bar()    # <footer> dengan status info
        
    def setup_menu_bar(self):
        """
        Menu Bar (seperti <header><nav> di HTML)
        Classic desktop app navigation
        """
        menubar = self.menuBar()  # QMainWindow built-in method
        
        # File Menu
        file_menu = menubar.addMenu('File')
        
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')  
        file_menu.addAction(open_action)
        
        file_menu.addSeparator()  # Divider line
        
        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        edit_menu.addAction('Copy')
        edit_menu.addAction('Paste')
        
        # Help Menu
        help_menu = menubar.addMenu('Help')
        help_menu.addAction('About')
        
    def setup_tool_bar(self):
        """
        Tool Bar (seperti quick action buttons)
        Common actions yang sering digunakan
        """
        toolbar = self.addToolBar('Main Toolbar')  # QMainWindow method
        
        # Add quick action buttons
        new_action = QAction('New', self)
        new_action.triggered.connect(self.new_file)
        toolbar.addAction(new_action)
        
        save_action = QAction('Save', self)
        toolbar.addAction(save_action)
        
        toolbar.addSeparator()  # Separator
        
        settings_action = QAction('Settings', self)
        toolbar.addAction(settings_action)
        
    def setup_central_widget(self):
        """
        Central Widget (seperti <main> content area)
        Main content area - WAJIB ada di QMainWindow
        """
        # QMainWindow HARUS punya central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)  # QMainWindow method
        
        # Layout untuk central widget
        layout = QVBoxLayout(central_widget)
        
        # Main content
        title = QLabel("Main Content Area")
        title.setStyleSheet("font-size: 18px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        description = QLabel("""
        This is the central widget area of QMainWindow.
        
        QMainWindow provides:
        • Menu bar (File, Edit, Help)
        • Tool bar (Quick actions)  
        • Central widget (Main content)
        • Status bar (Bottom info)
        
        Perfect for full desktop applications!
        """)
        description.setWordWrap(True)
        description.setStyleSheet("margin: 20px; line-height: 1.5;")
        layout.addWidget(description)
        
        # Some interactive content
        button = QPushButton("Click to Update Status")
        button.clicked.connect(self.update_status)
        layout.addWidget(button)
        
    def setup_status_bar(self):
        """
        Status Bar (seperti <footer> dengan info)
        Shows app status, progress, info messages
        """
        statusbar = self.statusBar()  # QMainWindow built-in method
        statusbar.showMessage("Ready - QMainWindow Application Started")
        
    # Event handlers
    def new_file(self):
        """Handle New File action"""
        print("New file created!")
        self.statusBar().showMessage("New file created", 2000)  # Show for 2 seconds
        
    def update_status(self):
        """Update status bar when button clicked"""
        self.statusBar().showMessage("Button was clicked!", 3000)

class QApplicationDemo:
    """
    QApplication Demo & Explanation
    Shows how QApplication manages multiple windows
    """
    def __init__(self):
        # STEP 1: Create QApplication (WAJIB - hanya satu per aplikasi)
        self.app = QApplication(sys.argv)
        
        # Set application properties
        self.app.setApplicationName("PyQt5 Demo App")
        self.app.setApplicationVersion("1.0")
        
        # Global styling (affects ALL windows)
        self.app.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                padding: 8px 16px;
                background-color: #007ACC;
                color: white;
                border: none;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #005a9e;
            }
        """)
        
        # Create windows
        self.create_windows()
        
    def create_windows(self):
        """Create and show multiple windows"""
        
        # Window 1: Simple QWidget
        self.simple_window = SimpleWidget()
        self.simple_window.show()
        
        # Window 2: Full QMainWindow  
        self.main_window = FullMainWindow()
        self.main_window.show()
        
        # QApplication akan manage kedua windows ini
        print(" QApplication managing 2 windows:")
        print("   1. Simple QWidget window")
        print("   2. Full QMainWindow application")
        
    def run(self):
        """Start the application event loop"""
        print("\n🚀 Starting QApplication event loop...")
        print("   - QApplication now listening for events")
        print("   - Close both windows to exit application")
        
        # STEP 2: Start event loop (seperti browser event loop)
        # Program akan 'hang' di sini sampai semua windows ditutup
        exit_code = self.app.exec_()
        
        print(f"\n👋 Application closed with exit code: {exit_code}")
        return exit_code

def main():
    """
    Main function demonstrating QApplication lifecycle
    """
    print("=== QApplication & QMainWindow Demo ===\n")
    
    # Create and run application
    demo = QApplicationDemo()
    return demo.run()

if __name__ == "__main__":
    sys.exit(main())

"""
QAPPLICATION vs QMAINWINDOW EXPLAINED:

QAPPLICATION (App Engine):
app = QApplication(sys.argv)     ↔ Browser engine untuk desktop
app.setApplicationName()         ↔ <title> tag  
app.setStyleSheet()             ↔ Global CSS stylesheet
app.exec_()                     ↔ Event loop (like browser event handling)

QAPPLICATION FEATURES:
• System Integration             ↔ Browser's OS integration
• Event Management              ↔ Browser's event system (click, key, etc)
• Multi-Window Management       ↔ Browser's tab/window management
• Global Styling                ↔ Global CSS styles
• Application Lifecycle         ↔ Browser session management

QWIDGET vs QMAINWINDOW:

QWIDGET (Basic Container):
QWidget()                       ↔ <div> - simple container
setLayout()                     ↔ CSS layout (flexbox/grid)
addWidget()                     ↔ appendChild()

QMAINWINDOW (Full App Structure):
QMainWindow()                   ↔ <html> - complete page structure
menuBar()                       ↔ <header><nav> - main navigation
addToolBar()                    ↔ <nav> - quick actions toolbar
setCentralWidget()              ↔ <main> - main content area
statusBar()                     ↔ <footer> - status information

WHEN TO USE WHAT:

USE QWIDGET WHEN:
• Simple dialogs                ↔ Modal popups
• Custom components             ↔ Reusable components
• Embedded panels               ↔ Widget inside larger app

USE QMAINWINDOW WHEN:
• Full desktop applications     ↔ Complete web applications
• Need menu/toolbar/statusbar   ↔ Need header/nav/footer
• Professional app interface    ↔ Business web applications
• Document-based applications   ↔ Text editors, IDEs, etc.

TYPICAL STRUCTURE:
app = QApplication(sys.argv)    # Create app engine
window = QMainWindow()          # Create main window
window.show()                   # Show window
sys.exit(app.exec_())          # Run until closed
"""