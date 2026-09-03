from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


@dataclass
class AgentTask:
    goal: str
    skill_name: str
    id: str = field(default_factory=lambda: uuid4().hex)
    status: TaskStatus = TaskStatus.PENDING
    updates: list[str] = field(default_factory=list)
    results: list[dict] = field(default_factory=list)
    final_answer: str | None = None
    runner: asyncio.Task | None = field(default=None, repr=False)
    cancel_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)
    pause_event: asyncio.Event = field(default_factory=asyncio.Event, repr=False)

    def __post_init__(self) -> None:
        self.pause_event.set()

    def add_update(self, text: str) -> None:
        if text.strip():
            self.updates.append(text.strip())

    def add_result(self, result: dict) -> None:
        self.results.append(result)

