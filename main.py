import asyncio
import sys

from PyQt6.QtCore import Qt, QMimeDatabase, QModelIndex
from PyQt6.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop, asyncSlot

from modules import handle_connection, signals_and_buttons, trees, trees_interactions, queue_manager, \
    profile_interactions, log
from user_interface.ui_client import Ui_KFTP


class FTPClient(QMainWindow, Ui_KFTP):
    load_profiles = profile_interactions.load_profiles
    choose_profile_from_combobox = profile_interactions.choose_profile_from_combobox
    load_profiles_to_db = profile_interactions.load_profiles_to_db
    delete_profile_from_db = profile_interactions.delete_profile_from_db

    log = log.log

    setup_local_tree = trees.setup_local_tree
    setup_remote_tree = trees.setup_remote_tree
    refresh_remote_tree = trees.refresh_remote_tree
    add_tree_item = trees.add_tree_item

    show_local_context_menu = trees_interactions.show_local_context_menu
    show_remote_context_menu = trees_interactions.show_remote_context_menu
    on_delete_from_local = trees_interactions.on_delete_from_local
    on_delete_from_remote = trees_interactions.on_delete_from_remote
    on_send_to_local = trees_interactions.on_send_to_local
    on_send_to_remote = trees_interactions.on_send_to_remote

    on_local_item_clicked = trees_interactions.on_local_item_clicked
    on_local_path_entered = trees_interactions.on_local_path_entered
    on_remote_item_clicked = trees_interactions.on_remote_item_clicked
    on_remote_path_entered = trees_interactions.on_remote_path_entered

    @asyncSlot(QModelIndex)
    async def on_node_expanded(self, index):
        """Handle node expansion event in both local and remote trees"""
        await trees.on_node_expanded(self, index)

    @asyncSlot()
    async def handle_connection(self):
        """Handle connection button click event"""
        await handle_connection.handle_connection(self)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ftp_client = None
        self.mime_db = QMimeDatabase()
        self.queue_manager = queue_manager.QueueManager(self)

        self.setup_local_tree()
        self.setup_remote_tree()
        self.load_profiles()

        self.local.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.remote.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)

        self.local.customContextMenuRequested.connect(self.show_local_context_menu)
        self.remote.customContextMenuRequested.connect(self.show_remote_context_menu)

        signals_and_buttons.setup_signals(self)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    loop = QEventLoop(app)
    asyncio.set_event_loop(loop)
    window = FTPClient()
    window.show()
    with loop:
        loop.run_forever()
