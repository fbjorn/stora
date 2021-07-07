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

        self.w_inp.setMaximumWidth(200)
        self.w_inp.inp_map.setMaximumHeight(self.w_inp.inp_str.height())

    def _connect_slots(self):
        self.dd_type.currentIndexChanged.connect(self.on_dropdown_changed)
        self.w_inp.signals.validation_error.connect(self.show_error)

    @Slot()
    def on_dropdown_changed(self, index: int):
        self.w_inp.w_stacked.setCurrentIndex(index)
        self.w_inp.clear_inputs()

    def show_error(self, text: str):
        self.lbl_error.setText(text)
        self.lbl_error.setVisible(text != "")

    def clear_inputs(self):
        self.w_inp.clear_inputs()

    @property
    def value(self):
        return self.w_inp.value

    @property
    def key(self) -> str:
        name = self.inp_name.text()
        if not name:
            raise ValueError("Name is empty")
        return name
