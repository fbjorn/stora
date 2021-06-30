import datetime
import json

from PySide6.QtCore import Slot

from app.widgets.auto.add_document_item import (
    AddDocumentItemWidget as AddDocumentItemWidgetAuto,
)


class AddDocumentItemWidget(AddDocumentItemWidgetAuto):
    def __init__(self, *args, name: str = "", **kwargs):
        super().__init__(*args, **kwargs)
        self.init_layout(name)
        self._connect_slots()

    def init_layout(self, name: str):
        self.show_error("")
        self.on_dropdown_changed(0)
        if name:
            self.inp_name.setText(name)

    def _connect_slots(self):
        self.dd_type.currentIndexChanged.connect(self.on_dropdown_changed)
        self.inp_number.textEdited.connect(self.validate)
        self.inp_map.textEdited.connect(self.validate)

    @Slot()
    def on_dropdown_changed(self, index: int):
        self.w_stacked.setCurrentIndex(index)
        self.clear_inputs()

    def show_error(self, text: str):
        self.lbl_error.setText(text)
        self.lbl_error.setVisible(text != "")

    def clear_inputs(self):
        self.inp_str.setText("")
        self.inp_number.setText("0")
        self.inp_map.setText("{}")
        self.inp_bool.setChecked(False)
        self.inp_date.setDateTime(datetime.datetime.utcnow())

    def validate(self):
        if self.w_stacked.currentWidget() == self.p_number:
            try:
                float(self.inp_number.text())
            except ValueError:
                self.show_error("Please enter a valid number")
                return False
        elif self.w_stacked.currentWidget() == self.p_map:
            try:
                json.loads(self.inp_map.text())
            except ValueError:
                self.show_error("Please enter a valid map")
                return False

        self.show_error("")
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
            return json.loads(self.inp_map.text())
        elif self.w_stacked.currentWidget() == self.p_bool:
            return self.inp_bool.isChecked()
        elif self.w_stacked.currentWidget() == self.p_date:
            return self.inp_date.dateTime().toPython()

    @property
    def key(self) -> str:
        name = self.inp_name.text()
        if not name:
            raise ValueError("Name is empty")
        return name
