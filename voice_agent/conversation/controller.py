from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from voice_agent.speech.scheduler import SpeechPriority
from voice_agent.turn.engine import UserTurn


class Intent(str, Enum):
    CHAT = "chat"
    START_TASK = "start_task"
    UPDATE_TASK = "update_task"
    ASK_PROGRESS = "ask_progress"
    PAUSE_TASK = "pause_task"
    RESUME_TASK = "resume_task"
    CANCEL_TASK = "cancel_task"
    SIMPLE_ACK = "simple_ack"


@dataclass(frozen=True)
class IntentResult:
    intent: Intent
    skill_name: str | None = None


class ConversationController:
    def __init__(self, agent_runtime, speech_scheduler) -> None:
        self.agent_runtime = agent_runtime
        self.speech_scheduler = speech_scheduler

    async def handle_turn(self, turn: UserTurn) -> None:
        text = turn.text.strip()
        if not text:
            return
        print(f"USER: {text}")
        result = await self.classify_intent(text)
        if result.intent == Intent.SIMPLE_ACK:
            return
        if result.intent == Intent.CANCEL_TASK:
            await self.agent_runtime.cancel_task()
            return
        if result.intent == Intent.PAUSE_TASK:
            await self.agent_runtime.pause_task()
            return
        if result.intent == Intent.RESUME_TASK:
            await self.agent_runtime.resume_task()
            return
        if result.intent == Intent.ASK_PROGRESS:
            await self.agent_runtime.report_progress()
            return
        if result.intent == Intent.UPDATE_TASK:
            await self.agent_runtime.update_task(text)
            return
        if result.intent == Intent.START_TASK:
            await self.agent_runtime.start_task(text, result.skill_name)
            return
        await self.agent_runtime.chat(text)

    async def classify_intent(self, text: str) -> IntentResult:
        normalized = text.strip().lower()
        compact = "".join(normalized.split())

        if compact in {"嗯", "嗯嗯", "好", "好的", "行", "可以", "收到"}:
            return IntentResult(Intent.SIMPLE_ACK)
        if any(keyword in normalized for keyword in ("取消", "别查了", "不用了", "停止任务", "结束任务")):
            return IntentResult(Intent.CANCEL_TASK)
        if any(keyword in normalized for keyword in ("暂停", "先停一下", "等一下")):
            return IntentResult(Intent.PAUSE_TASK)
        if compact in {"继续", "接着来", "继续吧"} or "继续执行" in normalized:
            return IntentResult(Intent.RESUME_TASK)
        if any(keyword in normalized for keyword in ("进度", "到哪", "怎么样了", "查到什么")):
            return IntentResult(Intent.ASK_PROGRESS)
        if self.agent_runtime.current_task is not None and any(
            keyword in normalized for keyword in ("加上", "也加", "顺便", "改成", "换成", "补充")
        ):
            return IntentResult(Intent.UPDATE_TASK)
        if any(keyword in normalized for keyword in ("测试长任务", "假任务", "长任务")):
            return IntentResult(Intent.START_TASK, "fake_long_task")
        if any(keyword in normalized for keyword in ("帮我", "查", "搜索", "搜", "整理", "对比", "比较")):
            skill = await self.agent_runtime.skill_registry.match(text)
            return IntentResult(Intent.START_TASK, skill.name)
        return IntentResult(Intent.CHAT)

