from functools import partial
from typing import List, Optional

from google.cloud import firestore
from PySide6.QtCore import Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QMenu, QTableWidgetItem

from app.widgets.auto.collection_table import (
    CollectionTableWidget as CollectionTableWidgetAuto,
)
from app.widgets.dialogs.add_document import AddDocumentDialog
from app.widgets.dialogs.show_document_value import ShowDocumentValueDialog


class TableItem(QTableWidgetItem):
    def __init__(self, db_id: str, content: str, *args):
        super().__init__(*args)
        self.db_id = db_id
        self.content = content
        self.setText(str(self.content))


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

        self._connect_slots()

    def _connect_slots(self):
        self.w_table.customContextMenuRequested.connect(self.create_table_context_menu)
        self.w_table.keyPressEvent = self._on_table_item_key_press
        self.b_refresh.clicked.connect(self.refresh_documents_in_table)
        self.b_add.clicked.connect(self.create_document)

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
        if event.text() == " ":
            data = self.w_table.currentItem().content
            dialog = ShowDocumentValueDialog(data)
            dialog.exec()

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
                item = TableItem(doc.get("id", doc.get("uuid", None)), v)
                self.w_table.setItem(i, header_pos[k], item)
                self.structure[k] = type(v)

        self.structure.pop("id", None)
