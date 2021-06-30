from PySide6.QtWidgets import QMessageBox


def show_error(text: str, title="Error"):
    mb = QMessageBox()
    mb.setWindowTitle(title)
    mb.setText(text)
    mb.exec()
