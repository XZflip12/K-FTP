# Настройки подключения по умолчанию
DEFAULT_FTP_PORT = 21
DEFAULT_FTP_USER = "anonymous"
DEFAULT_SOCKET_TIMEOUT = 5

# Тексты логов и уведомлений
LOG_EMPTY_HOST = "Host is empty"
LOG_CONNECTING = "Connecting to host: {host}:{port}..."
LOG_SUCCESS = "Connected to host and logged in!"
LOG_FETCHING = "Fetching root files..."
LOG_FETCH_SUCCESS = "Files fetched successfully!"
LOG_ERROR = "Error: {error}"

# Форматы логов
LOG_FORMAT = "%H:%M:%S"

# Идентификация профилей и ключи БД
DEFAULT_PROFILE_ID = 1
DEFAULT_PROFILE_NAME = "Default"
COMBO_INDEX_EMPTY = -1

KEY_ID = "id"
KEY_HOST = "host"
KEY_PORT = "port"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"

# Дефолтные значения FTP
DEFAULT_FTP_USER = "anonymous"
DEFAULT_FTP_PORT = 21

# Тексты ошибок и логирования
LOG_CHOOSE_ERROR = "Error: {error}"
LOG_SAVE_NO_HOST_ERROR = "Error: cannot save profile without host"
LOG_SAVE_SUCCESS = "Profile [{host}] saved successfully!"
LOG_SAVE_ERROR = "Saving profile error: {error}"

LOG_DEL_NO_SELECT_ERROR = "Error: cannot delete profile without selected item"
LOG_DEL_DEFAULT_ERROR = "Error: Default profile cannot be deleted!"
LOG_DEL_SUCCESS = "Profile [{host}] deleted successfully!"
LOG_DEL_ERROR = "Deleting profile error: {error}"

# Размеры колонок интерфейса
LOCAL_COLUMN_0_WIDTH = 250
REMOTE_COLUMN_0_WIDTH = 250
REMOTE_COLUMN_1_WIDTH = 100

# Заголовки таблицы удаленного сервера
HEADER_NAME = "Name"
HEADER_SIZE = "Size"
HEADER_TYPE = "Type"

# Ключи и типы данных файловой структуры
KEY_TYPE = "type"
KEY_SIZE = "size"
TYPE_DIR = "dir"

# Текстовые подписи элементов дерева
TEXT_FOLDER = "Folder"
TEXT_FILE = "File"
TEXT_LOADING = "Loading..."

# Сообщения для логов
LOG_FETCH_SUBFOLDER = "Fetching subfolder: {path}..."
LOG_FETCH_SUBFOLDER_ERROR = "Error fetching subfolder: {error}"

# Имя файла базы данных
DB_FILE_NAME = "profiles.db"

# Дефолтные значения для профиля по умолчанию в БД
DEFAULT_DB_HOST = "localhost"
DEFAULT_DB_USER = "default_user"
DEFAULT_DB_PASS = "default_pass"
DEFAULT_DB_PORT = 21

# Ключи для словаря профиля
KEY_ID = "id"
KEY_HOST = "host"
KEY_USERNAME = "username"
KEY_PASSWORD = "password"
KEY_PORT = "port"

# SQL Запросы
SQL_CREATE_TABLE = """
    CREATE TABLE IF NOT EXISTS profiles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        host TEXT NOT NULL,
        username TEXT NOT NULL,
        password TEXT NOT NULL,
        port INTEGER NOT NULL DEFAULT 21
        )
    """

SQL_COUNT_PROFILES = "SELECT COUNT(*) FROM profiles"

SQL_INSERT_DEFAULT = """
    INSERT INTO profiles (host, username, password, port)
    VALUES ('localhost', 'default_user', 'default_pass', 21)
"""

SQL_INSERT_PROFILE = (
    "INSERT INTO profiles (host, username, password, port) VALUES (?, ?, ?, ?)"
)

SQL_DELETE_PROFILE = "DELETE FROM profiles WHERE id = ?"

SQL_SELECT_ALL = "SELECT * FROM profiles"

SQL_SELECT_BY_ID = "SELECT host, username, password, port FROM profiles WHERE id = ?"

# Дефолтные значения для тестового сервера
DEFAULT_SERVER_HOST = "localhost"
DEFAULT_SERVER_PORT = 2121
