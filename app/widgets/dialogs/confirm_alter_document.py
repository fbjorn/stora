from PySide6.QtWidgets import QDialog

from app.widgets.auto.dialog_confirm_alter_document import Ui_Dialog


class ConfirmAlterDocumentDialog(QDialog, Ui_Dialog):
    def __init__(self, *args, old="", new="", **kwargs):
        super().__init__(*args, **kwargs)

        self.setupUi(self)

        self.lbl_prev_value.setText(old)
        self.lbl_new_value.setText(new)
