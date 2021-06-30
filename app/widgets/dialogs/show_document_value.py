import json

from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QDialog

from app.utils import apply_theme
from app.widgets.auto.dialog_document_value import Ui_Dialog


class ShowDocumentValueDialog(QDialog, Ui_Dialog):
    def __init__(self, value, *args):
        super().__init__(*args)

        self.setupUi(self)
        apply_theme(self)

        self._value = value

        self.lbl_formatter.setText(self.pretty_value)
        self.te_value.setText(str(self._value))
        self.lbl_formatter.setFocus()

    @property
    def pretty_value(self) -> str:
        if isinstance(self._value, (list, dict)):
            return json.dumps(self._value, indent=2)
        # if hasattr(self._value, "strftime"):
        #     return self._value.strftime("%m-%d-%Y - %H:%M:%S")
        return str(self._value)

    def keyPressEvent(self, event: QKeyEvent) -> None:
        if event.text() == " ":
            self.accept()
        super().keyPressEvent(event)
