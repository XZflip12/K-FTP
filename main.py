import asyncio
import sys

from PyQt6.QtCore import Qt, QMimeDatabase, QModelIndex
from PyQt6.QtWidgets import QApplication, QMainWindow
from qasync import QEventLoop, asyncSlot

import handle_connection
import log
import profile_interactions
import signals_and_buttons
import trees
import profile_interactions
from trees_interactions import *
import trees_interactions
from user_interface.ui_client import Ui_KFTP


class FTPClient(QMainWindow, Ui_KFTP):
    load_profiles = profile_interactions.load_profiles
    choose_profile_from_combobox = profile_interactions.choose_profile_from_combobox
    load_profiles_to_db = profile_interactions.load_profiles_to_db
    delete_profile_from_db = profile_interactions.delete_profile_from_db

    log = log.log

    setup_local_tree = trees.setup_local_tree
    setup_remote_tree = trees.setup_remote_tree
    add_tree_item = trees.add_tree_item

    show_local_context_menu = trees_interactions.show_local_context_menu
    show_remote_context_menu = trees_interactions.show_remote_context_menu
    on_delete_from_local = trees_interactions.on_delete_from_local
    on_delete_from_remote = trees_interactions.on_delete_from_remote
    on_send_to_local = trees_interactions.on_send_to_local
    on_send_to_remote = trees_interactions.on_send_to_remote

    @asyncSlot(QModelIndex)
    async def on_node_expanded(self, index):
        await trees.on_node_expanded(self, index)

    @asyncSlot()
    async def handle_connection(self):
        await handle_connection.handle_connection(self)

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.ftp_client = None
        self.mime_db = QMimeDatabase()

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
