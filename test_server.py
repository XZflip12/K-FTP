import asyncio
import aioftp
from config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


async def run_server():
    # Ограничиваем скорость, например, до 1 МБ/с (1024 * 1024 байт/сек)
    # При таком лимите файл 200 МБ будет качаться ~200 секунд (по 0.5% в секунду)
    SPEED_LIMIT = 1024 * 1024  # 1 MB/s

    server = aioftp.Server(
        read_speed_limit_per_connection=SPEED_LIMIT,
        write_speed_limit_per_connection=SPEED_LIMIT,
    )

    print(
        f"Локальный FTP-сервер запущен на port {DEFAULT_SERVER_PORT} с лимитом 1 МБ/с..."
    )
    await server.run(host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT)


if __name__ == "__main__":
    asyncio.run(run_server())
