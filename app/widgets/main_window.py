from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow

from app.widgets.auto.main_window import Ui_MainWindow
from app.widgets.database_view import DatabaseView
from app.widgets.dialogs.connect_to_db import ConnectToDBDialog


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.db_view = DatabaseView("please-select-a-db-first")
        self.setCentralWidget(self.db_view)

        self._init_ui()
        self._connect_slots()

    def _init_ui(self):
        if self.db_view.db_name == "please-select-a-db-first":
            if not self.connect_to_new_database():
                QApplication.quit()
        self.resize_to_almost_full_screen()

    def resize_to_almost_full_screen(self):
        size = QSize(QApplication.primaryScreen().size())
        self.setGeometry(100, 100, size.width() - 200, size.height() - 200)

    def connect_to_new_database(self):
        dialog = ConnectToDBDialog()
        dialog.exec()
        if not dialog.db_name:
            return False
        self.db_view = DatabaseView(dialog.db_name)
        self.setCentralWidget(self.db_view)
        return True

    def _connect_slots(self):
        self.a_connect_to_db.triggered.connect(self.connect_to_new_database)
