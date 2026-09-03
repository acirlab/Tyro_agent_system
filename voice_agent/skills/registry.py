from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Skill:
    name: str
    description: str
    tools: list[str] = field(default_factory=list)
    feedback: dict[str, str] = field(default_factory=dict)


class SkillRegistry:
    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}

    def register(self, skill: Skill) -> None:
        if skill.name in self._skills:
            raise ValueError(f"Skill already registered: {skill.name}")
        self._skills[skill.name] = skill

    def get(self, name: str) -> Skill:
        try:
            return self._skills[name]
        except KeyError as exc:
            raise KeyError(f"Unknown skill: {name}") from exc

    def list(self) -> list[Skill]:
        return list(self._skills.values())

    async def match(self, user_text: str) -> Skill:
        text = user_text.strip().lower()
        if any(
            keyword in text
            for keyword in ("论文", "文献", "综述", "sota", "state of the art", "benchmark", "前沿", "顶会")
        ):
            return self.get("academic_research")
        if any(keyword in text for keyword in ("查", "搜索", "搜", "网页", "资料", "对比", "比较")):
            return self.get("web_research")
        return self.get("general_chat")


def build_default_skill_registry() -> SkillRegistry:
    registry = SkillRegistry()
    registry.register(
        Skill(
            name="general_chat",
            description="普通中文对话",
            tools=[],
            feedback={"start": "我正在想一下。"},
        )
    )
    registry.register(
        Skill(
            name="web_research",
            description="搜索并整理公开资料",
            tools=["web_search"],
            feedback={"start": "我开始搜索相关资料。", "analyze": "我正在整理找到的信息。"},
        )
    )
    registry.register(
        Skill(
            name="academic_research",
            description="检索学术论文并生成综述或 SOTA 调研报告",
            tools=["academic_research"],
            feedback={"start": "我开始做科研文献调研。", "analyze": "我正在整理论文和引用信息。"},
        )
    )
    registry.register(
        Skill(
            name="fake_long_task",
            description="用于验证进度反馈和打断的长任务",
            tools=["fake_long_task"],
            feedback={"start": "我开始处理这个任务。"},
        )
    )
    return registry
