from __future__ import annotations

import asyncio
from typing import Any

from voice_agent.tools.base import ToolResult


class FakeLongTaskTool:
    name = "fake_long_task"
    description = "Runs a cancellable synthetic long task for duplex interruption tests."

    async def execute(self, arguments: dict[str, Any], progress_callback, cancel_token: asyncio.Event) -> ToolResult:
        steps = int(arguments.get("steps", 5))
        delay = float(arguments.get("delay", 0.4))
        for index in range(steps):
            if cancel_token.is_set():
                return ToolResult(ok=False, data={"cancelled_at": index}, error="cancelled")
            await progress_callback(f"我正在处理第 {index + 1} 步。")
            await asyncio.sleep(delay)
        return ToolResult(ok=True, data={"message": "fake_long_task completed", "steps": steps})

