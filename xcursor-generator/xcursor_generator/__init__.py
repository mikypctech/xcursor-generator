# xcursor_generator/__init__.py
import sys
from PyQt6.QtWidgets import QApplication
from xcursor_generator.gui import XCursorGenerator

def main():
    app = QApplication(sys.argv)
    window = XCursorGenerator()
    window.show()
    sys.exit(app.exec())
