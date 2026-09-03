from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class ResearchStage:
    name: str
    description: str


@dataclass
class ResearchStageMachine:
    stages: list[ResearchStage]
    current_index: int = 0
    history: list[str] = field(default_factory=list)

    @property
    def current(self) -> ResearchStage:
        return self.stages[self.current_index]

    @property
    def completed(self) -> bool:
        return self.current_index >= len(self.stages) - 1 and self.current.name == "final"

    def advance(self, note: str = "") -> ResearchStage:
        if note:
            self.history.append(f"{self.current.name}: {note}")
        if self.current_index < len(self.stages) - 1:
            self.current_index += 1
        return self.current


def build_research_stage_machine() -> ResearchStageMachine:
    return ResearchStageMachine(
        stages=[
            ResearchStage("scope", "识别用户目标是综述生成还是 SOTA 调研。"),
            ResearchStage("retrieve", "检索学术数据库并汇总候选论文。"),
            ResearchStage("structure", "生成大纲、证据包或 SOTAClaim。"),
            ResearchStage("verify", "检查元数据、引用和可比性风险。"),
            ResearchStage("write", "写入 Markdown 报告 artifact。"),
            ResearchStage("final", "向用户返回短结论和报告路径。"),
        ]
    )
