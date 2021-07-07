import json
from functools import partial
from typing import List, Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import DocumentReference
from PySide6.QtCore import Slot
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import QMenu, QTableWidgetItem

from app.widgets.auto.collection_table import (
    CollectionTableWidget as CollectionTableWidgetAuto,
)
from app.widgets.dialogs.add_document import AddDocumentDialog
from app.widgets.dialogs.show_document_value import ShowDocumentValueDialog
from app.widgets.dialogs.update_value import UpdateValueDialog


class TableItem(QTableWidgetItem):
    def __init__(self, db_id: str, key: str, content, *args):
        super().__init__(*args)
        self.db_id = db_id
        self.key = key
        self.content = content

        self.type_ = type(self.content)
        self.set_cell_text()

    @property
    def repr(self):
        if self.type_ in {dict, list}:
            return json.dumps(self.content)
        else:
            return str(self.content)

    @property
    def pretty_repr(self):
        if self.type_ in {dict, list}:
            return json.dumps(self.content, indent=2)
        else:
            return str(self.content)

    def set_value(self, content):
        self.content = content
        self.set_cell_text()

    def set_cell_text(self):
        self.setText(self.repr)


class CollectionTableWidget(CollectionTableWidgetAuto):
    def __init__(
        self, *args, name: str = "", client: Optional[firestore.Client] = None, **kwargs
    ):
        super().__init__(*args, **kwargs)

        self.client = client
        self.col_name = name
        if self.client:
            self.col_ref = self.client.collection(self.col_name)
        else:
            self.col_ref = None
        self.structure = {}

        self._last_activated_item: Optional[TableItem] = None

        self._connect_slots()

    def _connect_slots(self):
        self.w_table.customContextMenuRequested.connect(self.create_table_context_menu)
        self.w_table.keyPressEvent = self._on_table_item_key_press
        self.b_refresh.clicked.connect(self.refresh_documents_in_table)
        self.b_add.clicked.connect(self.create_document)

        self.w_table.itemDoubleClicked.connect(self._set_last_activated_item)
        self.w_table.itemChanged.connect(self.on_table_item_changed)

    def get_db_path(self, db_id: str) -> str:
        return f"{self.col_name}/{db_id}"

    def get_doc_ref(self, db_id: str) -> DocumentReference:
        return self.client.document(self.get_db_path(db_id))

    def _set_last_activated_item(self, item: TableItem):
        self._last_activated_item = item
        dialog = UpdateValueDialog(
            doc_ref=self.get_doc_ref(item.db_id),
            key=item.key,
            old_value=item.pretty_repr,
            type_=item.type_,
        )
        if dialog.exec():
            item.set_value(dialog.value)

    def on_table_item_changed(self, item: TableItem):
        # ignore the modification
        item.set_cell_text()

    @Slot()
    def create_document(self):
        dialog = AddDocumentDialog(
            collection=self.col_ref,
            title=f"Add document to {self.col_name}",
            structure=self.structure,
        )
        dialog.exec()
        self.refresh_documents_in_table()

    def create_table_context_menu(self, pos):
        db_ids = set(
            item.db_id for item in self.w_table.selectedItems() if item is not None
        )

        menu = QMenu()
        menu.addAction(
            f"Remove {len(db_ids)} document(s)",
            partial(self.delete_documents, db_ids),
        )
        menu.exec(self.w_table.viewport().mapToGlobal(pos))

    def delete_documents(self, doc_ids: List[str]):
        for doc_id in doc_ids:
            self.client.document(f"{self.col_name}/{doc_id}").delete()
        self.refresh_documents_in_table()

    def _on_table_item_key_press(self, event: QKeyEvent):
        item: TableItem = self.w_table.currentItem()
        # show an item preview
        if event.key() == Qt.Key_Space:
            dialog = ShowDocumentValueDialog(key=item.key, value=item.content)
            dialog.exec()
        # modify the item
        elif event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.EnterKeyReturn):
            dialog = UpdateValueDialog(
                doc_ref=self.get_doc_ref(item.db_id),
                key=item.key,
                old_value=item.pretty_repr,
                type_=item.type_,
            )
            if dialog.exec():
                item.set_value(dialog.value)
        # TODO: make sure arrows work

    def refresh_documents_in_table(self, col_name: Optional[str] = None):
        if col_name:
            self.col_name = col_name
            self.col_ref = self.client.collection(self.col_name)

        docs = []
        headers = set()
        for doc in self.col_ref.stream():
            doc_dict = doc.to_dict()
            doc_dict["id"] = doc.id
            headers.update(set(doc_dict.keys()))
            docs.append(doc_dict)

        headers = sorted(list(headers))
        try:
            headers.remove("id")
        except ValueError:
            pass
        else:
            headers = list(headers) + ["id"]

        header_pos = {h: i for i, h in enumerate(headers)}

        self.w_table.setColumnCount(len(headers))
        self.w_table.setRowCount(len(docs))
        self.w_table.setHorizontalHeaderLabels(headers)

        self.structure = {}
        for i, doc in enumerate(docs):
            for k, v in doc.items():
                item = TableItem(
                    db_id=doc.get("id", doc.get("uuid", None)), key=k, content=v
                )
                self.w_table.setItem(i, header_pos[k], item)
                self.structure[k] = type(v)

        self.structure.pop("id", None)
