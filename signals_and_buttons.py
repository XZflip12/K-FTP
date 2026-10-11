# Привязка кнопок и сигналов
def setup_signals(ui):
    ui.connect_btn.clicked.connect(ui.handle_connection)
    ui.actionSave_Profile.triggered.connect(ui.load_profiles_to_db)
    ui.actionDelete_Profile.triggered.connect(ui.delete_profile_from_db)

    ui.profile_combo.currentIndexChanged.connect(ui.choose_profile_from_combobox)

    ui.remote.expanded.connect(ui.on_node_expanded)

    ui.actionClose.triggered.connect(ui.close)
