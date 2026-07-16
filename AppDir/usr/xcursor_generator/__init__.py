# xcursor_generator/__init__.py
import sys
from PyQt6.QtWidgets import QApplication
from xcursor_generator.gui import XCursorGenerator
from xcursor_generator.version import __version__

def main():
    app = QApplication(sys.argv)
    window = XCursorGenerator(__version__)
    window.show()
    sys.exit(app.exec())
