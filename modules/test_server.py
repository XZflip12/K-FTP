import asyncio
import aioftp
from config import (
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    SPEED_LIMIT,
    SHOWED_SPEED_LIMIT,
)


async def run_server():
    server = aioftp.Server(
        read_speed_limit_per_connection=SPEED_LIMIT,
        write_speed_limit_per_connection=SPEED_LIMIT,
    )

    print(
        f"Локальный FTP-сервер запущен на port {DEFAULT_SERVER_PORT} с лимитом {SHOWED_SPEED_LIMIT} МБ/с..."
    )
    await server.run(host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT)


if __name__ == "__main__":
    asyncio.run(run_server())
