# main.py - PyQt5 Responsive Layout Demo
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QGridLayout, QPushButton, QLabel, 
                           QTextEdit, QSplitter, QFrame)
from PyQt5.QtCore import Qt
import sys

class ResponsiveDemo(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("PyQt5 Responsive Layout Demo")
        self.setGeometry(200, 200, 800, 600)
        self.setMinimumSize(400, 300)  # Minimum window size
        
        # Central widget (required for QMainWindow)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        
        # 1. RESPONSIVE HEADER
        header = self.create_responsive_header()
        main_layout.addWidget(header)
        
        # 2. RESPONSIVE CONTENT AREA
        content = self.create_responsive_content()
        main_layout.addWidget(content, 1)  # stretch factor = 1 (flex-grow: 1)
        
        # 3. RESPONSIVE FOOTER
        footer = self.create_responsive_footer()
        main_layout.addWidget(footer)
        
    def create_responsive_header(self):
        """
        Responsive Header (seperti navbar yang auto-adjust)
        HTML/CSS equivalent: 
        .header { display: flex; justify-content: space-between; }
        """
        header_frame = QFrame()
        header_frame.setFrameStyle(QFrame.StyledPanel)
        header_frame.setStyleSheet("""
            QFrame {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(header_frame)  # display: flex; flex-direction: row;
        
        # Logo/Title (fixed width)
        title = QLabel("Responsive App")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        # Spacer (flex-grow: 1 - takes remaining space)
        layout.addStretch()  # ↔ margin-left: auto in CSS
        
        # Navigation buttons (fixed width)
        nav_buttons = ["Home", "About", "Contact"]
        for btn_text in nav_buttons:
            btn = QPushButton(btn_text)
            btn.setStyleSheet("""
                QPushButton {
                    background-color: #34495e;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    margin: 0 2px;
                }
                QPushButton:hover {
                    background-color: #4a6741;
                }
            """)
            layout.addWidget(btn)
        
        return header_frame
    
    def create_responsive_content(self):
        """
        Responsive Content Area dengan Splitter
        HTML/CSS equivalent:
        .content { display: flex; } dengan resizable panels
        """
        # QSplitter = Resizable panels (seperti CSS Grid dengan drag handles)
        splitter = QSplitter(Qt.Horizontal)
        
        # LEFT PANEL - Sidebar
        sidebar = self.create_sidebar()
        splitter.addWidget(sidebar)
        
        # RIGHT PANEL - Main content
        main_content = self.create_main_content()
        splitter.addWidget(main_content)
        
        # Set initial sizes (30% sidebar, 70% main content)
        splitter.setSizes([240, 560])  # 30% of 800px = 240px
        
        # Responsive behavior: minimum sizes
        splitter.setChildrenCollapsible(False)  # Prevent panels from collapsing
        
        return splitter
    
    def create_sidebar(self):
        """
        Responsive Sidebar
        HTML/CSS equivalent: 
        .sidebar { min-width: 200px; max-width: 300px; }
        """
        sidebar_frame = QFrame()
        sidebar_frame.setFrameStyle(QFrame.StyledPanel)
        sidebar_frame.setStyleSheet("""
            QFrame {
                background-color: #ecf0f1;
                min-width: 200px;
                max-width: 300px;
            }
        """)
        
        layout = QVBoxLayout(sidebar_frame)
        
        # Sidebar title
        title = QLabel("Sidebar Menu")
        title.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Menu items (responsive buttons)
        menu_items = ["Dashboard", "Profile", "Settings", "Reports", "Help"]
        for item in menu_items:
            btn = QPushButton(item)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 10px;
                    border: none;
                    background-color: transparent;
                }
                QPushButton:hover {
                    background-color: #bdc3c7;
                }
            """)
            layout.addWidget(btn)
        
        # Push menu items to top
        layout.addStretch()  # ↔ margin-top: auto
        
        return sidebar_frame
    
    def create_main_content(self):
        """
        Responsive Main Content Area
        HTML/CSS equivalent:
        .main-content { flex: 1; display: grid; grid-template-rows: auto 1fr; }
        """
        main_frame = QFrame()
        main_frame.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout(main_frame)
        
        # Content header
        content_header = QLabel("Main Content Area")
        content_header.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px;")
        layout.addWidget(content_header)
        
        # Responsive grid content
        grid_content = self.create_responsive_grid()
        layout.addWidget(grid_content, 1)  # flex-grow: 1
        
        # Text area (responsive)
        text_area = QTextEdit()
        text_area.setPlaceholderText("This text area will resize with the window...")
        text_area.setStyleSheet("margin: 10px; padding: 10px;")
        layout.addWidget(text_area, 1)  # flex-grow: 1
        
        return main_frame
    
    def create_responsive_grid(self):
        """
        Responsive Grid Layout
        HTML/CSS equivalent:
        display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
        """
        grid_frame = QFrame()
        grid_layout = QGridLayout(grid_frame)
        
        # Create responsive cards
        cards_data = [
            ("Card 1", "#e74c3c"), ("Card 2", "#3498db"),
            ("Card 3", "#2ecc71"), ("Card 4", "#f39c12")
        ]
        
        for i, (title, color) in enumerate(cards_data):
            card = self.create_responsive_card(title, color)
            row = i // 2  # 2 cards per row
            col = i % 2
            grid_layout.addWidget(card, row, col)
        
        # Make cards responsive
        grid_layout.setColumnStretch(0, 1)  # Column 0 can grow
        grid_layout.setColumnStretch(1, 1)  # Column 1 can grow
        
        return grid_frame
    
    def create_responsive_card(self, title, color):
        """
        Responsive Card Component
        HTML/CSS equivalent:
        .card { min-width: 150px; flex: 1; }
        """
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                color: white;
                border-radius: 8px;
                margin: 5px;
                min-width: 150px;
                min-height: 100px;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        card_title = QLabel(title)
        card_title.setAlignment(Qt.AlignCenter)
        card_title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(card_title)
        
        card_content = QLabel("Responsive content")
        card_content.setAlignment(Qt.AlignCenter)
        layout.addWidget(card_content)
        
        return card
    
    def create_responsive_footer(self):
        """
        Responsive Footer
        HTML/CSS equivalent:
        .footer { display: flex; justify-content: center; }
        """
        footer_frame = QFrame()
        footer_frame.setFrameStyle(QFrame.StyledPanel)
        footer_frame.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                color: white;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(footer_frame)
        
        # Center the footer content
        layout.addStretch()  # Left spacer
        
        footer_text = QLabel("© 2024 Responsive PyQt5 App")
        footer_text.setAlignment(Qt.AlignCenter)
        layout.addWidget(footer_text)
        
        layout.addStretch()  # Right spacer
        
        return footer_frame
    
    def resizeEvent(self, event):
        """
        Handle window resize events (seperti window.onresize di JS)
        Custom responsive behavior bisa ditambahkan di sini
        """
        super().resizeEvent(event)
        
        # Get new window size
        new_size = event.size()
        width = new_size.width()
        height = new_size.height()
        
        # Custom responsive logic berdasarkan ukuran
        if width < 600:
            # Small screen behavior
            self.setWindowTitle(f"Responsive App (Small: {width}x{height})")
        elif width < 900:
            # Medium screen behavior  
            self.setWindowTitle(f"Responsive App (Medium: {width}x{height})")
        else:
            # Large screen behavior
            self.setWindowTitle(f"Responsive App (Large: {width}x{height})")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide responsive behavior
    app.setStyleSheet("""
        /* Global responsive styles */
        * {
            font-family: Arial, sans-serif;
        }
    """)
    
    window = ResponsiveDemo()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

"""
PYQT5 RESPONSIVENESS CONCEPTS:

LAYOUT RESPONSIVENESS:
QVBoxLayout/QHBoxLayout    ↔ CSS Flexbox (flex-direction: column/row)
addStretch()               ↔ flex-grow: 1 (expand to fill space)
stretch_factor             ↔ flex: [number] (relative sizing)
QGridLayout                ↔ CSS Grid (responsive grid system)
QSplitter                  ↔ Resizable panels with drag handles

SIZE POLICIES:
widget.setSizePolicy()     ↔ CSS min-width, max-width, flex properties
setMinimumSize()          ↔ min-width, min-height
setMaximumSize()          ↔ max-width, max-height
sizeHint()                ↔ Preferred/default size

RESPONSIVE TECHNIQUES:
1. STRETCH FACTORS:
layout.addWidget(widget, stretch_factor)  ↔ flex: [number]

2. SPLITTERS:
QSplitter(Qt.Horizontal)   ↔ Resizable columns
QSplitter(Qt.Vertical)     ↔ Resizable rows

3. GRID RESPONSIVENESS:
setColumnStretch(col, factor)  ↔ grid-template-columns with fr units
setRowStretch(row, factor)     ↔ grid-template-rows with fr units

4. WINDOW RESIZE HANDLING:
resizeEvent()              ↔ window.addEventListener('resize', ...)

5. MINIMUM/MAXIMUM CONSTRAINTS:
setMinimumSize()          ↔ min-width/min-height
setMaximumSize()          ↔ max-width/max-height

RESPONSIVE BEST PRACTICES:
- Use layouts instead of fixed positioning
- Set minimum/maximum sizes appropriately  
- Use stretch factors for proportional sizing
- Handle window resize events for custom behavior
- Test on different screen sizes
- Consider mobile-first approach for scalability
"""