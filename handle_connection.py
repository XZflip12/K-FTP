import aioftp

from config import (
    DEFAULT_FTP_PORT,
    DEFAULT_FTP_USER,
    DEFAULT_SOCKET_TIMEOUT,
    LOG_CONNECTING,
    LOG_EMPTY_HOST,
    LOG_ERROR,
    LOG_FETCH_SUCCESS,
    LOG_FETCHING,
    LOG_SUCCESS,
)


async def handle_connection(self):
    host = self.hostname.text().strip()
    port_text = self.port.text().strip()
    port = int(port_text) if port_text else DEFAULT_FTP_PORT
    username = self.username.text().strip() or DEFAULT_FTP_USER
    password = self.password.text().strip()

    if not host:
        self.log(LOG_EMPTY_HOST)
        return

    self.connect_btn.setEnabled(False)
    self.log(LOG_CONNECTING.format(host=host, port=port))

    try:
        self.ftp_client = aioftp.Client(socket_timeout=DEFAULT_SOCKET_TIMEOUT)
        await self.ftp_client.connect(host, port=port)
        await self.ftp_client.login(username, password)
        self.log(LOG_SUCCESS)

        self.log(LOG_FETCHING)
        self.remote_model.removeRows(0, self.remote_model.rowCount())

        items_list = []
        async for path, stat in self.ftp_client.list():
            if path.name in [".", ".."]:
                continue
            items_list.append((path, stat))

        items_list.sort(key=lambda x: (x[1].get("type") != "dir", x[0].name.lower()))

        # Добавляем файлы в корень модели
        for path, stat in items_list:
            self.add_tree_item(self.remote_model, path, stat)

        self.log(LOG_FETCH_SUCCESS)

    except Exception as e:
        self.log(LOG_ERROR.format(error=e))
        self.ftp_client = None

    finally:
        self.connect_btn.setEnabled(True)
