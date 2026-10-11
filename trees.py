from PyQt6.QtCore import QDir, QModelIndex, Qt
from PyQt6.QtGui import QFileSystemModel, QStandardItem, QStandardItemModel
from PyQt6.QtWidgets import QStyle

from config import (
    HEADER_NAME,
    HEADER_SIZE,
    HEADER_TYPE,
    KEY_SIZE,
    KEY_TYPE,
    LOCAL_COLUMN_0_WIDTH,
    LOG_FETCH_SUBFOLDER,
    LOG_FETCH_SUBFOLDER_ERROR,
    REMOTE_COLUMN_0_WIDTH,
    REMOTE_COLUMN_1_WIDTH,
    TEXT_FILE,
    TEXT_FOLDER,
    TEXT_LOADING,
    TYPE_DIR,
)
from misc.format_size import format_size


def setup_local_tree(self):
    self.local_model = QFileSystemModel()
    self.local_model.setRootPath(QDir.rootPath())
    self.local.setModel(self.local_model)
    self.local.setRootIndex(self.local_model.index(QDir.rootPath()))
    self.local.setColumnWidth(0, LOCAL_COLUMN_0_WIDTH)


def setup_remote_tree(self):
    self.remote_model = QStandardItemModel()
    self.remote_model.setHorizontalHeaderLabels([HEADER_NAME, HEADER_SIZE, HEADER_TYPE])
    self.remote.setModel(self.remote_model)
    self.remote.setColumnWidth(0, REMOTE_COLUMN_0_WIDTH)
    self.remote.setColumnWidth(1, REMOTE_COLUMN_1_WIDTH)


def add_tree_item(self, parent, path, stat):
    """Вспомогательный метод для добавления элементов (в корень или в папку)"""
    folder_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_DirIcon)
    file_icon = self.style().standardIcon(QStyle.StandardPixmap.SP_FileIcon)

    name = path.name
    is_dir = stat.get(KEY_TYPE) == TYPE_DIR
    raw_size = stat.get(KEY_SIZE, None)

    name_item = QStandardItem(name)
    name_item.setData(str(path), Qt.ItemDataRole.UserRole)

    if is_dir:
        name_item.setIcon(folder_icon)
        type_item = QStandardItem(TEXT_FOLDER)
        size_item = QStandardItem("")

        dummy = QStandardItem(TEXT_LOADING)
        name_item.appendRow([dummy])
    else:
        name_item.setIcon(file_icon)
        mime_type = self.mime_db.mimeTypeForFile(str(path))
        type_item = QStandardItem(mime_type.comment() or TEXT_FILE)
        size_item = QStandardItem(format_size(raw_size))

    name_item.setEditable(False)
    size_item.setEditable(False)
    type_item.setEditable(False)

    parent.appendRow([name_item, size_item, type_item])


async def on_node_expanded(self, index: QModelIndex):
    """Срабатывает при раскрытии папки пользователем"""
    item = self.remote_model.itemFromIndex(index)
    if not item or not self.ftp_client:
        return

    if item.rowCount() == 1 and item.child(0).text() == TEXT_LOADING:
        item.removeRow(0)

        folder_path = item.data(Qt.ItemDataRole.UserRole)
        self.log(LOG_FETCH_SUBFOLDER.format(path=folder_path))

        try:
            items_list = []
            async for path, stat in self.ftp_client.list(folder_path):
                if path.name in [".", ".."]:
                    continue
                items_list.append((path, stat))

            items_list.sort(
                key=lambda x: (x[1].get(KEY_TYPE) != TYPE_DIR, x[0].name.lower())
            )

            for path, stat in items_list:
                self.add_tree_item(item, path, stat)

        except Exception as e:
            self.log(LOG_FETCH_SUBFOLDER_ERROR.format(error=e))
