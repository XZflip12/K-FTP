import os
import shutil
from pathlib import Path
import log
from qasync import asyncSlot
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QMenu, QMessageBox, QFileDialog


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
    item = self.remote_model.itemFromIndex(index)
    if not item:
        self.log("Item not found!")
        return

    remote_path = item.data(Qt.ItemDataRole.UserRole)
    file_name = item.text()

    if not remote_path:
        self.log("Remote path not found!")
        return

    local_dest_path = QFileDialog.getExistingDirectory(
        self,
        "Save file",
        "",
    )

    if not local_dest_path:
        return

    try:
        await self.ftp_client.download(remote_path, local_dest_path)
        self.log(f"{file_name} downloaded successfully!")
    except Exception as e:
        self.log(f"Error: {e}")


@asyncSlot()
async def on_send_to_remote(self, index):
    if not self.ftp_client:
        self.log("No FTP client connected!")
        return

    local_path = Path(self.local_model.filePath(index))

    destination_dir = "/"
    if hasattr(self, "input_remote_path") and self.input_remote_path.text():
        destination_dir = self.input_remote_path.text()

    self.log(f"Uploading '{local_path.name}' to server [{destination_dir}]...")

    try:
        await self.ftp_client.upload(local_path, destination_dir)
        self.log(f"'{local_path.name}' uploaded successfully!")

    except Exception as e:
        self.log(f"Error: {e}")
