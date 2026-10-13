import os
import shutil
from pathlib import Path
from qasync import asyncSlot
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QMessageBox
from modules.config import (
    LOG_NO_FTP_CLIENT,
    DIR_MARKERS,
    LOG_SCANNING_LOCAL_FOLDER,
    LOG_SCANNING_REMOTE_FOLDER,
    TYPE_DIR,
    DIRECTION_DOWNLOAD,
    DIRECTION_UPLOAD,
    LOG_FOLDER_FILES_ADDED,
    LOG_REMOTE_FOLDER_READ_ERROR,
    LOG_LOCAL_PATH_NOT_FOUND,
    DEFAULT_REMOTE_PATH,
)


def show_local_context_menu(self, pos):
    index = self.local.indexAt(pos)
    if not index.isValid():
        return

    menu = QMenu()
    menu.addAction("Send to remote server", lambda: self.on_send_to_remote(index))
    menu.addAction("Delete", lambda: self.on_delete_from_local(index))

    menu.exec(self.local.mapToGlobal(pos))


def show_remote_context_menu(self, pos):
    index = self.remote.indexAt(pos)
    if not index.isValid():
        return

    menu = QMenu()
    menu.addAction("Download to local", lambda: self.on_send_to_local(index))
    menu.addAction("Delete from remote", lambda: self.on_delete_from_remote(index))

    menu.exec(self.remote.mapToGlobal(pos))


