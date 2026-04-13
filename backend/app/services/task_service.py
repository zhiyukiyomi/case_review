from __future__ import annotations

import threading
import uuid
from concurrent.futures import Future, ThreadPoolExecutor
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from app.config import settings


@dataclass
class TaskRecord:
    task_id: str
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    result: dict[str, Any] | None = None
    error: str | None = None


class TaskService:
    def __init__(self) -> None:
        self.executor = ThreadPoolExecutor(max_workers=settings.max_workers)
        self._records: dict[str, TaskRecord] = {}
        self._lock = threading.Lock()

    def submit(self, task_callable: Callable[[], dict[str, Any]]) -> TaskRecord:
        task_id = uuid.uuid4().hex
        record = TaskRecord(task_id=task_id, status="running")
        with self._lock:
            self._records[task_id] = record

        future = self.executor.submit(task_callable)
        future.add_done_callback(lambda item, current_task_id=task_id: self._finalize(current_task_id, item))
        return record

    def _finalize(self, task_id: str, future: Future) -> None:
        with self._lock:
            record = self._records[task_id]

        try:
            result = future.result()
        except Exception as exc:  # noqa: BLE001
            with self._lock:
                record.status = "failed"
                record.error = str(exc)
                record.updated_at = datetime.utcnow().isoformat()
            return

        with self._lock:
            record.status = "completed"
            record.result = result
            record.updated_at = datetime.utcnow().isoformat()

    def get(self, task_id: str) -> TaskRecord | None:
        with self._lock:
            return self._records.get(task_id)


task_service = TaskService()
