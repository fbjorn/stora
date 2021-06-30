from PySide6.QtCore import Qt, Slot
from PySide6.QtWidgets import QHeaderView, QTreeWidgetItem

from app.db import get_firestore_emulator_client
from app.widgets.auto.database_view import DatabaseViewWidget as DatabaseViewWidgetAuto


class DatabaseView(DatabaseViewWidgetAuto):
    def __init__(self, db_name, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.table = self.w_collection_table.w_table
        self.tree = self.w_collections_tree.w_tree

        self.db_name = db_name
        self.client = get_firestore_emulator_client(self.db_name)
        self.w_collection_table.client = self.client
        self.w_collections_tree.client = self.client

        self._init_ui()
        self._connect_slots()

        self.w_collections_tree.refresh_collections_list()

    def _init_ui(self):
        self.lbl_db_name.setText(self.db_name)
        self.w_stack.setCurrentWidget(self.page_info)

        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def _connect_slots(self):
        self.tree.itemClicked.connect(self._on_collection_double_clicked)

    @Slot()
    def _on_collection_double_clicked(self, item: QTreeWidgetItem, *_):
        col_name = item.text(0)
        self.w_collection_table.refresh_documents_in_table(col_name)
        self.w_stack.setCurrentWidget(self.page_table)
