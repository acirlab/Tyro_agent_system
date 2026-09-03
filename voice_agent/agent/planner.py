from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from voice_agent.skills.registry import Skill


@dataclass(frozen=True)
class AgentDecision:
    type: str
    tool_name: str | None = None
    arguments: dict[str, Any] | None = None
    question: str | None = None
    answer: str | None = None


class SimplePlanner:
    async def first_action(self, goal: str, skill: Skill) -> AgentDecision:
        if skill.name == "fake_long_task":
            return AgentDecision(type="tool", tool_name="fake_long_task", arguments={"steps": 8, "delay": 0.5})
        if "academic_research" in skill.tools:
            return AgentDecision(type="tool", tool_name="academic_research", arguments={"query": goal, "limit": 24})
        if "web_search" in skill.tools:
            return AgentDecision(type="tool", tool_name="web_search", arguments={"query": goal, "limit": 5})
        return AgentDecision(type="finish")
