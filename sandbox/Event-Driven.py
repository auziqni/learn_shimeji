"""
main.py - Event-Driven Programming Example

This example demonstrates a simple event-driven application using PyQt5.
"""

from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QLabel
import sys

class window(QWidget):
    def __init__(self):
        super().__init__()
        self.counter = 0  # Simple counter for demonstration
        self.setup_ui()
        
    def setup_ui(self):
        # Create window
        self.setWindowTitle("Event-Driven Example")
        self.setGeometry(300, 300, 250, 150)
        
        # Create vertical layout
        layout = QVBoxLayout()
        
        # Label to show counter
        self.label = QLabel(f"Counter: {self.counter}")
        layout.addWidget(self.label)
        
        # Button that will trigger events
        self.button = QPushButton("Click Me!")
        # Connect button click event to handler function
        self.button.clicked.connect(self.on_button_clicked)
        
        layout.addWidget(self.button)
        
        # Reset button
        reset_btn = QPushButton("Reset")
        reset_btn.clicked.connect(self.on_reset_clicked)  # Connect another event
        layout.addWidget(reset_btn)
        
        self.setLayout(layout)
    
    # EVENT HANDLER FUNCTIONS
    def on_button_clicked(self):
        """Function called ONLY when the button is clicked"""
        self.counter += 1
        self.label.setText(f"Counter: {self.counter}")
        print(f"Button clicked! Counter now: {self.counter}")
    
    def on_reset_clicked(self):
        """Event handler for reset button"""
        self.counter = 0
        self.label.setText(f"Counter: {self.counter}")
        print("Counter reset!")


def main():
    
    # Create QApplication (required for all PyQt5 apps)
    app = QApplication(sys.argv)
    
    # Create window instance
    main_window = window()
    main_window.show()  # Show the window
    
    # Start the event loop
    sys.exit(app.exec_())    

if __name__ == "__main__":
    main()