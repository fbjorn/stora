import os
import sys

from PySide6.QtWidgets import QApplication

from app.utils import apply_theme
from app.widgets.main_window import MainWindow

os.environ["FIRESTORE_EMULATOR_HOST"] = "localhost:8686"


def main():
    app = QApplication([])
    mw = MainWindow()
    apply_theme(app, patch=True)
    mw.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
