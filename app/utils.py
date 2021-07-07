from pathlib import Path

from PySide6.QtWidgets import QApplication, QWidget
from qt_material import apply_stylesheet

from app.settings import conf


def apply_theme(app: QApplication, patch=False):
    if conf.material_theme:
        apply_stylesheet(app, theme=conf.material_theme)
        if patch:
            qss = Path(__file__).parent.parent / "assets" / "styles.qss"
            stylesheet = app.styleSheet()
            app.setStyleSheet(stylesheet + qss.read_text())


def apply_debug_css_borders(widget: QWidget):
    if hasattr(widget, "setStyleSheet"):
        ss = widget.styleSheet()
        widget.setStyleSheet(f"{ss}\nborder: 1px solid black")
    for child in widget.children():
        apply_debug_css_borders(child)
