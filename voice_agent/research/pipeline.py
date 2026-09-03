from __future__ import annotations

import re
from concurrent.futures import ThreadPoolExecutor, wait
from collections.abc import Callable
from dataclasses import replace
from typing import Protocol

from voice_agent.research.clients import ArxivClient, CrossrefClient, OpenAlexClient, SemanticScholarClient
from voice_agent.research.clients.dashscope import cosine_similarity
from voice_agent.research.full_text import FullTextFetcher
from voice_agent.research.models import (
    AcademicReport,
    CitationAudit,
    EvidenceChunk,
    Paper,
    Perspective,
    PerspectiveTurn,
    ResearchMode,
    SOTAClaim,
    StormRunTrace,
)


class PaperSearcher(Protocol):
    def search(self, query: str, limit: int = 10) -> list[Paper]:
        ...


Progress = Callable[[str], None]


class AcademicResearchPipeline:
    def __init__(
        self,
        searchers: list[PaperSearcher] | None = None,
        crossref: CrossrefClient | None = None,
        embedding_client=None,
        reranker=None,
        full_text_fetcher: FullTextFetcher | None = None,
        fetch_full_text: bool = True,
        max_full_text_papers: int = 6,
        max_search_queries: int = 8,
        search_timeout_seconds: float = 30.0,
        max_chunks_per_report: int = 48,
        chunk_chars: int = 1800,
        chunk_overlap: int = 240,
    ) -> None:
        self.searchers = searchers or [SemanticScholarClient(), OpenAlexClient(), ArxivClient()]
        self.crossref = crossref
        self.embedding_client = embedding_client
        self.reranker = reranker
        self.full_text_fetcher = full_text_fetcher
        self.fetch_full_text = fetch_full_text
        self.max_full_text_papers = max_full_text_papers
        self.max_search_queries = max_search_queries
        self.search_timeout_seconds = search_timeout_seconds
        self.max_chunks_per_report = max_chunks_per_report
        self.chunk_chars = chunk_chars
        self.chunk_overlap = chunk_overlap

    def run(self, query: str, mode: ResearchMode, limit: int = 24, progress: Progress | None = None) -> AcademicReport:
        progress = progress or (lambda _message: None)
        progress("正在扩展学术检索词。")
        search_query = _normalize_academic_query(query)
        perspectives = self._build_perspectives(search_query, mode)
        planned_turns = self._plan_perspective_turns(search_query, mode, perspectives)
        expanded_queries = _unique_preserve_order(
            self._expand_queries(search_query, mode)
            + [query for turn in planned_turns for query in turn.search_queries]
            + [perspective.query for perspective in perspectives]
        )[: self.max_search_queries]
        per_query_limit = max(3, min(10, limit // max(1, len(expanded_queries)) + 1))

        papers = self._search_all(expanded_queries, per_query_limit, progress)

        progress("正在去重和排序论文。")
        ranked = self._rank_papers(self._dedup(papers), search_query)
        ranked = self._filter_low_relevance(ranked, search_query)[:limit]
        ranked = self._enrich_missing_dois(ranked, progress)
        if mode == ResearchMode.SOTA:
            progress("正在整理 SOTA 候选。")
            claims = self._extract_sota_claims(query, ranked)
            markdown = self._write_sota_report(query, ranked, claims)
            return AcademicReport(mode=mode, query=query, markdown=markdown, papers=ranked, sota_claims=claims)

        progress("正在获取全文并构建证据块。")
        evidence_chunks = self._build_evidence_chunks(search_query, ranked, progress)
        progress("正在生成直出大纲并基于证据 refine。")
        citation_map = {paper.stable_key: f"P{index}" for index, paper in enumerate(ranked, start=1)}
        groups = self._group_papers(ranked)
        section_evidence = self._section_evidence(groups, evidence_chunks)
        direct_outline = self._build_direct_outline(query)
        refined_outline = self._refine_outline_with_evidence(query, direct_outline, groups, section_evidence, citation_map)
        completed_turns = self._complete_perspective_turns(planned_turns, ranked, evidence_chunks, citation_map)
        trace = StormRunTrace(
            direct_outline=direct_outline,
            refined_outline=refined_outline,
            perspective_turns=completed_turns,
            retrieval_query_count=len(expanded_queries),
            evidence_chunk_count=len(evidence_chunks),
            full_text_chunk_count=sum(1 for chunk in evidence_chunks if chunk.source_type == "full_text"),
        )
        progress("正在按 refined outline 分章节写作。")
        markdown = self._write_survey_report(query, ranked, perspectives, evidence_chunks, trace)
        return AcademicReport(mode=mode, query=query, markdown=markdown, papers=ranked, storm_trace=trace)

    def _build_perspectives(self, query: str, mode: ResearchMode) -> list[Perspective]:
        if mode == ResearchMode.SOTA:
            return [
                Perspective("Benchmark curator", "哪些数据集、指标和设置定义了 SOTA？", f"{query} benchmark dataset metric"),
                Perspective("Reproducibility reviewer", "哪些论文提供代码、模型或复现实验？", f"{query} code repository reproducibility"),
                Perspective("Recent-work tracker", "最近一年有哪些新方法声称刷新结果？", f"{query} recent state of the art"),
            ]
        return [
            Perspective("Field historian", "该领域的基础问题和早期脉络是什么？", f"{query} foundational survey taxonomy"),
            Perspective("System builder", "已有系统如何组织检索、规划、写作和验证？", f"{query} system framework pipeline"),
            Perspective("Evaluation critic", "现有工作如何评估覆盖、引用质量和可靠性？", f"{query} evaluation benchmark citation quality"),
            Perspective("Application researcher", "这些方法如何进入真实科研工作流？", f"{query} applications case study workflow"),
            Perspective("Recent-work tracker", "最近一到两年的新趋势是什么？", f"{query} recent advances 2025 2026"),
        ]

    def _expand_queries(self, query: str, mode: ResearchMode) -> list[str]:
        normalized = " ".join(query.split())
        if mode == ResearchMode.SOTA:
            return [
                normalized,
                f"{normalized} state of the art benchmark",
                f"{normalized} leaderboard dataset metric",
            ]
        return [
            normalized,
            f"{normalized} survey",
            f"{normalized} review recent advances",
        ] + _domain_specific_queries(normalized)

    def _plan_perspective_turns(
        self, query: str, mode: ResearchMode, perspectives: list[Perspective]
    ) -> list[PerspectiveTurn]:
        turns: list[PerspectiveTurn] = []
        for perspective in perspectives:
            follow_up = _follow_up_question(perspective, mode)
            queries = _unique_preserve_order(
                [
                    perspective.query,
                    _question_to_query(query, perspective.question),
                    _question_to_query(query, follow_up),
                ]
            )
            turns.append(
                PerspectiveTurn(
                    perspective_name=perspective.name,
                    role_description=perspective.question,
                    question=follow_up,
                    search_queries=queries,
                )
            )
        return turns

    def _search_all(self, queries: list[str], per_query_limit: int, progress: Progress) -> list[Paper]:
        papers: list[Paper] = []
        futures = []
        executor = ThreadPoolExecutor(max_workers=min(8, max(1, len(queries) * len(self.searchers))))
        try:
            for expanded_query in queries:
                for searcher in self.searchers:
                    progress(f"正在检索：{expanded_query}")
                    futures.append(executor.submit(searcher.search, expanded_query, per_query_limit))
            done, _not_done = wait(futures, timeout=self.search_timeout_seconds)
            for future in done:
                try:
                    papers.extend(future.result())
                except Exception:
                    continue
        finally:
            executor.shutdown(wait=False, cancel_futures=True)
        return papers

    def _enrich_missing_dois(self, papers: list[Paper], progress: Progress) -> list[Paper]:
        if self.crossref is None:
            return papers
        enriched: list[Paper] = []
        for paper in papers:
            if paper.doi:
                enriched.append(paper)
                continue
            try:
                doi = self.crossref.find_doi(paper.title)
            except Exception:
                doi = None
            if doi:
                progress(f"已补全 DOI：{paper.title[:40]}")
                enriched.append(replace(paper, doi=doi))
            else:
                enriched.append(paper)
        return enriched

    def _complete_perspective_turns(
        self,
        planned_turns: list[PerspectiveTurn],
        papers: list[Paper],
        evidence_chunks: list[EvidenceChunk],
        citation_map: dict[str, str],
    ) -> list[PerspectiveTurn]:
        completed: list[PerspectiveTurn] = []
        for turn in planned_turns:
            scored: list[tuple[float, Paper]] = []
            for paper in papers:
                text = f"{paper.title} {paper.abstract or ''}"
                score = max(_lexical_score(query, text) for query in turn.search_queries)
                scored.append((score, paper))
            top_papers = [paper for score, paper in sorted(scored, key=lambda item: item[0], reverse=True) if score > 0][:4]
            if not top_papers:
                top_papers = papers[:3]
            citations = [citation_map[paper.stable_key] for paper in top_papers if paper.stable_key in citation_map]
            chunks = [
                chunk
                for chunk in evidence_chunks
                if any(chunk.paper.stable_key == paper.stable_key for paper in top_papers)
            ][:3]
            completed.append(
                replace(
                    turn,
                    answer_summary=_perspective_answer_summary(turn, top_papers, chunks, citation_map),
                    evidence_citations=citations,
                )
            )
        return completed

    def _dedup(self, papers: list[Paper]) -> list[Paper]:
        seen: set[str] = set()
        unique: list[Paper] = []
        for paper in papers:
            keys = _paper_keys(paper)
            if seen.intersection(keys):
                continue
            seen.update(keys)
            unique.append(paper)
        return unique

    def _rank_papers(self, papers: list[Paper], query: str) -> list[Paper]:
        query_terms = _query_terms(query)
        core_terms = _core_query_terms(query_terms)

        def score(paper: Paper) -> tuple[int, int, int, int]:
            haystack = f"{paper.title} {paper.abstract or ''}".lower()
            overlap = sum(1 for term in query_terms if term and term in haystack)
            core_overlap = sum(1 for term in core_terms if term and term in haystack)
            phrase_bonus = sum(1 for phrase in _query_phrases(query) if phrase in haystack)
            domain_bonus = _domain_anchor_score(query, haystack)
            year = paper.year or 0
            citations = paper.citation_count or 0
            return (domain_bonus * 5 + core_overlap * 3 + phrase_bonus * 2 + overlap, core_overlap, year, citations)

        return sorted(papers, key=score, reverse=True)

    def _filter_low_relevance(self, papers: list[Paper], query: str) -> list[Paper]:
        core_terms = _core_query_terms(_query_terms(query))
        if not core_terms:
            return papers
        strong: list[Paper] = []
        for paper in papers:
            haystack = f"{paper.title} {paper.abstract or ''}".lower()
            core_overlap = sum(1 for term in core_terms if term and term in haystack)
            domain_score = _domain_anchor_score(query, haystack)
            if domain_score >= 2 or core_overlap >= 3:
                strong.append(paper)
        if "agent" in core_terms and len(strong) >= 5:
            return strong
        if len(strong) >= 8:
            return strong
        return papers

    def _extract_sota_claims(self, query: str, papers: list[Paper]) -> list[SOTAClaim]:
        claims: list[SOTAClaim] = []
        for paper in papers:
            text = f"{paper.title}. {paper.abstract or ''}"
            if not _looks_like_sota(text):
                continue
            method = paper.title.split(":")[0][:80]
            claims.append(
                SOTAClaim(
                    task=query,
                    dataset="unknown",
                    metric="unknown",
                    setting="reported by paper abstract/title",
                    method=method,
                    score="unknown",
                    paper_title=paper.title,
                    year=paper.year,
                    evidence_url=paper.url,
                    evidence_level="L1: paper self-claim",
                    notes="第一版仅从标题/摘要识别 SOTA 候选，后续阶段需要接论文表格抽取和榜单验证。",
                )
            )
        return claims[:10]

    def _build_evidence_chunks(self, query: str, papers: list[Paper], progress: Progress) -> list[EvidenceChunk]:
        chunks: list[EvidenceChunk] = []
        full_text_attempts = 0
        for paper in papers:
            text = None
            source_type = "abstract"
            if (
                self.fetch_full_text
                and self.full_text_fetcher is not None
                and paper.pdf_url
                and full_text_attempts < self.max_full_text_papers
            ):
                try:
                    full_text_attempts += 1
                    progress(f"正在解析全文：{paper.title[:40]}")
                    text = self.full_text_fetcher.fetch_text(paper)
                    if text:
                        source_type = "full_text"
                except Exception:
                    text = None
            if not text:
                text = paper.abstract or ""
                source_type = "abstract" if text else "metadata"
            if not text and paper.title:
                text = paper.title
            for index, chunk_text in enumerate(_chunk_text(text, self.chunk_chars, self.chunk_overlap)):
                chunks.append(EvidenceChunk(paper=paper, text=chunk_text, chunk_index=index, source_type=source_type))
        return self._rank_chunks(query, chunks)[: self.max_chunks_per_report]

    def _rank_chunks(self, query: str, chunks: list[EvidenceChunk]) -> list[EvidenceChunk]:
        if not chunks:
            return []
        docs = [_compact(chunk.text, 1800) for chunk in chunks]
        if self.reranker is not None:
            try:
                scored = self.reranker.rerank(query, docs, top_n=min(len(docs), self.max_chunks_per_report))
                by_index = {index: score for index, score in scored}
                ranked = [replace(chunk, relevance_score=by_index.get(index, 0.0)) for index, chunk in enumerate(chunks)]
                return _diversify_chunks(sorted(ranked, key=lambda chunk: chunk.relevance_score, reverse=True), max_per_paper=4)
            except Exception:
                pass
        if self.embedding_client is not None:
            try:
                vectors = self.embedding_client.embed([query] + docs)
                query_vector = vectors[0]
                ranked = [
                    replace(chunk, relevance_score=cosine_similarity(query_vector, vector))
                    for chunk, vector in zip(chunks, vectors[1:])
                ]
                return _diversify_chunks(sorted(ranked, key=lambda chunk: chunk.relevance_score, reverse=True), max_per_paper=4)
            except Exception:
                pass
        ranked = sorted(
            [replace(chunk, relevance_score=_lexical_score(query, chunk.text)) for chunk in chunks],
            key=lambda chunk: chunk.relevance_score,
            reverse=True,
        )
        return _diversify_chunks(ranked, max_per_paper=4)

    def _write_survey_report(
        self,
        query: str,
        papers: list[Paper],
        perspectives: list[Perspective],
        evidence_chunks: list[EvidenceChunk],
        storm_trace: StormRunTrace | None = None,
    ) -> str:
        groups = self._group_papers(papers)
        citation_map = {paper.stable_key: f"P{index}" for index, paper in enumerate(papers, start=1)}
        section_evidence = self._section_evidence(groups, evidence_chunks)
        citation_audit = self._citation_audit(papers, citation_map, evidence_chunks)
        lines = [
            f"# 研究综述：{query}",
            "",
            "## 摘要",
            "",
            self._write_abstract(query, papers, groups, citation_map),
            "",
            "## 调研范围与方法",
            "",
            f"本报告面向“{query}”进行自动化学术调研，流程对齐 STORM 的“预写作检索与大纲生成 -> 带引用长文写作”范式，以及 AutoSurvey 的“检索增强、分节写作、结构化评估”范式。"
            f"当前运行共保留 {len(papers)} 篇去重候选论文，正文中的 `[P#]` 均可在文末参考文献中追溯。"
            f"本轮构建了 {len(evidence_chunks)} 个 evidence chunks；若论文提供可访问 PDF，则优先使用全文，否则降级为摘要或元数据。",
            "",
            "## STORM-style 运行轨迹",
            "",
            *self._write_storm_trace(storm_trace),
            "",
            "## STORM-style 多视角问题",
            "",
            *self._write_perspectives(perspectives),
            "",
            "## STORM-style 多视角问答日志",
            "",
            *self._write_perspective_turns(storm_trace.perspective_turns if storm_trace else []),
            "",
            "## 关键结论",
            "",
            *self._write_key_takeaways(papers, groups, citation_map, section_evidence),
            "",
            "## 代表论文",
            "",
            "| 编号 | 年份 | 标题 | 来源 | 引用数 | 链接 |",
            "| --- | --- | --- | --- | --- | --- |",
        ]
        for index, paper in enumerate(papers[:20], start=1):
            citation_id = citation_map[paper.stable_key]
            lines.append(
                f"| [{citation_id}] | {paper.year or ''} | {paper.title} | {paper.source or ''} | "
                f"{paper.citation_count if paper.citation_count is not None else ''} | {paper.url or ''} |"
            )
        lines.extend(["", "## 建议综述大纲", ""])
        if storm_trace:
            lines.extend(["### Direct outline", ""])
            lines.extend(f"- {item}" for item in storm_trace.direct_outline)
            lines.extend(["", "### Evidence-refined outline", ""])
            lines.extend(f"- {item}" for item in storm_trace.refined_outline)
        else:
            lines.extend(self._build_outline(query, groups))
        lines.extend(["", "## 主题脉络", ""])
        lines.extend(self._write_research_trajectory(groups, citation_map))
        lines.extend(["", "## 方法与系统分类", ""])
        lines.extend(self._write_taxonomy_table(groups, citation_map))
        lines.extend(["", "## 正文综述", ""])
        lines.extend(self._write_body_sections(query, groups, citation_map, section_evidence))
        lines.extend(["", "## 综合对比", ""])
        lines.extend(self._write_comparison_table(groups, citation_map))
        lines.extend(["", "## 研究空白与未来方向", ""])
        lines.extend(self._write_future_directions(papers, groups, citation_map, evidence_chunks))
        lines.extend(["", "## Section Evidence Pack", ""])
        for label, group in groups.items():
            lines.append(f"### {label}")
            chunks = section_evidence.get(label, [])
            if not chunks:
                lines.append("- 暂无候选证据，后续需要追加检索。")
                lines.append("")
                continue
            for chunk in chunks[:6]:
                citation_id = citation_map[chunk.paper.stable_key]
                summary = _compact(chunk.text, 220)
                lines.append(
                    f"- [{citation_id}] `{chunk.source_type}` score={chunk.relevance_score:.3f}: {summary}"
                )
            lines.append("")
        lines.extend(["## Citation Audit", ""])
        lines.extend(self._write_citation_audit(citation_audit))
        lines.extend(["", "## OpenScholar-style 证据覆盖", ""])
        lines.extend(self._write_evidence_coverage(evidence_chunks, citation_map))
        lines.extend(["## 质量检查清单", ""])
        lines.extend(
            [
                f"- 覆盖性：当前综述依赖自动召回的 {len(papers)} 篇候选论文，仍需人工检查是否遗漏公认 seminal work。",
                "- 新近性：建议追加最近 6-12 个月限定检索，单独审阅 arXiv/OpenReview/顶会 accepted paper。",
                "- 引用可靠性：当前 `[P#]` 已连接到 evidence chunks；若 source_type 为 full_text，则比摘要级证据更可靠。",
                "- 结构一致性：大纲、正文和 evidence pack 已对齐；taxonomy 仍需要后续 LLM/embedding 聚类继续增强。",
                "- SOTA 可比性：如果综述涉及 benchmark，需要额外验证 dataset split、metric direction、训练数据和推理预算。",
            ]
        )
        lines.extend(["", "## 参考文献", ""])
        for paper in papers[:20]:
            citation_id = citation_map[paper.stable_key]
            authors = ", ".join(paper.authors[:3])
            if len(paper.authors) > 3:
                authors += " et al."
            prefix = f"- [{citation_id}] "
            meta = f"{authors}. " if authors else ""
            meta += f"{paper.title}. "
            if paper.venue:
                meta += f"{paper.venue}, "
            if paper.year:
                meta += f"{paper.year}. "
            if paper.url:
                meta += paper.url
            lines.append(prefix + meta.strip())
        return "\n".join(lines) + "\n"

    def _section_evidence(
        self, groups: dict[str, list[Paper]], evidence_chunks: list[EvidenceChunk]
    ) -> dict[str, list[EvidenceChunk]]:
        output: dict[str, list[EvidenceChunk]] = {}
        for label, papers in groups.items():
            if not papers:
                output[label] = []
                continue
            paper_keys = {paper.stable_key for paper in papers}
            label_terms = label.lower()
            chunks = [chunk for chunk in evidence_chunks if chunk.paper.stable_key in paper_keys]
            if len(chunks) < 3:
                chunks = sorted(
                    evidence_chunks,
                    key=lambda chunk: chunk.relevance_score + _lexical_score(label_terms, chunk.text) * 0.05,
                    reverse=True,
                )[:6]
            output[label] = _diversify_chunks(chunks, max_per_paper=2)[:8]
        return output

    def _citation_audit(
        self, papers: list[Paper], citation_map: dict[str, str], evidence_chunks: list[EvidenceChunk]
    ) -> list[CitationAudit]:
        chunk_count: dict[str, int] = {}
        for chunk in evidence_chunks:
            chunk_count[chunk.paper.stable_key] = chunk_count.get(chunk.paper.stable_key, 0) + 1
        audits = []
        for paper in papers[:20]:
            count = chunk_count.get(paper.stable_key, 0)
            status = "full_text_grounded" if count and any(
                chunk.paper.stable_key == paper.stable_key and chunk.source_type == "full_text" for chunk in evidence_chunks
            ) else "abstract_grounded" if count else "metadata_only"
            audits.append(
                CitationAudit(
                    citation_id=citation_map[paper.stable_key],
                    paper_title=paper.title,
                    has_url=bool(paper.url),
                    has_abstract_or_full_text=bool(paper.abstract or count),
                    evidence_chunks=count,
                    status=status,
                )
            )
        return audits

    def _write_perspectives(self, perspectives: list[Perspective]) -> list[str]:
        return [f"- **{item.name}**：{item.question} 检索式：`{item.query}`" for item in perspectives]

    def _write_abstract(self, query: str, papers: list[Paper], groups: dict[str, list[Paper]], citation_map: dict[str, str]) -> str:
        if not papers:
            return f"围绕“{query}”未检索到足够候选论文，因此无法形成可靠综述。"
        active_groups = [label for label, group in groups.items() if group]
        return (
            f"围绕“{query}”，本报告从 {len(papers)} 篇候选论文中梳理研究脉络。"
            f"现有材料主要覆盖 {('、'.join(active_groups)) or '若干相关方向'}。"
            f"高优先级阅读对象包括 { _cite_many(papers[:5], citation_map) }。"
            "整体来看，较好的科研调研系统通常不是单次生成，而是将问题界定、广域检索、主题组织、证据压缩、分节写作和引用核查拆成流水线。"
        )

    def _write_key_takeaways(
        self,
        papers: list[Paper],
        groups: dict[str, list[Paper]],
        citation_map: dict[str, str],
        section_evidence: dict[str, list[EvidenceChunk]],
    ) -> list[str]:
        if not papers:
            return ["- 未形成可靠结论。"]
        takeaways = [
            f"- 候选文献显示，该方向需要同时关注系统架构、检索 grounding、评估基准和应用约束，而不是只比较单个模型 { _cite_many(papers[:3], citation_map) }。",
            "- 综述写作应先产出可审阅的大纲和 evidence pack，再进入正文生成；这比一次性长文生成更容易控制覆盖面和引用质量。",
        ]
        for label, group in groups.items():
            if group:
                full_text_count = sum(1 for chunk in section_evidence.get(label, []) if chunk.source_type == "full_text")
                source_note = f"，其中 {full_text_count} 个全文证据块" if full_text_count else "，当前主要是摘要级证据"
                takeaways.append(f"- `{label}` 当前以 { _cite_many(group[:3], citation_map) } 为主要证据入口{source_note}。")
        return takeaways

    def _write_research_trajectory(self, groups: dict[str, list[Paper]], citation_map: dict[str, str]) -> list[str]:
        dated = sorted(
            [paper for group in groups.values() for paper in group if paper.year],
            key=lambda paper: paper.year or 0,
        )
        if not dated:
            return ["当前候选论文缺少年份信息，暂时无法生成清晰时间线。"]
        early = dated[: min(3, len(dated))]
        recent = dated[-min(5, len(dated)) :]
        return [
            f"从时间线上看，较早工作可作为问题定义和基础方法入口，例如 { _cite_many(early, citation_map) }。",
            f"近年的论文更集中在系统化、自动化和评估问题上，例如 { _cite_many(list(reversed(recent)), citation_map) }。",
            "因此，组会展示时可以把该领域讲成三段：早期基础方法形成、LLM/agent 系统化带来工作流自动化、近期重点转向可验证引用和 benchmark 化评估。",
        ]

    def _write_taxonomy_table(self, groups: dict[str, list[Paper]], citation_map: dict[str, str]) -> list[str]:
        lines = [
            "| 类别 | 关注问题 | 代表论文 | 当前证据强度 |",
            "| --- | --- | --- | --- |",
        ]
        descriptions = {
            "基础方法与模型": "核心模型、算法思想、任务定义和理论基础",
            "系统与工具": "agent 编排、检索工具、pipeline、交互式工作台",
            "评估与 Benchmark": "数据集、指标、leaderboard、实验协议和可比性",
            "应用与案例": "具体学科、行业或用户工作流中的落地方式",
        }
        for label, group in groups.items():
            strength = "中" if len(group) >= 3 else "低"
            if group and any((paper.citation_count or 0) > 100 for paper in group):
                strength = "较高"
            lines.append(
                f"| {label} | {descriptions.get(label, '相关研究分支')} | { _cite_many(group[:4], citation_map) or '待补充' } | {strength} |"
            )
        return lines

    def _write_body_sections(
        self,
        query: str,
        groups: dict[str, list[Paper]],
        citation_map: dict[str, str],
        section_evidence: dict[str, list[EvidenceChunk]],
    ) -> list[str]:
        lines: list[str] = []
        section_titles = {
            "基础方法与模型": "1. 问题定义与基础方法",
            "系统与工具": "2. Agent 系统与调研流水线",
            "评估与 Benchmark": "3. 评估体系与 SOTA 追踪",
            "应用与案例": "4. 应用场景与工作流融合",
        }
        for label, title in section_titles.items():
            group = groups.get(label, [])
            lines.extend([f"### {title}", ""])
            if not group:
                lines.extend(["当前检索结果中该方向证据不足，需要追加定向检索。", ""])
                continue
            cited = _cite_many(group[:4], citation_map)
            first = group[0]
            evidence = section_evidence.get(label, [])
            chunk_sentence = ""
            if evidence:
                top_chunk = evidence[0]
                chunk_sentence = (
                    f"本节最相关证据来自 [{citation_map[top_chunk.paper.stable_key]}] 的 `{top_chunk.source_type}` chunk，"
                    f"其内容摘要为：{_compact(top_chunk.text, 140)}"
                )
            lines.append(
                f"围绕“{query}”，`{label}` 方向的候选论文说明该主题已经形成可归纳的子问题。"
                f"代表性材料包括 {cited}。"
                f"其中，{first.title} 提供了一个优先阅读入口；其摘要显示，该方向关注的是"
                f"{_compact(first.abstract or '论文元数据所描述的核心问题', 120)}。"
                f"{chunk_sentence}"
            )
            if len(group) > 1:
                lines.append(
                    f"从多篇论文的题名和摘要看，这一类工作需要进一步区分“概念性综述”“系统实现”和“实验评估”三种证据。"
                    f"后续写正式综述时，应把 { _cite_many(group[1:4], citation_map) } 的贡献点拆成独立 claim，并为每个 claim 绑定原文段落。"
                )
            lines.append("")
        lines.extend(["### 5. 综合讨论", ""])
        lines.append(
            "与普通搜索报告相比，高质量科研综述的关键不是列出更多论文，而是把论文组织成可审查的论证结构："
            "先说明研究问题，再按方法谱系和系统组件分层，最后回到 benchmark、局限和未来方向。"
            "当前实现已经把候选论文、分类、大纲、正文、evidence chunks 和参考文献对齐到同一组 `[P#]` 证据编号；下一步应加入更强的 LLM 分节写作和 claim-level 判断。"
        )
        return lines

    def _write_comparison_table(self, groups: dict[str, list[Paper]], citation_map: dict[str, str]) -> list[str]:
        lines = [
            "| 维度 | 当前观察 | 支撑文献 | 后续需要补强 |",
            "| --- | --- | --- | --- |",
        ]
        rows = [
            ("覆盖面", "是否覆盖基础、高被引和近期工作", groups.get("基础方法与模型", []), "引入 citation graph 和最近一年时间过滤"),
            ("系统性", "是否能归纳 agent/pipeline/tool 的结构", groups.get("系统与工具", []), "抽取系统组件和数据流图"),
            ("评估性", "是否有 benchmark、dataset、metric 或 leaderboard", groups.get("评估与 Benchmark", []), "接入 SOTA 表格抽取和可比性判断"),
            ("落地性", "是否说明真实研究工作流中的使用方式", groups.get("应用与案例", []), "补充 case study 和用户交互流程"),
        ]
        for dimension, observation, group, next_step in rows:
            lines.append(f"| {dimension} | {observation} | { _cite_many(group[:3], citation_map) or '待补充' } | {next_step} |")
        return lines

    def _write_future_directions(
        self,
        papers: list[Paper],
        groups: dict[str, list[Paper]],
        citation_map: dict[str, str],
        evidence_chunks: list[EvidenceChunk],
    ) -> list[str]:
        recent = [paper for paper in papers if paper.year and paper.year >= 2024]
        full_text_chunks = [chunk for chunk in evidence_chunks if chunk.source_type == "full_text"]
        lines = [
            f"- **全文证据化**：本轮已构建 {len(evidence_chunks)} 个 evidence chunks，其中全文 chunk 为 {len(full_text_chunks)} 个；后续应继续提高 PDF 覆盖率。",
            f"- **多视角规划**：参考 STORM，需要加入 perspective-guided question asking，用不同专家视角主动发现遗漏主题。",
            f"- **分节写作与修订**：参考 AutoSurvey，需要按 section 独立召回和写作，再做跨章节一致性修订。",
            f"- **新近论文覆盖**：当前候选集中 2024 年以后论文有 {len(recent)} 篇，后续应为近期进展单独建立章节 { _cite_many(recent[:4], citation_map) }。",
            "- **SOTA 表格化**：涉及 benchmark 时，应输出 task/dataset/metric/setting，而不是只在正文中描述“性能更好”。",
        ]
        return lines

    def _write_citation_audit(self, audits: list[CitationAudit]) -> list[str]:
        lines = [
            "| 引用 | 标题 | URL | 证据块 | 状态 |",
            "| --- | --- | --- | --- | --- |",
        ]
        for audit in audits:
            lines.append(
                f"| [{audit.citation_id}] | {audit.paper_title} | {'yes' if audit.has_url else 'no'} | "
                f"{audit.evidence_chunks} | {audit.status} |"
            )
        return lines

    def _write_storm_trace(self, trace: StormRunTrace | None) -> list[str]:
        if trace is None:
            return ["- 未记录 STORM-style 运行轨迹。"]
        return [
            f"- 多视角角色数：{len(trace.perspective_turns)}。",
            f"- 学术检索查询数：{trace.retrieval_query_count}。",
            f"- evidence chunks：{trace.evidence_chunk_count}，其中全文 chunks：{trace.full_text_chunk_count}。",
            "- 流程：direct outline -> perspective-guided scholarly retrieval -> evidence-refined outline -> section-level evidence packing -> section-by-section writing -> citation audit。",
        ]

    def _write_perspective_turns(self, turns: list[PerspectiveTurn]) -> list[str]:
        if not turns:
            return ["- 暂无多视角问答日志。"]
        lines: list[str] = []
        for turn in turns:
            lines.extend(
                [
                    f"### {turn.perspective_name}",
                    "",
                    f"- 角色关注：{turn.role_description}",
                    f"- 追问：{turn.question}",
                    f"- 检索式：{'; '.join(f'`{query}`' for query in turn.search_queries)}",
                    f"- 证据引用：{', '.join(f'[{citation}]' for citation in turn.evidence_citations) or '待补充'}",
                    f"- 回答摘要：{turn.answer_summary or '暂无可靠证据。'}",
                    "",
                ]
            )
        return lines

    def _write_evidence_coverage(self, chunks: list[EvidenceChunk], citation_map: dict[str, str]) -> list[str]:
        if not chunks:
            return ["- 尚未构建证据块，报告退化为论文元数据综述。"]
        full_text_count = sum(1 for chunk in chunks if chunk.source_type == "full_text")
        abstract_count = sum(1 for chunk in chunks if chunk.source_type == "abstract")
        lines = [
            f"- 证据块总数：{len(chunks)}。",
            f"- 全文证据块：{full_text_count}；摘要证据块：{abstract_count}。",
            "- Top evidence chunks：",
        ]
        for chunk in chunks[:8]:
            citation_id = citation_map.get(chunk.paper.stable_key, "?")
            lines.append(
                f"  - [{citation_id}] `{chunk.source_type}` score={chunk.relevance_score:.3f}: {_compact(chunk.text, 180)}"
            )
        return lines

    def _write_sota_report(self, query: str, papers: list[Paper], claims: list[SOTAClaim]) -> str:
        lines = [
            f"# SOTA 调研草稿：{query}",
            "",
            "## 生成说明",
            "",
            "这是 Tyro Duplex 科研调研 MVP 自动生成的 SOTA 候选图谱。当前版本只做论文级候选召回和标题/摘要识别，尚未做结果表抽取或本地复现。",
            "",
            "## SOTA 候选",
            "",
            "| # | 年份 | 方法/论文 | 数据集 | 指标 | 分数 | 证据等级 | 链接 |",
            "| --- | --- | --- | --- | --- | --- | --- | --- |",
        ]
        if claims:
            for index, claim in enumerate(claims, start=1):
                lines.append(
                    f"| {index} | {claim.year or ''} | {claim.paper_title} | {claim.dataset} | "
                    f"{claim.metric} | {claim.score} | {claim.evidence_level} | {claim.evidence_url or ''} |"
                )
        else:
            lines.append("| - | - | 未从标题/摘要识别到明确 SOTA 候选 | - | - | - | - | - |")
        lines.extend(["", "## 候选论文池", ""])
        for paper in papers[:20]:
            lines.append(f"- {paper.title} ({paper.year or 'unknown'}), {paper.source or 'unknown'}: {paper.url or ''}")
        lines.extend(["", "## 后续验证清单", ""])
        lines.extend(
            [
                "- 补充 benchmark/leaderboard 来源，区分论文自报与第三方榜单。",
                "- 抽取论文结果表，标准化 task/dataset/metric/setting。",
                "- 判断不同设置是否可比，例如数据 split、训练数据、模型规模和推理预算。",
                "- 对关键 SOTA 候选追加代码链接和复现实验状态。",
            ]
        )
        return "\n".join(lines) + "\n"

    def _build_direct_outline(self, query: str) -> list[str]:
        return [
            f"引言：{query} 的研究问题、应用背景和综述范围",
            "背景：关键概念、技术前提和相关研究传统",
            "方法分类：按模型、检索、agent 编排和验证方式组织已有工作",
            "代表系统：梳理可复现系统、开源工具和端到端 pipeline",
            "评估与 SOTA：总结 benchmark、指标、数据集和可比性风险",
            "应用与工作流：讨论真实科研场景中的使用方式",
            "局限与未来方向：覆盖可信度、引用质量、全文证据和人工审核",
        ]

    def _refine_outline_with_evidence(
        self,
        query: str,
        direct_outline: list[str],
        groups: dict[str, list[Paper]],
        section_evidence: dict[str, list[EvidenceChunk]],
        citation_map: dict[str, str],
    ) -> list[str]:
        refined = [direct_outline[0]]
        if groups.get("基础方法与模型"):
            refined.append(
                "背景与研究脉络：从基础论文和近期综述中界定问题 "
                f"{_cite_many(groups['基础方法与模型'][:3], citation_map)}"
            )
        if groups.get("系统与工具"):
            refined.append(
                "系统架构与 agent workflow：比较检索、规划、工具调用、写作和验证模块 "
                f"{_cite_many(groups['系统与工具'][:4], citation_map)}"
            )
        if groups.get("评估与 Benchmark"):
            refined.append(
                "评估协议与 SOTA 追踪：整理数据集、指标、人工偏好评测和 leaderboard 风险 "
                f"{_cite_many(groups['评估与 Benchmark'][:4], citation_map)}"
            )
        if groups.get("应用与案例"):
            refined.append(
                "应用与人机协同：分析学科场景、交互式工作台和 human-in-the-loop 审核 "
                f"{_cite_many(groups['应用与案例'][:4], citation_map)}"
            )
        sparse_labels = [label for label, chunks in section_evidence.items() if len(chunks) < 2]
        if sparse_labels:
            refined.append(f"证据缺口：{', '.join(sparse_labels)} 仍需追加定向检索和全文获取")
        refined.append(f"局限与未来方向：围绕全文 grounding、claim-level citation audit 和可复现 SOTA 表格展开")
        return [item for item in refined if item.strip()]

    def _build_outline(self, query: str, groups: dict[str, list[Paper]]) -> list[str]:
        outline = [f"1. 引言：{query} 的问题定义、应用背景和研究动机"]
        index = 2
        for label, group in groups.items():
            if not group:
                continue
            representative = group[0].title
            outline.append(f"{index}. {label}：以 {representative} 等论文为起点组织讨论")
            index += 1
        outline.extend(
            [
                f"{index}. 评估协议与 SOTA：整理主流数据集、指标和可比性风险",
                f"{index + 1}. 局限与未来方向：总结未解决问题和后续研究机会",
            ]
        )
        return outline

    def _group_papers(self, papers: list[Paper]) -> dict[str, list[Paper]]:
        groups = {
            "基础方法与模型": [],
            "系统与工具": [],
            "评估与 Benchmark": [],
            "应用与案例": [],
        }
        for paper in papers:
            text = f"{paper.title} {paper.abstract or ''}".lower()
            if any(term in text for term in ("benchmark", "evaluation", "leaderboard", "dataset")):
                groups["评估与 Benchmark"].append(paper)
            elif any(term in text for term in ("system", "tool", "agent", "framework", "pipeline")):
                groups["系统与工具"].append(paper)
            elif any(term in text for term in ("application", "case study", "deploy", "clinical", "industry")):
                groups["应用与案例"].append(paper)
            else:
                groups["基础方法与模型"].append(paper)
        return groups


def infer_research_mode(query: str) -> ResearchMode:
    lowered = query.lower()
    if any(keyword in lowered for keyword in ("sota", "state of the art", "benchmark", "leaderboard", "最先进", "榜单")):
        return ResearchMode.SOTA
    return ResearchMode.SURVEY


def _normalize_academic_query(query: str) -> str:
    lowered = " ".join(query.lower().split())
    replacements = {
        "科研 agent": "scientific research agent",
        "科研agent": "scientific research agent",
        "研究 agent": "research agent",
        "研究agent": "research agent",
        "文献综述": "literature review",
        "综述论文": "survey paper",
        "综述": "survey",
        "文献": "literature",
        "论文": "paper",
        "前沿": "frontier",
        "顶会": "top conference",
        "最先进": "state of the art",
        "榜单": "leaderboard",
    }
    for source, target in replacements.items():
        lowered = lowered.replace(source, f" {target} ")
    stopwords = (
        "帮我",
        "请",
        "调研",
        "研究下",
        "查一下",
        "找一下",
        "整理",
        "一份",
        "一下",
        "相关",
        "的",
    )
    for stopword in stopwords:
        lowered = lowered.replace(stopword, " ")
    normalized = " ".join(lowered.split())
    return normalized or query


def _query_terms(query: str) -> set[str]:
    return {term.lower() for term in re.findall(r"[A-Za-z0-9_\\-]+|[\u4e00-\u9fff]+", query)}


def _core_query_terms(query_terms: set[str]) -> set[str]:
    generic = {
        "survey",
        "paper",
        "papers",
        "literature",
        "review",
        "recent",
        "advances",
        "state",
        "of",
        "the",
        "art",
        "benchmark",
        "leaderboard",
        "scientific",
        "research",
    }
    return {term for term in query_terms if term not in generic and len(term) > 2}


def _query_phrases(query: str) -> list[str]:
    normalized = " ".join(query.lower().split())
    phrases = []
    for phrase in (
        "large language model",
        "scientific research agent",
        "research agent",
        "autonomous agent",
        "literature review",
        "survey paper",
        "state of the art",
    ):
        if phrase in normalized:
            phrases.append(phrase)
    return phrases


def _domain_anchor_score(query: str, haystack: str) -> int:
    query_lower = query.lower()
    score = 0
    if any(anchor in query_lower for anchor in ("literature review", "survey", "scientific review")):
        if any(anchor in haystack for anchor in ("literature review", "systematic review", "survey", "scientific review")):
            score += 1
    if any(anchor in query_lower for anchor in ("large language model", "llm", "agent", "rag", "retrieval")):
        if any(anchor in haystack for anchor in ("large language model", "llm", "agent", "retrieval", "rag", "augmented generation")):
            score += 1
    if any(anchor in query_lower for anchor in ("automated", "automation", "generation")):
        if any(anchor in haystack for anchor in ("automated", "automation", "generation", "generate")):
            score += 1
    return score


def _domain_specific_queries(query: str) -> list[str]:
    if "agent" not in query.lower():
        return []
    return [
        "large language model based autonomous agents survey",
        "LLM agents literature review survey",
        "AI research agent literature review system",
        "scientific literature review agent retrieval augmented generation",
    ]


def _follow_up_question(perspective: Perspective, mode: ResearchMode) -> str:
    if mode == ResearchMode.SOTA:
        questions = {
            "Benchmark curator": "哪些论文明确报告 task/dataset/metric/setting，并声称达到或刷新 SOTA？",
            "Reproducibility reviewer": "哪些结果有代码、模型、数据或第三方复现证据支撑？",
            "Recent-work tracker": "最近一到两年有哪些新论文可能改变当前 SOTA 判断？",
        }
    else:
        questions = {
            "Field historian": "这个方向的代表性早期工作、综述和问题定义是什么？",
            "System builder": "这些系统分别如何组织检索、规划、工具调用、写作和引用验证？",
            "Evaluation critic": "现有工作怎样评估覆盖率、事实性、引用质量和人工偏好？",
            "Application researcher": "这些方法在哪些科研工作流中落地，用户如何介入和校正？",
            "Recent-work tracker": "2024 年以后有哪些新系统、benchmark 或评测协议值得单独成节？",
        }
    return questions.get(perspective.name, perspective.question)


def _question_to_query(query: str, question: str) -> str:
    terms = []
    lowered = question.lower()
    mappings = (
        ("早期", "foundational seminal"),
        ("综述", "survey review"),
        ("系统", "system framework architecture"),
        ("检索", "retrieval augmented generation"),
        ("工具", "tool use agent"),
        ("引用", "citation grounding verification"),
        ("评估", "evaluation benchmark metric"),
        ("覆盖", "coverage recall"),
        ("人工", "human expert preference"),
        ("工作流", "workflow human in the loop"),
        ("落地", "application case study"),
        ("2024", "2024 2025 2026 recent"),
        ("sota", "state of the art leaderboard"),
        ("数据集", "dataset benchmark"),
        ("指标", "metric score"),
        ("代码", "code repository reproducibility"),
    )
    for keyword, expansion in mappings:
        if keyword in lowered or keyword in question:
            terms.append(expansion)
    if not terms:
        terms.append(question)
    return " ".join([query] + terms)


def _perspective_answer_summary(
    turn: PerspectiveTurn,
    papers: list[Paper],
    chunks: list[EvidenceChunk],
    citation_map: dict[str, str],
) -> str:
    if not papers:
        return "未召回足够论文，无法回答该视角问题。"
    citations = _cite_many(papers[:4], citation_map)
    leading = papers[0]
    evidence_note = ""
    if chunks:
        best = chunks[0]
        evidence_note = (
            f" 最相关证据块来自 [{citation_map.get(best.paper.stable_key, '?')}] 的"
            f" `{best.source_type}`，内容指向：{_compact(best.text, 160)}"
        )
    return (
        f"该视角的候选证据主要来自 {citations}。"
        f"优先入口是《{leading.title}》，其元数据/摘要显示该视角与"
        f"{_compact(leading.abstract or leading.title, 140)}相关。"
        f"{evidence_note}"
    )


def _looks_like_sota(text: str) -> bool:
    lowered = text.lower()
    return any(
        keyword in lowered
        for keyword in (
            "state-of-the-art",
            "state of the art",
            "sota",
            "outperform",
            "surpass",
            "benchmark",
            "leaderboard",
            "achieves",
            "达到最先进",
            "最先进",
        )
    )


def _compact(text: str, max_length: int) -> str:
    normalized = " ".join(text.split())
    if len(normalized) <= max_length:
        return normalized
    return normalized[: max_length - 3] + "..."


def _cite_many(papers: list[Paper], citation_map: dict[str, str]) -> str:
    citations = []
    for paper in papers:
        citation = citation_map.get(paper.stable_key)
        if citation:
            citations.append(f"[{citation}]")
    return "、".join(citations)


def _paper_keys(paper: Paper) -> set[str]:
    keys = {paper.stable_key}
    title_key = _normalize_title_key(paper.title)
    if title_key:
        keys.add(f"title:{title_key}")
    return keys


def _normalize_title_key(title: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", title.lower()).strip()


def _chunk_text(text: str, chunk_chars: int, overlap: int) -> list[str]:
    normalized = "\n".join(line.strip() for line in text.splitlines() if line.strip())
    if not normalized:
        return []
    if len(normalized) <= chunk_chars:
        return [normalized]
    chunks: list[str] = []
    start = 0
    step = max(1, chunk_chars - overlap)
    while start < len(normalized):
        chunk = normalized[start : start + chunk_chars].strip()
        if chunk:
            chunks.append(chunk)
        start += step
    return chunks


def _lexical_score(query: str, text: str) -> float:
    terms = _query_terms(query)
    if not terms:
        return 0.0
    haystack = text.lower()
    hits = sum(1 for term in terms if term in haystack)
    return hits / len(terms)


def _diversify_chunks(chunks: list[EvidenceChunk], max_per_paper: int) -> list[EvidenceChunk]:
    counts: dict[str, int] = {}
    selected: list[EvidenceChunk] = []
    for chunk in chunks:
        key = chunk.paper.stable_key
        if counts.get(key, 0) < max_per_paper:
            selected.append(chunk)
            counts[key] = counts.get(key, 0) + 1
    return selected


def _unique_preserve_order(values: list[str]) -> list[str]:
    seen: set[str] = set()
    output: list[str] = []
    for value in values:
        normalized = " ".join(str(value).split())
        key = normalized.lower()
        if not normalized or key in seen:
            continue
        seen.add(key)
        output.append(normalized)
    return output
