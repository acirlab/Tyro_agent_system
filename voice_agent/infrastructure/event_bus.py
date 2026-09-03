from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class Event:
    type: str
    payload: dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


class EventBus:
    def __init__(self) -> None:
        self._subscribers: dict[str, list[asyncio.Queue[Event]]] = defaultdict(list)
        self._wildcards: list[asyncio.Queue[Event]] = []

    async def publish(self, event: Event | str, **payload: Any) -> None:
        if isinstance(event, str):
            event = Event(type=event, payload=payload)
        queues = [*self._subscribers.get(event.type, []), *self._wildcards]
        for queue in queues:
            await queue.put(event)

    def subscribe(self, event_type: str = "*") -> asyncio.Queue[Event]:
        queue: asyncio.Queue[Event] = asyncio.Queue()
        if event_type == "*":
            self._wildcards.append(queue)
        else:
            self._subscribers[event_type].append(queue)
        return queue

