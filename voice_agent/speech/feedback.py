from __future__ import annotations

import asyncio

from voice_agent.infrastructure.event_bus import EventBus
from voice_agent.speech.scheduler import SpeechPriority


class FeedbackController:
    def __init__(self, event_bus: EventBus, speech_scheduler) -> None:
        self.event_bus = event_bus
        self.speech_scheduler = speech_scheduler
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None:
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task is None:
            return
        self._task.cancel()
        try:
            await self._task
        except asyncio.CancelledError:
            pass
        self._task = None

    async def on_llm_start(self) -> None:
        await self.speech_scheduler.replace_progress("我正在确认下一步。")

    async def on_tool_start(self, tool_name: str) -> None:
        if tool_name == "web_search":
            await self.speech_scheduler.replace_progress("我正在搜索相关资料。")
        elif tool_name == "academic_research":
            await self.speech_scheduler.replace_progress("我开始在后台做科研文献调研，完成后会告诉你。")
        elif tool_name == "fake_long_task":
            await self.speech_scheduler.replace_progress("我正在处理这个任务。")
        else:
            await self.speech_scheduler.replace_progress("我正在执行下一步。")

    async def on_tool_progress(self, message: str) -> None:
        await self.speech_scheduler.replace_progress(message)

    async def on_task_complete(self) -> None:
        return None

    async def _run(self) -> None:
        queue = self.event_bus.subscribe("*")
        while True:
            event = await queue.get()
            if event.type == "LLMStarted":
                continue
            elif event.type == "ToolStarted":
                await self.on_tool_start(str(event.payload.get("tool_name", "")))
            elif event.type == "ToolProgress":
                await self.on_tool_progress(str(event.payload.get("message", "")))
            elif event.type == "ToolError":
                await self.speech_scheduler.say("刚才的查询没有成功，我在换一种方式。", SpeechPriority.ERROR)
            elif event.type == "TaskCompleted":
                await self.on_task_complete()
