from typing import Optional

import dateutil.parser
from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.firestore_v1 import DocumentReference
from PySide6.QtWidgets import QDialog

from app.db import update_document_value
from app.widgets.auto.dialog_update_value import Ui_Dialog
from app.widgets.dialogs.confirm_alter_document import ConfirmAlterDocumentDialog


class UpdateValueDialog(QDialog, Ui_Dialog):
    def __init__(
        self,
        *args,
        doc_ref: Optional[DocumentReference] = None,
        key: str = "",
        old_value=None,
        type_=None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.setupUi(self)

        self.doc_ref = doc_ref
        self.old_value = old_value
        self.key = key
        self.type_ = type_

        self.w_inp = self.w_value_input
        self._init_layout()
        self._connect_slots()

    def _connect_slots(self):
        self.w_inp.signals.validation_error.connect(self.show_error)

    def _init_layout(self):
        self.lbl_title.setText(f"Update {self.key}")
        self.lbl_error.setVisible(False)

        if self.type_ == str:
            self.w_inp.w_stacked.setCurrentWidget(self.w_inp.p_str)
            self.w_inp.inp_str.setText(self.old_value)
        elif self.type_ in (int, float):
            self.w_inp.w_stacked.setCurrentWidget(self.w_inp.p_number)
            self.w_inp.inp_number.setText(self.old_value)
        elif self.type_ in (dict, list):
            self.w_inp.w_stacked.setCurrentWidget(self.w_inp.p_map)
            self.w_inp.inp_map.setPlainText(self.old_value)
        elif self.type_ == DatetimeWithNanoseconds:
            self.w_inp.w_stacked.setCurrentWidget(self.w_inp.p_date)
            self.w_inp.inp_date.setDateTime(dateutil.parser.parse(self.old_value))

    def show_error(self, text: str):
        has_error = text != ""
        if text:
            self.lbl_error.setText(text)

        self.lbl_error.setVisible(has_error)
        self.buttonBox.button(self.buttonBox.Ok).setDisabled(has_error)

    def accept(self) -> None:
        dlg = ConfirmAlterDocumentDialog(
            old=str(self.old_value), new=str(self.w_inp.value)
        )
        if dlg.exec():
            if self.update_document():
                super().accept()

    def update_document(self) -> bool:
        return update_document_value(self.doc_ref, key=self.key, value=self.w_inp.value)

    @property
    def value(self):
        return self.w_inp.value