def on_delete_from_local(self, index):
    local_path = self.local_model.filePath(index)
    file_name = self.local_model.fileName(index)

    reply = QMessageBox.warning(
        self,
        "Delete file",
        f"Are you sure you want to delete {file_name}?<br><center>⚠ This action cannot be undone! ⚠</center>",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    if reply == QMessageBox.StandardButton.Yes:
        try:
            if self.local_model.isDir(index):
                shutil.rmtree(local_path)
            else:
                os.remove(local_path)
            self.log(
                "Element deleted successfully! (If you accidentally deteled a wrong file, well I don't give a fuck lol :))"
            )
        except Exception as e:
            self.log(f"Error: {e}")
    else:
        self.log("Deletion cancelled")


@asyncSlot()
async def on_delete_from_remote(self, index):
    if not self.ftp_client:
        self.log("No FTP client connected!")
        return

    item = self.remote_model.itemFromIndex(index)
    if not item:
        self.log("Item not found!")
        return

    remote_path = item.data(Qt.ItemDataRole.UserRole)
    file_name = item.text()

    if not remote_path:
        self.log("Remote path not found!")
        return

    reply = QMessageBox.warning(
        self,
        "Delete file",
        f"Are you sure you want to delete {file_name} from remote server?<br><center>⚠ This action cannot be undone! ⚠</center>",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.No,
    )

    if reply != QMessageBox.StandardButton.Yes:
        return

    self.log("Deleting file from remote server...")

    try:
        await self.ftp_client.remove(remote_path)
        self.log(f"{file_name} deleted successfully!")

        self.remote_model.removeRow(index.row(), index.parent())
    except Exception as e:
        self.log(f"Error: {e}")


@asyncSlot()
async def on_send_to_local(self, index):
    """Download directly to the currently opened local directory (FileZilla style)."""
    if not self.ftp_client:
        self.log(LOG_NO_FTP_CLIENT)
        return

    item = self.remote_model.itemFromIndex(index)
    if not item:
        return

    remote_path = item.data(Qt.ItemDataRole.UserRole)
    file_name = item.text()
    if not remote_path:
        return

    local_dest_path = (
        self.local_pathline.text().strip()
        if hasattr(self, "local_pathline") and self.local_pathline.text()
        else str(Path.home() / "Downloads")
    )

    type_item = self.remote_model.item(index.row(), 2)
    is_dir = type_item is not None and type_item.text() in DIR_MARKERS

    if is_dir:
        self.log(LOG_SCANNING_REMOTE_FOLDER.format(name=file_name))
        try:
            count = 0
            async for path, stat in self.ftp_client.list(remote_path, recursive=True):
                if stat.get("type") != TYPE_DIR and path.name not in [".", ".."]:
                    rel_path = Path(str(path)).relative_to(
                        Path(str(remote_path)).parent
                    )
                    target_dir = Path(local_dest_path) / rel_path.parent
                    target_dir.mkdir(parents=True, exist_ok=True)

                    # Safely convert size to int (handles strings/None returned by FTP)
                    raw_size = stat.get("size", 0)
                    try:
                        total_size = int(raw_size) if raw_size is not None else 0
                    except (ValueError, TypeError):
                        total_size = 0

                    self.queue_manager.add_task(
                        file_name=path.name,
                        direction=DIRECTION_DOWNLOAD,
                        source_path=str(path),
                        dest_path=str(target_dir),
                        total_size=total_size,
                    )
                    count += 1
            self.log(LOG_FOLDER_FILES_ADDED.format(count=count))
        except Exception as e:
            self.log(LOG_REMOTE_FOLDER_READ_ERROR.format(error=e))
    else:
        raw_size = item.data(Qt.ItemDataRole.UserRole + 1) or 0
        try:
            total_size = int(raw_size) if raw_size is not None else 0
        except (ValueError, TypeError):
            total_size = 0

        self.queue_manager.add_task(
            file_name=file_name,
            direction=DIRECTION_DOWNLOAD,
            source_path=str(remote_path),
            dest_path=local_dest_path,
            total_size=total_size,
        )


@asyncSlot()
async def on_send_to_remote(self, index):
    """Enqueue local file or directory for uploading to remote server."""
    if not self.ftp_client:
        self.log(LOG_NO_FTP_CLIENT)
        return

    local_path = Path(self.local_model.filePath(index))
    if not local_path.exists():
        self.log(LOG_LOCAL_PATH_NOT_FOUND)
        return

    destination_dir = DEFAULT_REMOTE_PATH
    if hasattr(self, "remote_pathline") and self.remote_pathline.text():
        destination_dir = self.remote_pathline.text().strip() or DEFAULT_REMOTE_PATH

    if local_path.is_dir():
        self.log(LOG_SCANNING_LOCAL_FOLDER.format(name=local_path.name))
        count = 0
        for file in local_path.rglob("*"):
            if file.is_file():
                rel_dir = file.parent.relative_to(local_path.parent)
                target_remote_dir = (f"{destination_dir}/{rel_dir.as_posix()}").replace(
                    "//", "/"
                )

                self.queue_manager.add_task(
                    file_name=file.name,
                    direction=DIRECTION_UPLOAD,
                    source_path=str(file),
                    dest_path=target_remote_dir,
                    total_size=file.stat().st_size,
                )
                count += 1
        self.log(LOG_FOLDER_FILES_ADDED.format(count=count))
    else:
        self.queue_manager.add_task(
            file_name=local_path.name,
            direction=DIRECTION_UPLOAD,
            source_path=str(local_path),
            dest_path=destination_dir,
            total_size=local_path.stat().st_size,
        )


def on_local_item_clicked(self, index):
    path = self.local_model.filePath(index)

    if not self.local_model.isDir(index):
        path = str(Path(path).parent)

    self.local_pathline.setText(path)


def on_local_path_entered(self):
    path = self.local_pathline.text().strip()

    if os.path.exists(path) and os.path.isdir(path):
        index = self.local_model.index(path)
        self.local.setRootIndex(index)

    else:
        self.log("Invalid path!")


def on_remote_item_clicked(self, index):
    item = self.remote_model.itemFromIndex(index)
    if not item:
        return

    path = item.data(Qt.ItemDataRole.UserRole)
    if path:
        self.remote_pathline.setText(str(path))


def find_item_by_path(parent_item, target_path):
    for row in range(parent_item.rowCount()):
        child = parent_item.child(row)
        if child.data(Qt.ItemDataRole.UserRole) == target_path:
            return child
        found = find_item_by_path(child, target_path)
        if found:
            return found
    return None


def on_remote_path_entered(self):
    target_path = self.remote_pathline.text().strip()

    item = find_item_by_path(self.remote_model.invisibleRootItem(), target_path)
    if item:
        index = item.index()
        self.remote.setCurrentIndex(index)
        self.remote.scrollTo(index)
        self.log(f"Access to: {target_path}")
    else:
        self.log(
            f"Folder {target_path} hasn't been loaded yet. Expand it through the tree."
        )
