from typing import Optional

from google.cloud import firestore
from google.cloud.firestore_v1 import CollectionReference
from PySide6.QtCore import Slot
from PySide6.QtWidgets import QTreeWidgetItem

from app.widgets.auto.collections_tree import (
    CollectionsTreeWidget as CollectionsTreeWidgetAuto,
)


class CollectionsTreeWidget(CollectionsTreeWidgetAuto):
    def __init__(self, *args, client: Optional[firestore.Client] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = client

        self._connect_slots()

    def _connect_slots(self):
        self.b_refresh.clicked.connect(self.refresh_collections_list)

    @Slot()
    def refresh_collections_list(self):
        self.w_tree.clear()

        for col in self.client.collections():
            col: CollectionReference
            item = QTreeWidgetItem(self.w_tree)
            item.setText(0, col.id)
            self.w_tree.addTopLevelItem(item)
