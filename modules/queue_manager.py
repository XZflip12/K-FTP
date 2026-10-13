import asyncio
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional

import aioftp
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QTableWidgetItem

from misc.format_size import format_size


class TaskStatus(Enum):
    QUEUED = "Queued"
    RUNNING = "Running"
    PAUSED = "Paused"
    DONE = "Done"
    ERROR = "Error"
    CANCELLED = "Cancelled"


@dataclass
class TransferTask:
    row: int
    file_name: str
    direction: str
    source_path: str
    dest_path: str
    total_size: int
    transferred: int = 0
    status: TaskStatus = TaskStatus.QUEUED


class QueueManager:

    def __init__(self, main_window):
        self.ui = main_window
        self.tasks: list[TransferTask] = []
        self.current_task: Optional[TransferTask] = None
        self.is_paused = False
        self.worker_task: Optional[asyncio.Task] = None
        self.transfer_client: Optional[aioftp.Client] = None

    async def _get_transfer_client(self) -> aioftp.Client:
        """Maintains a dedicated FTP connection for file transfers."""
        if self.transfer_client is not None:
            try:
                await self.transfer_client.get_current_directory()
            except Exception:
                await self._close_transfer_client()

        if self.transfer_client is None:
            host = self.ui.hostname.text().strip()
            port = int(self.ui.port.text().strip() or 21)
            username = self.ui.username.text().strip() or "anonymous"
            password = self.ui.password.text().strip()

            self.transfer_client = aioftp.Client(socket_timeout=15)
            await self.transfer_client.connect(host, port=port)
            await self.transfer_client.login(username, password)

        return self.transfer_client

    async def _close_transfer_client(self):
        """Hard-closes the transfer connection to prevent lingering network buffers."""
        if self.transfer_client:
            try:
                await self.transfer_client.quit()
            except Exception:
                pass
            finally:
                self.transfer_client = None

    def _update_progress_text(self, task: TransferTask):
        """Updates the progress cell with pure text: percentages and downloaded size."""
        item = self.ui.table_queue.item(task.row, 4)
        if not item:
            return

        if task.total_size > 0:
            percent = int((task.transferred / task.total_size) * 100)
            percent = min(percent, 100)
            text = f"{percent}% ({format_size(task.transferred)} / {format_size(task.total_size)})"
        else:
            text = f"{format_size(task.transferred)}"

        item.setText(text)

    def add_task(
        self,
        file_name: str,
        direction: str,
        source_path: str,
        dest_path: str,
        total_size: int,
    ):
        """Adds a task to the queue table and starts the worker."""
        table = self.ui.table_queue
        row = table.rowCount()
        table.insertRow(row)

        table.setItem(row, 0, QTableWidgetItem(file_name))
        where_text = "Server -> Local" if direction == "Download" else "Local -> Server"
        table.setItem(row, 1, QTableWidgetItem(where_text))
        table.setItem(row, 2, QTableWidgetItem(format_size(total_size)))

        status_item = QTableWidgetItem(TaskStatus.QUEUED.value)
        table.setItem(row, 3, status_item)

        initial_text = (
            f"0% (0 B / {format_size(total_size)})" if total_size > 0 else "0 B"
        )
        progress_item = QTableWidgetItem(initial_text)
        progress_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        table.setItem(row, 4, progress_item)

        task = TransferTask(
            row=row,
            file_name=file_name,
            direction=direction,
            source_path=source_path,
            dest_path=dest_path,
            total_size=total_size,
        )
        self.tasks.append(task)
        self.ui.log(f"Added to queue: {file_name} ({direction})")

        if not self.worker_task or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._process_queue())

    def update_task_status(self, task: TransferTask, status: TaskStatus):
        task.status = status
        self.ui.table_queue.item(task.row, 3).setText(status.value)

    async def _process_queue(self):
        """Processes queued items one by one."""
        while True:
            if self.is_paused:
                await asyncio.sleep(0.5)
                continue

            pending = [t for t in self.tasks if t.status == TaskStatus.QUEUED]
            if not pending:
                break

            task = pending[0]
            self.current_task = task
            self.update_task_status(task, TaskStatus.RUNNING)

            try:
                await self._execute_transfer(task)

                if task.status == TaskStatus.RUNNING:
                    self.update_task_status(task, TaskStatus.DONE)
                    task.transferred = task.total_size
                    self._update_progress_text(task)
                    self.ui.log(f"Transfer completed: {task.file_name}")
                elif task.status == TaskStatus.PAUSED:
                    self.ui.log(f"Paused: {task.file_name}")
                elif task.status == TaskStatus.CANCELLED:
                    self.ui.log(f"Transfer cancelled: {task.file_name}")

            except Exception as e:
                self.update_task_status(task, TaskStatus.ERROR)
                self.ui.log(f"Transfer error: {task.file_name} - {e}")
                await self._close_transfer_client()

            self.current_task = None

    async def _execute_transfer(self, task: TransferTask):
        """Transfers file data safely and drops TCP connection upon pause/cancel."""
        client = await self._get_transfer_client()
        chunk_size = 64 * 1024

        if task.total_size <= 0:
            try:
                stat = await client.stat(task.source_path)
                task.total_size = int(stat.get("size", 0))
                self.ui.table_queue.item(task.row, 2).setText(
                    format_size(task.total_size)
                )
            except Exception:
                pass

        if task.direction == "Download":
            dest_file = Path(task.dest_path) / task.file_name
            offset = dest_file.stat().st_size if dest_file.exists() else 0
            task.transferred = offset
            self._update_progress_text(task)

            stream = await client.download_stream(task.source_path, offset=offset)
            mode = "ab" if offset > 0 else "wb"

            try:
                with open(dest_file, mode) as f:
                    while True:
                        if task.status != TaskStatus.RUNNING:
                            await client.abort()
                            stream.close()
                            await self._close_transfer_client()
                            break

                        # Читаем чанк с таймаутом 10 сек (защита от вечного зависания):
                        try:
                            block = await asyncio.wait_for(
                                stream.read(chunk_size), timeout=10.0
                            )
                        except asyncio.TimeoutError:
                            # Если сокет застрял — разрываем и пробуем заново
                            raise Exception("Connection stalled (socket timeout)")

                        if not block:
                            await stream.finish()
                            break

                        f.write(block)
                        task.transferred += len(block)
                        self._update_progress_text(task)
            except Exception:
                stream.close()
                await self._close_transfer_client()
                raise

        elif task.direction == "Upload":
            local_file = Path(task.source_path)
            remote_dest = f"{task.dest_path}/{task.file_name}".replace("//", "/")
            offset = task.transferred
            self._update_progress_text(task)

            stream = await client.upload_stream(remote_dest, offset=offset)

            try:
                with open(local_file, "rb") as f:
                    if offset > 0:
                        f.seek(offset)
                    while True:
                        if task.status != TaskStatus.RUNNING:
                            try:
                                await client.abort()
                            except Exception:
                                pass
                            stream.close()
                            await self._close_transfer_client()
                            break

                        block = f.read(chunk_size)
                        if not block:
                            await stream.finish()
                            break

                        await stream.write(block)
                        task.transferred += len(block)
                        self._update_progress_text(task)
            except Exception:
                stream.close()
                await self._close_transfer_client()
                raise

    def pause_current(self):
        """Signals active task to pause."""
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            self.update_task_status(self.current_task, TaskStatus.PAUSED)

    def resume_queue(self):
        """Resumes paused tasks and restarts queue worker."""
        for t in self.tasks:
            if t.status == TaskStatus.PAUSED:
                self.update_task_status(t, TaskStatus.QUEUED)

        self.is_paused = False
        if not self.worker_task or self.worker_task.done():
            self.worker_task = asyncio.create_task(self._process_queue())
        self.ui.log("Queue resumed")

    def cancel_or_clear(self):
        """Cancels transfer and clears table."""
        if self.current_task and self.current_task.status == TaskStatus.RUNNING:
            self.update_task_status(self.current_task, TaskStatus.CANCELLED)

        self.tasks.clear()
        self.ui.table_queue.setRowCount(0)
        self.ui.log("Queue cleared")
