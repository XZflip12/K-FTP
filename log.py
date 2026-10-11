from datetime import datetime

from config import LOG_FORMAT


def log(self, message: str):
    timestamp = datetime.now().strftime(LOG_FORMAT)
    formated_message = f"[{timestamp}], {message}"
    self.log_console.appendPlainText(formated_message)
