# Привязка кнопок и сигналов
def setup_signals(ui):
    ui.connect_btn.clicked.connect(
        lambda checked: ui.handle_connection() if checked else ui.handle_disconnect()
    )
    ui.actionSave_Profile.triggered.connect(ui.load_profiles_to_db)
    ui.actionDelete_Profile.triggered.connect(ui.delete_profile_from_db)
    ui.actionUpdate_remote_tree.triggered.connect(ui.refresh_remote_tree)

    ui.StartResume_PushButton.clicked.connect(ui.queue_manager.resume_queue)
    ui.Pause_PushButton.clicked.connect(ui.queue_manager.pause_current)
    ui.ClearCancel_PushButton.clicked.connect(ui.queue_manager.cancel_or_clear)

    ui.profile_combo.currentIndexChanged.connect(ui.choose_profile_from_combobox)

    ui.remote.expanded.connect(ui.on_node_expanded)

    ui.actionClose.triggered.connect(ui.close)

    ui.local.clicked.connect(ui.on_local_item_clicked)
    ui.local_pathline.returnPressed.connect(ui.on_local_path_entered)

    ui.remote.expanded.connect(ui.on_node_expanded)
    ui.remote.clicked.connect(ui.on_remote_item_clicked)
    ui.remote_pathline.returnPressed.connect(ui.on_remote_path_entered)
