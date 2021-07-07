import datetime
import json

from PySide6.QtCore import QObject, Signal

from app.widgets.auto.document_value_input import (
    DocumentValueInputWidget as DocumentValueInputWidgetAuto,
)


class DocumentValueInputSignals(QObject):
    validation_error = Signal(str)


class DocumentValueInputWidget(DocumentValueInputWidgetAuto):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.signals = DocumentValueInputSignals()
        self._connect_slots()

    def _connect_slots(self):
        self.inp_number.textEdited.connect(self.validate)
        self.inp_map.textChanged.connect(self.validate)

    def clear_inputs(self):
        self.inp_str.setText("")
        self.inp_number.setText("0")
        self.inp_map.setPlainText("{}")
        self.inp_bool.setChecked(False)
        self.inp_date.setDateTime(datetime.datetime.utcnow())

    def validate(self):
        if self.w_stacked.currentWidget() == self.p_number:
            try:
                float(self.inp_number.text())
            except ValueError:
                self.signals.validation_error.emit("Please enter a valid number")
                return False
        elif self.w_stacked.currentWidget() == self.p_map:
            try:
                json.loads(self.inp_map.toPlainText())
            except ValueError:
                self.signals.validation_error.emit("Please enter a valid map")
                return False

        self.signals.validation_error.emit("")
        return True

    @property
    def value(self):
        if not self.validate():
            raise ValueError("Field validation failed")
        if self.w_stacked.currentWidget() == self.p_str:
            return self.inp_str.text()
        elif self.w_stacked.currentWidget() == self.p_number:
            num = self.inp_number.text()
            return float(num) if "." in num else int(num)
        elif self.w_stacked.currentWidget() == self.p_map:
            return json.loads(self.inp_map.toPlainText())
        elif self.w_stacked.currentWidget() == self.p_bool:
            return self.inp_bool.isChecked()
        elif self.w_stacked.currentWidget() == self.p_date:
            return self.inp_date.dateTime().toPython()
