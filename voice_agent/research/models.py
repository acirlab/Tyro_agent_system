from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class ResearchMode(str, Enum):
    SURVEY = "academic_survey"
    SOTA = "sota_finder"


@dataclass(frozen=True)
class Paper:
    title: str
    authors: list[str] = field(default_factory=list)
    year: int | None = None
    venue: str | None = None
    abstract: str | None = None
    url: str | None = None
    pdf_url: str | None = None
    doi: str | None = None
    citation_count: int | None = None
    source: str | None = None
    code_urls: list[str] = field(default_factory=list)

    @property
    def stable_key(self) -> str:
        if self.doi:
            return f"doi:{self.doi.lower()}"
        return "title:" + " ".join(self.title.lower().split())


@dataclass(frozen=True)
class Evidence:
    paper_title: str
    source_url: str | None
    summary: str
    relevance_score: float


@dataclass(frozen=True)
class EvidenceChunk:
    paper: Paper
    text: str
    chunk_index: int
    source_type: str
    relevance_score: float = 0.0

    @property
    def label(self) -> str:
        return f"{self.paper.title}#chunk-{self.chunk_index}"


@dataclass(frozen=True)
class Perspective:
    name: str
    question: str
    query: str


@dataclass(frozen=True)
class PerspectiveTurn:
    perspective_name: str
    role_description: str
    question: str
    search_queries: list[str]
    answer_summary: str = ""
    evidence_citations: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class StormRunTrace:
    direct_outline: list[str]
    refined_outline: list[str]
    perspective_turns: list[PerspectiveTurn]
    retrieval_query_count: int
    evidence_chunk_count: int
    full_text_chunk_count: int


@dataclass(frozen=True)
class CitationAudit:
    citation_id: str
    paper_title: str
    has_url: bool
    has_abstract_or_full_text: bool
    evidence_chunks: int
    status: str


@dataclass(frozen=True)
class SOTAClaim:
    task: str
    dataset: str
    metric: str
    setting: str
    method: str
    score: str
    paper_title: str
    year: int | None
    evidence_url: str | None
    evidence_level: str
    comparable: str = "uncertain"
    notes: str = ""


@dataclass(frozen=True)
class AcademicReport:
    mode: ResearchMode
    query: str
    markdown: str
    papers: list[Paper]
    sota_claims: list[SOTAClaim] = field(default_factory=list)
    storm_trace: StormRunTrace | None = None
    output_path: str | None = None
