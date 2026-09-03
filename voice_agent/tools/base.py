from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Protocol


ProgressCallback = Callable[[str], Awaitable[None]]


@dataclass(frozen=True)
class ToolResult:
    ok: bool
    data: dict[str, Any]
    error: str | None = None


class Tool(Protocol):
    name: str
    description: str

    async def execute(
        self,
        arguments: dict[str, Any],
        progress_callback: ProgressCallback,
        cancel_token: asyncio.Event,
    ) -> ToolResult:
        ...

