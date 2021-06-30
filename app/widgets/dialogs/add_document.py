from typing import Any, Dict, List, Optional, Type

from google.api_core.datetime_helpers import DatetimeWithNanoseconds
from google.cloud.firestore_v1 import CollectionReference
from loguru import logger
from PySide6.QtWidgets import QDialog, QVBoxLayout

from app.utils import apply_theme
from app.widgets.add_document_item import AddDocumentItemWidget
from app.widgets.auto.dialog_add_document import Ui_Dialog
from app.widgets.dialogs.error import show_error

TYPE_TO_DROPDOWN_INDEX = {
    str: 0,
    bool: 1,
    int: 2,
    float: 2,
    DatetimeWithNanoseconds: 3,
    list: 4,
    dict: 4,
}


class AddDocumentDialog(QDialog, Ui_Dialog):
    def __init__(
        self,
        collection: CollectionReference,
        title: str = "",
        structure: Optional[Dict[str, Type]] = None,
        *args
    ):
        super().__init__(*args)

        self.setupUi(self)
        self.input_widgets: List[AddDocumentItemWidget] = [self.w_add_item_default]
        self.collection = collection

        if title:
            self.setWindowTitle(title)

        apply_theme(self)

        self._connect_slots()

        if structure:
            self.create_input_widgets(structure)

    def _connect_slots(self):
        self.b_add_field.clicked.connect(self.add_field_input_widget)

    def create_input_widgets(self, structure: Dict[str, Any]):
        self.w_scroll_content.layout().removeWidget(self.w_add_item_default)
        self.w_add_item_default.setParent(None)
        self.w_add_item_default.deleteLater()
        self.input_widgets = []

        for name, type_ in structure.items():
            wgt = self.add_field_input_widget(name=name)
            wgt.dd_type.setCurrentIndex(TYPE_TO_DROPDOWN_INDEX.get(type_, 0))

    def add_field_input_widget(self, name: str = ""):
        wgt = AddDocumentItemWidget(name=name)
        self.input_widgets.append(wgt)
        layout: QVBoxLayout = self.w_scroll_content.layout()
        layout.insertWidget(len(self.input_widgets), wgt)
        wgt.inp_name.setFocus()
        return wgt

    def accept(self) -> None:
        try:
            document = {w.key: w.value for w in self.input_widgets}
        except ValueError:
            show_error(
                "Document is incorrect, please check validation errors "
                "or that all fields has a name"
            )
            return

        try:
            self.collection.add(document)
        except Exception:
            show_error("Failed to create document")
            logger.exception("Failed to create document")
            return

        super().accept()
