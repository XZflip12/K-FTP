import asyncio

import aioftp

from config import DEFAULT_SERVER_HOST, DEFAULT_SERVER_PORT


async def run_server():
    server = aioftp.Server()
    print(f"Локальный FTP-сервер запущен на port {DEFAULT_SERVER_PORT}...")
    await server.run(host=DEFAULT_SERVER_HOST, port=DEFAULT_SERVER_PORT)


if __name__ == "__main__":
    asyncio.run(run_server())
