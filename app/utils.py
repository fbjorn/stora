from pathlib import Path

from PySide6.QtWidgets import QApplication
from qt_material import apply_stylesheet

from app.settings import conf


def apply_theme(app: QApplication, patch=False):
    if conf.material_theme:
        apply_stylesheet(app, theme=conf.material_theme)
        if patch:
            qss = Path(__file__).parent.parent / "assets" / "styles.qss"
            stylesheet = app.styleSheet()
            app.setStyleSheet(stylesheet + qss.read_text())
