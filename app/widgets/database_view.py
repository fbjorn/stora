from functools import partial
from typing import List, Optional

from google.cloud.firestore_v1 import CollectionReference
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QKeyEvent
from PySide6.QtWidgets import QHeaderView, QMenu, QTableWidgetItem, QTreeWidgetItem

from app.db import get_firestore_emulator_client
from app.widgets.auto.database_view import DatabaseViewWidget
from app.widgets.dialogs.document_value import DocumentValueDialog


class TableItem(QTableWidgetItem):
    def __init__(self, db_id: str, content: str, *args):
        super().__init__(*args)
        self.db_id = db_id
        self.content = content
        self.setText(str(self.content))


class DatabaseView(DatabaseViewWidget):
    def __init__(self, db_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = self.w_collection_table.w_table
        self.tree = self.w_collections_tree.w_tree

        self.db_name = db_name
        self.db = get_firestore_emulator_client(self.db_name)

        self._init_ui()
        self._connect_slots()

        self.refresh_collections_list()

    def _init_ui(self):
        self.lbl_db_name.setText(self.db_name)
        self.w_stack.setCurrentWidget(self.page_info)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_slots(self):
        self.w_collections_tree.b_refresh.clicked.connect(self.refresh_collections_list)
        self.tree.itemClicked.connect(self._on_collection_double_clicked)
        self.table.customContextMenuRequested.connect(self.create_table_context_menu)
        self.table.keyPressEvent = self._on_table_item_key_press
        self.w_collection_table.b_refresh.clicked.connect(
            self.refresh_documents_in_table
        )

    @property
    def current_collection_name(self) -> Optional[str]:
        idx = self.tree.currentColumn()
        item = self.tree.currentItem()
        if not item:
            return None
        return item.text(idx)

    def create_table_context_menu(self, pos):
        db_ids = set(
            item.db_id for item in self.table.selectedItems() if item is not None
        )

        menu = QMenu()
        menu.addAction(
            f"Remove {len(db_ids)} document(s)",
            partial(self.delete_documents, db_ids),
        )
        menu.exec(self.table.viewport().mapToGlobal(pos))

    def delete_documents(self, doc_ids: List[str]):
        coll = self.current_collection_name
        for doc_id in doc_ids:
            self.db.document(f"{coll}/{doc_id}").delete()
        self.refresh_documents_in_table(coll)

    @Slot()
    def refresh_collections_list(self):
        self.tree.clear()

        for col in self.db.collections():
            col: CollectionReference
            item = QTreeWidgetItem(self.tree)
            item.setText(0, col.id)
            self.tree.addTopLevelItem(item)

    @Slot()
    def _on_collection_double_clicked(self, item: QTreeWidgetItem, *_):
        col_name = item.text(0)
        self.refresh_documents_in_table(col_name)
        self.w_stack.setCurrentWidget(self.page_table)

    def _on_table_item_key_press(self, event: QKeyEvent):
        if event.text() == " ":
            data = self.table.currentItem().content
            dialog = DocumentValueDialog(data)
            dialog.exec()

    def refresh_documents_in_table(self, col_name: Optional[str] = None):
        if not col_name:
            col_name = self.current_collection_name
        docs = []
        headers = set()
        for doc in self.db.collection(col_name).stream():
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

        self.table.setColumnCount(len(headers))
        self.table.setRowCount(len(docs))
        self.table.setHorizontalHeaderLabels(headers)
        for i, doc in enumerate(docs):
            for k, v in doc.items():
                item = TableItem(doc.get("id", doc.get("uuid", None)), v)
                self.table.setItem(i, header_pos[k], item)
