from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

from voice_agent.research.pipeline import AcademicResearchPipeline, infer_research_mode
from voice_agent.research.storage import ResearchStorage
from voice_agent.tools.base import ToolResult


class AcademicResearchTool:
    name = "academic_research"
    description = "Searches scholarly sources and writes a survey or SOTA research report to a Markdown artifact."

    def __init__(
        self,
        pipeline: AcademicResearchPipeline | None = None,
        storage: ResearchStorage | None = None,
        llm=None,
        enable_llm_writer: bool = False,
        pipeline_timeout_seconds: float = 180.0,
        writer_timeout_seconds: float = 120.0,
    ) -> None:
        self.pipeline = pipeline or AcademicResearchPipeline()
        self.storage = storage or ResearchStorage()
        self.llm = llm
        self.enable_llm_writer = enable_llm_writer
        self.pipeline_timeout_seconds = pipeline_timeout_seconds
        self.writer_timeout_seconds = writer_timeout_seconds

    async def execute(self, arguments: dict[str, Any], progress_callback, cancel_token: asyncio.Event) -> ToolResult:
        query = str(arguments.get("query", "")).strip()
        if not query:
            return ToolResult(ok=False, data={}, error="missing query")
        limit = int(arguments.get("limit", 24))
        mode = infer_research_mode(str(arguments.get("mode") or query))

        progress_messages: list[str] = []

        def sync_progress(message: str) -> None:
            progress_messages.append(message)

        await progress_callback("我开始做科研文献调研。")
        if cancel_token.is_set():
            return ToolResult(ok=False, data={}, error="cancelled")

        try:
            report = await asyncio.wait_for(
                asyncio.to_thread(self.pipeline.run, query, mode, limit, sync_progress),
                timeout=self.pipeline_timeout_seconds,
            )
            markdown = report.markdown
            evidence_markdown: str | None = None
            if self.enable_llm_writer and self.llm is not None and self.llm.__class__.__name__ != "FakeLLM":
                await progress_callback("我正在生成 STORM 风格最终综述。")
                evidence_markdown = markdown
                markdown = await self._write_clean_storm_article(query, markdown)
            for message in progress_messages[-5:]:
                if cancel_token.is_set():
                    return ToolResult(ok=False, data={}, error="cancelled")
                await progress_callback(message)
            path = self.storage.save_markdown(str(arguments.get("task_id") or "manual"), _slug(query), markdown)
            evidence_path = None
            if evidence_markdown is not None:
                evidence_path = path.with_name("evidence_report.md")
                evidence_path.write_text(evidence_markdown, encoding="utf-8")
            return ToolResult(
                ok=True,
                data={
                    "query": query,
                    "mode": report.mode.value,
                    "paper_count": len(report.papers),
                    "sota_claim_count": len(report.sota_claims),
                    "report_path": str(path),
                    "evidence_report_path": str(evidence_path) if evidence_path else None,
                    "top_papers": [
                        {
                            "title": paper.title,
                            "year": paper.year,
                            "url": paper.url,
                            "source": paper.source,
                            "citation_count": paper.citation_count,
                        }
                        for paper in report.papers[:5]
                    ],
                },
            )
        except Exception as exc:
            return ToolResult(ok=False, data={"query": query}, error=str(exc))

    async def _write_clean_storm_article(self, query: str, markdown: str) -> str:
        evidence = _truncate(markdown, 26000)
        messages = [
            {
                "role": "system",
                "content": (
                    "你是严谨的科研综述写作助手。请模仿 STORM 最终 Wikipedia-style article 的写法，"
                    "只输出干净的最终综述正文，不输出工作流日志、运行轨迹、问答日志、Evidence Pack、Citation Audit、质量检查清单或引用自检。"
                    "先吸收 evidence report 中的多视角问答、refined outline、section evidence 和参考文献，但这些只能作为内部依据。"
                    "只允许使用 evidence report 中出现的论文、系统、年份、指标、URL 和事实；不要新增来源。"
                    "必须保留 [P#] inline citations，每个实质性段落至少一个引用；无法被证据支撑的内容不要写。"
                    "Markdown 一级标题只用主题名；之后只使用这些二级章节，顺序固定："
                    "summary, Background, System Architecture, Technological Approaches, "
                    "Notable Systems and Implementations, Applications, Evaluation and Benchmarking, "
                    "Challenges and Limitations, Ethical and Legal Considerations, Future Directions, References。"
                    "正文用中文，章节标题保留英文。References 只列 evidence report 里的 [P#] 文献。"
                    "写作要像综述文章，而不是项目审计报告；不要出现“本报告”“本轮”“证据块”“source_type”“score”等工程词。"
                ),
            },
            {"role": "user", "content": f"主题：{query}\n\nEvidence report:\n{evidence}"},
        ]
        try:
            synthesis = (await asyncio.wait_for(self.llm.generate(messages), timeout=self.writer_timeout_seconds)).strip()
        except Exception:
            return markdown
        if not synthesis:
            return markdown
        return _clean_final_article(synthesis, markdown)


def _slug(value: str) -> str:
    return "_".join(value.lower().split())[:48]


def _truncate(value: str, max_length: int) -> str:
    if len(value) <= max_length:
        return value
    return value[: max_length - 3] + "..."


def _clean_final_article(article: str, evidence_markdown: str) -> str:
    article = _strip_unwanted_sections(article.strip())
    if "## References" not in article:
        article = article.rstrip() + "\n\n## References\n\n" + _extract_references(evidence_markdown)
    return article.rstrip() + "\n"


def _strip_unwanted_sections(markdown: str) -> str:
    unwanted = {
        "storm-style 运行轨迹",
        "storm-style 多视角问题",
        "storm-style 多视角问答日志",
        "建议综述大纲",
        "section evidence pack",
        "citation audit",
        "openscholar-style 证据覆盖",
        "质量检查清单",
        "引用自检",
        "调研范围与方法",
        "代表论文",
        "关键结论",
        "综合对比",
    }
    kept: list[str] = []
    skipping = False
    for line in markdown.splitlines():
        if line.startswith("## "):
            title = line[3:].strip().lower()
            skipping = title in unwanted
        elif line.startswith("# "):
            skipping = False
        if not skipping:
            kept.append(line)
    return "\n".join(kept).strip()


def _extract_references(evidence_markdown: str) -> str:
    lines = evidence_markdown.splitlines()
    in_refs = False
    refs: list[str] = []
    for line in lines:
        if line.strip() == "## 参考文献":
            in_refs = True
            continue
        if in_refs and line.startswith("## "):
            break
        if in_refs and line.strip().startswith("- [P"):
            refs.append(line.strip())
    return "\n".join(refs) if refs else "- References unavailable in evidence report."
