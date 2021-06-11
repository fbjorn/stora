from PySide6.QtWidgets import QDialog

from app.utils import apply_theme
from app.widgets.auto.dialog_connect_to_db import Ui_Dialog


class ConnectToDBDialog(QDialog, Ui_Dialog):
    def __init__(self, *args):
        super().__init__(*args)

        self.setupUi(self)
        apply_theme(self)

    @property
    def db_name(self):
        return self.inp_db_name.text()
