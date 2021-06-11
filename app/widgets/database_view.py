from google.cloud.firestore_v1 import CollectionReference
from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QMenu, QTableWidgetItem, QTreeWidgetItem

from app.db import get_firestore_emulator_client
from app.widgets.auto.database_view import DatabaseViewWidget


class TableAction:
    REMOVE_DOC = "Remove document"


class TableItem(QTableWidgetItem):
    def __init__(self, db_id: str, *args):
        super().__init__(*args)
        self.db_id = db_id


class DatabaseView(DatabaseViewWidget):
    def __init__(self, db_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = self.w_collection_table.w_table

        self.db_name = db_name
        self.db = get_firestore_emulator_client(self.db_name)
        self.row_to_db_id = {}

        self._init_ui()
        self._connect_slots()

        self.refresh_collections_list()

    def _init_ui(self):
        self.lbl_db_name.setText(self.db_name)
        self.w_stack.setCurrentWidget(self.page_info)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        # self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_slots(self):
        self.w_collections_tree.b_refresh.clicked.connect(self.refresh_collections_list)
        self.w_collections_tree.w_tree.itemClicked.connect(
            self._on_collection_double_clicked
        )
        self.table.customContextMenuRequested.connect(self.foo)

    def foo(self, pos):
        menu = QMenu()
        db_ids = set(
            item.db_id for item in self.table.selectedItems() if item is not None
        )
        menu.addAction(f"Remove {len(db_ids)} document(s)")
        menu.exec(self.table.viewport().mapToGlobal(pos))
        # if action and action.text() == TableAction.REMOVE_DOC:
        #     print(self.table.selectedItems())

    @Slot()
    def refresh_collections_list(self):
        for col in self.db.collections():
            col: CollectionReference
            item = QTreeWidgetItem(self.w_collections_tree.w_tree)
            item.setText(0, col.id)
            self.w_collections_tree.w_tree.addTopLevelItem(item)

    @Slot()
    def _on_collection_double_clicked(self, item: QTreeWidgetItem, *_):
        col_name = item.text(0)
        self.refresh_documents_in_table(col_name)
        self.w_stack.setCurrentWidget(self.page_table)

    def refresh_documents_in_table(self, col_name: str):
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
                # item = QTableWidgetItem(str(v))
                item = TableItem(doc.get("id", doc.get("uuid", None)), str(v))
                # item.db_id = doc.get("uuid", doc.get("id", None))
                self.table.setItem(i, header_pos[k], item)
                # self.row_to_db_id[i] = doc.get("uuid", doc.get("id", None))
