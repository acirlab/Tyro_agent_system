from __future__ import annotations

import asyncio
from typing import Any

from voice_agent.agent.planner import SimplePlanner
from voice_agent.agent.task import AgentTask, TaskStatus
from voice_agent.infrastructure.event_bus import EventBus
from voice_agent.speech.scheduler import SpeechPriority
from voice_agent.skills.registry import SkillRegistry
from voice_agent.tools.registry import ToolRegistry


class AgentRuntime:
    def __init__(
        self,
        llm,
        tool_registry: ToolRegistry,
        skill_registry: SkillRegistry,
        speech_scheduler,
        event_bus: EventBus,
    ) -> None:
        self.llm = llm
        self.tool_registry = tool_registry
        self.skill_registry = skill_registry
        self.speech_scheduler = speech_scheduler
        self.event_bus = event_bus
        self.planner = SimplePlanner()
        self.current_task: AgentTask | None = None

    async def start_task(self, goal: str, skill_name: str | None = None) -> AgentTask:
        skill = self.skill_registry.get(skill_name) if skill_name else await self.skill_registry.match(goal)
        task = AgentTask(goal=goal, skill_name=skill.name)
        self.current_task = task
        await self.event_bus.publish("TaskStarted", task_id=task.id, goal=goal, skill_name=skill.name)
        task.runner = asyncio.create_task(self.run_loop(task))
        return task

    async def update_task(self, text: str) -> None:
        if self.current_task is None or self.current_task.status in {TaskStatus.COMPLETED, TaskStatus.CANCELLED}:
            await self.start_task(text)
            return
        self.current_task.goal = f"{self.current_task.goal}\n补充要求：{text.strip()}"
        self.current_task.add_update(text)
        await self.event_bus.publish("TaskUpdated", task_id=self.current_task.id, text=text)
        await self.speech_scheduler.say("好的，我把这个要求加进去。", SpeechPriority.CHAT)

    async def pause_task(self) -> None:
        if self.current_task is None:
            await self.speech_scheduler.say("当前没有正在执行的任务。", SpeechPriority.CHAT)
            return
        self.current_task.pause_event.clear()
        self.current_task.status = TaskStatus.PAUSED
        await self.event_bus.publish("TaskPaused", task_id=self.current_task.id)
        await self.speech_scheduler.say("我先暂停。", SpeechPriority.CHAT)

    async def resume_task(self) -> None:
        if self.current_task is None:
            await self.speech_scheduler.say("当前没有可继续的任务。", SpeechPriority.CHAT)
            return
        self.current_task.pause_event.set()
        self.current_task.status = TaskStatus.RUNNING
        await self.event_bus.publish("TaskResumed", task_id=self.current_task.id)
        await self.speech_scheduler.say("好的，继续。", SpeechPriority.CHAT)

    async def cancel_task(self) -> None:
        if self.current_task is None:
            await self.speech_scheduler.say("当前没有正在执行的任务。", SpeechPriority.CHAT)
            return
        self.current_task.cancel_event.set()
        self.current_task.status = TaskStatus.CANCELLED
        await self.event_bus.publish("TaskCancelled", task_id=self.current_task.id)
        await self.speech_scheduler.say("已取消。", SpeechPriority.CHAT)

    async def report_progress(self) -> None:
        task = self.current_task
        if task is None:
            await self.speech_scheduler.say("当前没有正在执行的任务。", SpeechPriority.CHAT)
            return
        if task.status == TaskStatus.COMPLETED and task.final_answer:
            await self.speech_scheduler.say("任务已经完成。", SpeechPriority.CHAT)
            return
        if task.updates:
            await self.speech_scheduler.say(task.updates[-1], SpeechPriority.CHAT)
            return
        await self.speech_scheduler.say(f"当前任务状态是 {task.status.value}。", SpeechPriority.CHAT)

    async def chat(self, text: str) -> None:
        await self._announce_llm_start(None)
        answer = await self.llm.generate(text)
        await self.speech_scheduler.say(answer or "好的。", SpeechPriority.CHAT)

    async def run_loop(self, task: AgentTask) -> None:
        task.status = TaskStatus.RUNNING
        try:
            skill = self.skill_registry.get(task.skill_name)
            await self._announce_llm_start(task.id)
            decision = await self.planner.first_action(task.goal, skill)

            if decision.type == "tool":
                await task.pause_event.wait()
                if task.cancel_event.is_set():
                    return
                assert decision.tool_name is not None
                tool_arguments = {**(decision.arguments or {}), "task_id": task.id}
                result = await self._run_tool(task, decision.tool_name, tool_arguments)
                task.add_result({"tool": decision.tool_name, "result": result.data, "ok": result.ok, "error": result.error})
                if task.cancel_event.is_set():
                    return
                answer = await self._summarize(task, result.data, result.error)
                task.final_answer = answer
                task.status = TaskStatus.COMPLETED
                await self.event_bus.publish("TaskCompleted", task_id=task.id)
                await self.speech_scheduler.say(answer, SpeechPriority.FINAL)
                return

            answer = await self._direct_answer(task.goal)
            task.final_answer = answer
            task.status = TaskStatus.COMPLETED
            await self.event_bus.publish("TaskCompleted", task_id=task.id)
            await self.speech_scheduler.say(answer, SpeechPriority.FINAL)
        except asyncio.CancelledError:
            task.status = TaskStatus.CANCELLED
            raise
        except Exception as exc:
            task.status = TaskStatus.FAILED
            await self.event_bus.publish("TaskFailed", task_id=task.id, error=str(exc))
            await self.speech_scheduler.say(f"任务执行失败：{exc}", SpeechPriority.ERROR)

    async def _run_tool(self, task: AgentTask, tool_name: str, arguments: dict[str, Any]):
        tool = self.tool_registry.get(tool_name)
        await self.event_bus.publish("ToolStarted", task_id=task.id, tool_name=tool_name)

        async def progress(message: str) -> None:
            task.add_update(message)
            await self.event_bus.publish("ToolProgress", task_id=task.id, tool_name=tool_name, message=message)

        result = await tool.execute(arguments, progress, task.cancel_event)
        if not result.ok:
            await self.event_bus.publish("ToolError", task_id=task.id, tool_name=tool_name, error=result.error)
        return result

    async def _direct_answer(self, goal: str) -> str:
        await self._announce_llm_start(None)
        return await self.llm.generate(goal)

    async def _summarize(self, task: AgentTask, tool_data: dict[str, Any], error: str | None) -> str:
        if error:
            return f"这个任务没有成功：{error}"
        if task.skill_name == "fake_long_task":
            return "任务处理完成。"
        if task.skill_name == "academic_research":
            report_path = tool_data.get("report_path")
            paper_count = tool_data.get("paper_count", 0)
            mode = tool_data.get("mode", "academic_research")
            if report_path:
                return f"科研调研完成，模式是 {mode}，整理了 {paper_count} 篇候选论文。完整报告已写入 {report_path}。"
            return f"科研调研完成，整理了 {paper_count} 篇候选论文。"
        results = tool_data.get("results", [])
        if not results:
            return "我没有找到可靠的搜索结果。"
        compact_results = "\n".join(
            f"{index + 1}. {item.get('title', '')} {item.get('url', '')}"
            for index, item in enumerate(results[:5])
        )
        messages = [
            {
                "role": "system",
                "content": "你是语音助手。基于搜索结果用中文给出简短结论，最多三句话，不要编造搜索结果中没有的信息。",
            },
            {"role": "user", "content": f"用户目标：{task.goal}\n搜索结果：\n{compact_results}"},
        ]
        await self._announce_llm_start(task.id)
        return await self.llm.generate(messages)

    async def _announce_llm_start(self, task_id: str | None) -> None:
        await self.speech_scheduler.replace_progress("我正在确认下一步。")
        await self.event_bus.publish("LLMStarted", task_id=task_id)
