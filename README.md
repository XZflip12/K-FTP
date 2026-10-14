# K-FTP

![K-FTP](header.png)

Desktop FTP client built with PyQt6, aioftp and qasync.

## Features

- Two-pane view: local files and remote server
- Lazy loading of remote directories
- Transfer queue with pause, resume and clear; interrupted downloads are resumed
- Rename, delete and create folders on both sides via context menu
- Connection profiles stored in SQLite
- Path bars for both panes

## Requirements

- Python 3.10+

## Installation

```bash
git clone https://github.com/XZFlip12/k-ftp.git
cd k-ftp
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Note: `requirements.txt` is UTF-16 encoded.

## Usage

```bash
python main.py
```

Enter host, port, username and password, then press **Connect**. Use **App → Save Profile** to store the connection and **App → Delete Profile** to remove it (the `Default` profile can't be deleted).

### Test server

A local server for trying the client without a real FTP host (`localhost:2121`, anonymous login, 1 MB/s speed limit):

```bash
cd modules
python test_server.py
```

## Development

The UI is designed in Qt Designer. After editing `user_interface/ClientUI.ui`, regenerate the Python module:

```bash
pyuic6 user_interface/ClientUI.ui -o user_interface/ui_client.py
```

## Known issues

- Settings and Credits menu items are not implemented
- Plain FTP only, no FTPS/SFTP: traffic, including the password, is not encrypted
- Profile passwords are stored in plain text in `profiles.db`
- No automated tests

## License

[GPL-3.0](LICENSE)