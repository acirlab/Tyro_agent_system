import asyncio
import tempfile
import unittest
from pathlib import Path

from voice_agent.research.models import Paper, ResearchMode
from voice_agent.research.pipeline import AcademicResearchPipeline
from voice_agent.research.stage_machine import build_research_stage_machine
from voice_agent.research.storage import ResearchStorage
from voice_agent.tools.builtin.academic_research import AcademicResearchTool


class _FakeSearcher:
    def search(self, query: str, limit: int = 10):
        return [
            Paper(
                title="Agentic Literature Review Systems",
                authors=["A. Researcher"],
                year=2026,
                venue="DemoConf",
                abstract="A framework and pipeline for literature review agents with evaluation and dataset coverage.",
                url="https://example.com/agentic-review",
                citation_count=12,
                source="fake",
            ),
            Paper(
                title="State-of-the-Art Benchmarking for Research Agents",
                authors=["B. Scientist"],
                year=2025,
                venue="DemoBench",
                abstract="This method achieves state-of-the-art results on research agent benchmarks.",
                url="https://example.com/sota-agent",
                citation_count=20,
                source="fake",
            ),
        ][:limit]


class _SynthesisLLM:
    async def generate(self, messages):
        return """# Demo Article

## summary

这是干净的最终综述段落 [P1]。

## Background

这里是背景内容 [P1]。

## Citation Audit

这段不应该出现在最终报告。
"""


class AcademicResearchTests(unittest.TestCase):
    def test_phase2_survey_contains_outline_and_evidence_pack(self):
        pipeline = AcademicResearchPipeline(searchers=[_FakeSearcher()])

        report = pipeline.run("research agent literature review", ResearchMode.SURVEY, limit=5)

        self.assertIn("## 摘要", report.markdown)
        self.assertIn("## 正文综述", report.markdown)
        self.assertIn("## 综合对比", report.markdown)
        self.assertIn("## STORM-style 多视角问题", report.markdown)
        self.assertIn("## STORM-style 运行轨迹", report.markdown)
        self.assertIn("## STORM-style 多视角问答日志", report.markdown)
        self.assertIn("### Direct outline", report.markdown)
        self.assertIn("### Evidence-refined outline", report.markdown)
        self.assertIn("## Citation Audit", report.markdown)
        self.assertIn("## OpenScholar-style 证据覆盖", report.markdown)
        self.assertIn("## 建议综述大纲", report.markdown)
        self.assertIn("## Section Evidence Pack", report.markdown)
        self.assertIn("Agentic Literature Review Systems", report.markdown)
        self.assertIsNotNone(report.storm_trace)
        self.assertGreaterEqual(len(report.storm_trace.perspective_turns), 4)
        self.assertGreaterEqual(report.storm_trace.retrieval_query_count, 4)

    def test_phase3_sota_report_contains_structured_claim(self):
        pipeline = AcademicResearchPipeline(searchers=[_FakeSearcher()])

        report = pipeline.run("research agent SOTA benchmark", ResearchMode.SOTA, limit=5)

        self.assertGreaterEqual(len(report.sota_claims), 1)
        self.assertIn("## SOTA 候选", report.markdown)
        self.assertEqual(report.sota_claims[0].evidence_level, "L1: paper self-claim")

    def test_phase4_research_stage_machine_advances(self):
        machine = build_research_stage_machine()

        self.assertEqual(machine.current.name, "scope")
        machine.advance("mode selected")

        self.assertEqual(machine.current.name, "retrieve")
        self.assertEqual(machine.history, ["scope: mode selected"])


class AcademicResearchToolTests(unittest.IsolatedAsyncioTestCase):
    async def test_phase1_tool_writes_markdown_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = AcademicResearchTool(
                pipeline=AcademicResearchPipeline(searchers=[_FakeSearcher()]),
                storage=ResearchStorage(Path(tmpdir)),
            )
            updates = []

            async def progress(message: str):
                updates.append(message)

            result = await tool.execute(
                {"query": "research agent literature review", "limit": 5, "task_id": "demo"},
                progress,
                asyncio.Event(),
            )

            self.assertTrue(result.ok)
            self.assertTrue(Path(result.data["report_path"]).exists())
            self.assertIn("科研文献调研", updates[0])

    async def test_llm_writer_saves_clean_report_and_evidence_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tool = AcademicResearchTool(
                pipeline=AcademicResearchPipeline(searchers=[_FakeSearcher()]),
                storage=ResearchStorage(Path(tmpdir)),
                llm=_SynthesisLLM(),
                enable_llm_writer=True,
            )

            async def progress(message: str):
                pass

            result = await tool.execute(
                {"query": "research agent literature review", "limit": 5, "task_id": "demo"},
                progress,
                asyncio.Event(),
            )

            self.assertTrue(result.ok)
            report_path = Path(result.data["report_path"])
            evidence_path = Path(result.data["evidence_report_path"])
            report_text = report_path.read_text(encoding="utf-8")
            evidence_text = evidence_path.read_text(encoding="utf-8")
            self.assertIn("## summary", report_text)
            self.assertNotIn("Citation Audit", report_text)
            self.assertIn("## References", report_text)
            self.assertIn("## Citation Audit", evidence_text)


if __name__ == "__main__":
    unittest.main()
