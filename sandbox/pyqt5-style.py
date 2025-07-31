# main.py - PyQt5 Layouts Demo (HTML/CSS Style)
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                           QGridLayout, QLabel, QPushButton, QLineEdit)
from PyQt5.QtCore import Qt
import sys

class LayoutDemo(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        
    def setup_ui(self):
        self.setWindowTitle("PyQt5 Layouts = HTML/CSS")
        self.setGeometry(200, 200, 600, 400)
        
        # MAIN CONTAINER (seperti <body>)
        main_layout = QVBoxLayout()
        
        # 1. HEADER SECTION (seperti <header>)
        header = self.create_header_section()
        main_layout.addWidget(header)
        
        # 2. CONTENT SECTION (seperti <main>)
        content = self.create_content_section()
        main_layout.addWidget(content)
        
        # 3. FOOTER SECTION (seperti <footer>)
        footer = self.create_footer_section()
        main_layout.addWidget(footer)
        
        self.setLayout(main_layout)
    
    def create_header_section(self):
        """
        HTML equivalent:
        <header style="background: lightblue; padding: 10px;">
          <h1>My App</h1>
        </header>
        """
        header_widget = QWidget()
        
        # CSS-like styling
        header_widget.setStyleSheet("""
            QWidget {
                background-color: lightblue;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout()  # flex-direction: row
        
        title = QLabel("My App Header")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")  # CSS styling
        layout.addWidget(title)
        
        # Spacer (seperti margin-left: auto di CSS)
        layout.addStretch()
        
        login_btn = QPushButton("Login")
        layout.addWidget(login_btn)
        
        header_widget.setLayout(layout)
        return header_widget
    
    def create_content_section(self):
        """
        HTML equivalent:
        <main style="display: flex;">
          <aside>Sidebar</aside>
          <section>Main Content</section>
        </main>
        """
        content_widget = QWidget()
        layout = QHBoxLayout()  # display: flex
        
        # SIDEBAR (seperti <aside>)
        sidebar = QWidget()
        sidebar.setStyleSheet("""
            QWidget {
                background-color: lightgray;
                min-width: 150px;
                max-width: 150px;
            }
        """)
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(QLabel("Sidebar"))
        sidebar_layout.addWidget(QPushButton("Menu 1"))
        sidebar_layout.addWidget(QPushButton("Menu 2"))
        sidebar_layout.addStretch()  # flex-grow: 1
        sidebar.setLayout(sidebar_layout)
        
        # MAIN CONTENT (seperti <section>)
        main_content = self.create_main_content()
        
        # Add ke horizontal layout
        layout.addWidget(sidebar)        # flex: 0 0 150px
        layout.addWidget(main_content)   # flex: 1
        
        content_widget.setLayout(layout)
        return content_widget
    
    def create_main_content(self):
        """
        HTML equivalent:
        <section style="padding: 20px;">
          <form>
            <div class="form-group">
              <label>Name:</label>
              <input type="text">
            </div>
          </form>
        </section>
        """
        main_widget = QWidget()
        main_widget.setStyleSheet("padding: 20px;")
        
        # GRID LAYOUT (seperti CSS Grid)
        layout = QGridLayout()  # display: grid
        
        # Form-style layout
        layout.addWidget(QLabel("Name:"), 0, 0)           # row 0, col 0
        layout.addWidget(QLineEdit(), 0, 1)               # row 0, col 1
        
        layout.addWidget(QLabel("Email:"), 1, 0)          # row 1, col 0
        layout.addWidget(QLineEdit(), 1, 1)               # row 1, col 1
        
        layout.addWidget(QLabel("Age:"), 2, 0)            # row 2, col 0
        layout.addWidget(QLineEdit(), 2, 1)               # row 2, col 1
        
        submit_btn = QPushButton("Submit")
        layout.addWidget(submit_btn, 3, 0, 1, 2)          # row 3, col 0-1 (span 2 cols)
        
        main_widget.setLayout(layout)
        return main_widget
    
    def create_footer_section(self):
        """
        HTML equivalent:
        <footer style="background: darkgray; text-align: center;">
          <p>Footer Content</p>
        </footer>
        """
        footer_widget = QWidget()
        footer_widget.setStyleSheet("""
            QWidget {
                background-color: darkgray;
                color: white;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout()
        
        footer_text = QLabel("© 2024 My App - Footer Content")
        footer_text.setAlignment(Qt.AlignCenter)  # text-align: center
        layout.addWidget(footer_text)
        
        footer_widget.setLayout(layout)
        return footer_widget

def main():
    app = QApplication(sys.argv)
    window = LayoutDemo()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()

"""
MAPPING PyQt5 ↔ HTML/CSS:

STRUCTURE MAPPING:
QWidget()           ↔ <div>, <section>, <main>
QLabel()            ↔ <h1>, <h2>, <p>, <span>
QPushButton()       ↔ <button>
QLineEdit()         ↔ <input type="text">
QVBoxLayout()       ↔ flex-direction: column
QHBoxLayout()       ↔ flex-direction: row
QGridLayout()       ↔ display: grid

LAYOUT MAPPING:
addWidget()         ↔ appendChild() + flex item
addStretch()        ↔ flex-grow: 1 / margin-left: auto
setAlignment()      ↔ text-align, justify-content, align-items

STYLING MAPPING:
setStyleSheet()     ↔ <style> atau external CSS
background-color    ↔ background-color
padding            ↔ padding
font-size          ↔ font-size
border             ↔ border
:hover             ↔ :hover
:pressed           ↔ :active

EVENT MAPPING:
clicked.connect()   ↔ onclick="" atau addEventListener()
textChanged         ↔ oninput="" atau input event
valueChanged        ↔ onchange="" atau change event
"""

"""
CONTOH PENGGUNAAN SINGKAT:

WIDGETS (UI Elements):
# Text Display
label = QLabel("Hello")              ↔ <p>Hello</p>
label.setText("New Text")            ↔ element.textContent = "New Text"

# Button
btn = QPushButton("Click Me")        ↔ <button>Click Me</button>
btn.clicked.connect(my_function)     ↔ btn.onclick = my_function

# Text Input
input_field = QLineEdit()            ↔ <input type="text">
input_field.setText("default")       ↔ input.value = "default"
text = input_field.text()            ↔ text = input.value

# Slider
slider = QSlider(Qt.Horizontal)      ↔ <input type="range">
slider.setRange(0, 100)              ↔ min="0" max="100"
slider.setValue(50)                  ↔ value="50"

LAYOUTS (Positioning):
# Vertical Stack
layout = QVBoxLayout()               ↔ display: flex; flex-direction: column;
layout.addWidget(widget1)            ↔ <div>widget1</div>
layout.addWidget(widget2)            ↔ <div>widget2</div>

# Horizontal Stack  
layout = QHBoxLayout()               ↔ display: flex; flex-direction: row;
layout.addWidget(left_widget)        ↔ <div>left</div>
layout.addWidget(right_widget)       ↔ <div>right</div>

# Grid Layout
layout = QGridLayout()               ↔ display: grid;
layout.addWidget(widget, 0, 0)       ↔ grid-row: 1; grid-column: 1;
layout.addWidget(widget, 0, 1)       ↔ grid-row: 1; grid-column: 2;

# Spacing
layout.addStretch()                  ↔ flex-grow: 1; atau margin-left: auto;

STYLING (Appearance):
# CSS-like Styling
widget.setStyleSheet("color: red;")   ↔ style="color: red;"

widget.setStyleSheet("" "
    QPushButton {
        background-color: blue;          ↔ background-color: blue;
        color: white;                    ↔ color: white;
        border: 2px solid black;         ↔ border: 2px solid black;
        padding: 10px;                   ↔ padding: 10px;
        font-size: 14px;                 ↔ font-size: 14px;
    }
    QPushButton:hover {
        background-color: lightblue;     ↔ button:hover { background: lightblue; }
    }
"" ")

EVENTS (Interactions):
# Button Click
btn.clicked.connect(handle_click)     ↔ btn.addEventListener('click', handleClick)

# Text Change
input.textChanged.connect(on_change)  ↔ input.addEventListener('input', onChange)

# Slider Change
slider.valueChanged.connect(on_slide) ↔ slider.addEventListener('change', onSlide)

CONTAINER (Structure):
# Main Container
container = QWidget()                 ↔ <div class="container">
container.setLayout(layout)           ↔ CSS rules applied to container
parent.addWidget(container)           ↔ parent.appendChild(container)
"""