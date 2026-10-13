from modules.config import (
    COMBO_INDEX_EMPTY,
    DEFAULT_FTP_PORT,
    DEFAULT_FTP_USER,
    DEFAULT_PROFILE_ID,
    DEFAULT_PROFILE_NAME,
    KEY_HOST,
    KEY_ID,
    KEY_PASSWORD,
    KEY_PORT,
    KEY_USERNAME,
    LOG_CHOOSE_ERROR,
    LOG_DEL_DEFAULT_ERROR,
    LOG_DEL_ERROR,
    LOG_DEL_NO_SELECT_ERROR,
    LOG_DEL_SUCCESS,
    LOG_SAVE_ERROR,
    LOG_SAVE_NO_HOST_ERROR,
    LOG_SAVE_SUCCESS,
)
from modules.db import delete_profile, get_profile, get_profiles, save_profile


def load_profiles(self):
    profiles = get_profiles()

    host, username, password, port = (
        profiles[0][KEY_HOST],
        profiles[0][KEY_USERNAME],
        profiles[0][KEY_PASSWORD],
        profiles[0][KEY_PORT],
    )

    self.hostname.setText(str(host))
    self.port.setText(str(port))
    self.username.setText(username)
    self.password.setText(str(password))

    for profile in profiles:
        if profile[KEY_ID] == DEFAULT_PROFILE_ID:
            self.profile_combo.addItem(DEFAULT_PROFILE_NAME, profile[KEY_ID])
        else:
            self.profile_combo.addItem(
                f"{profile[KEY_HOST]}:{profile[KEY_PORT]} ({profile[KEY_USERNAME]})",
                profile[KEY_ID],
            )


def choose_profile_from_combobox(self):
    selected_index = self.profile_combo.currentIndex()

    if selected_index == COMBO_INDEX_EMPTY:
        self.hostname.clear()
        self.port.clear()
        self.username.clear()
        self.password.clear()
        return

    profile_id = self.profile_combo.itemData(selected_index)

    try:
        host, username, password, port = get_profile(profile_id)
        self.hostname.setText(host)
        self.port.setText(str(port))
        self.username.setText(username)
        self.password.setText(str(password))

    except Exception as e:
        self.log(LOG_CHOOSE_ERROR.format(error=e))


def load_profiles_to_db(self):
    host = self.hostname.text().strip()
    port_text = self.port.text().strip()
    username = self.username.text().strip() or DEFAULT_FTP_USER
    password = self.password.text().strip()

    if not host:
        self.log(LOG_SAVE_NO_HOST_ERROR)
        return

    port = int(port_text) if port_text else DEFAULT_FTP_PORT

    try:
        new_profile_id = save_profile(
            host=host, username=username, password=password, port=port
        )
        self.log(LOG_SAVE_SUCCESS.format(host=host))

        display_text = f"{host}:{port} ({username})"
        self.profile_combo.addItem(display_text, new_profile_id)

        last_index = self.profile_combo.count() - 1
        self.profile_combo.setCurrentIndex(last_index)

        self.choose_profile_from_combobox()

    except Exception as e:
        self.log(LOG_SAVE_ERROR.format(error=e))


def delete_profile_from_db(self):
    selected_index = self.profile_combo.currentIndex()
    if selected_index == COMBO_INDEX_EMPTY:
        self.log(LOG_DEL_NO_SELECT_ERROR)
        return

    profile_id = self.profile_combo.itemData(selected_index)

    if profile_id == DEFAULT_PROFILE_ID:
        self.log(LOG_DEL_DEFAULT_ERROR)
        return

    host = self.profile_combo.currentText()

    try:
        delete_profile(profile_id=profile_id)
        self.log(LOG_DEL_SUCCESS.format(host=host))

        self.profile_combo.removeItem(selected_index)

        if self.profile_combo.count() > 0:
            self.profile_combo.setCurrentIndex(0)
        else:
            self.profile_combo.setCurrentIndex(COMBO_INDEX_EMPTY)

        self.choose_profile_from_combobox()

    except Exception as e:
        self.log(LOG_DEL_ERROR.format(error=e))
