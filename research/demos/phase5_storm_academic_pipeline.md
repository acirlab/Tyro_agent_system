# Phase 5 Demo: STORM-style Academic Pipeline

## Goal

Apply STORM's workflow shape inside Tyro Duplex:

1. Multi-perspective question asking
2. Scholarly retrieval
3. Direct outline generation
4. Evidence-refined outline
5. Section-level evidence packing
6. Section-by-section writing
7. Citation audit

The retriever/evidence layer is Tyro-native rather than STORM's default web search:

- Semantic Scholar
- OpenAlex
- arXiv
- Crossref DOI enrichment
- Full-text PDF extraction
- DashScope `text-embedding-v4`
- DashScope `qwen3-rerank`
- DashScope `qwen3.7-plus` writer

## Code Entry Points

- Pipeline: `/home/acir/Tyro_duplex/voice_agent/research/pipeline.py`
- Trace models: `/home/acir/Tyro_duplex/voice_agent/research/models.py`
- Tool writer: `/home/acir/Tyro_duplex/voice_agent/tools/builtin/academic_research.py`
- Runtime wiring: `/home/acir/Tyro_duplex/voice_agent/bootstrap.py`

## Demo Query

```text
Automated scientific literature review generation using large language model agents
```

## Demo Output

- `/home/acir/Tyro_duplex/research/tyro_storm_academic_pipeline_demo.md`
- Clean STORM-style article: `/home/acir/Tyro_duplex/research/tyro_storm_clean_article_demo.md`
- Evidence/debug report: `/home/acir/Tyro_duplex/research/tyro_storm_clean_article_evidence_report.md`
- Raw run: `/home/acir/Tyro_duplex/research/runs/20260827_183241_storm_ac_automated_scientific_literature_review_generatio/report.md`

## Metrics

Tyro Duplex STORM-style academic backend:

- Candidate papers: 14
- Unique citation markers: 14
- Report length: 3,270 words
- Evidence chunks: 32
- Full-text chunks: 24
- Perspective roles: 5
- Scholarly retrieval queries: 10

Prior open-source STORM run with DuckDuckGo:

- Candidate/reference sources: 26
- Report length: 2,398 words
- Unique citation markers: 26
- Retrieval queries: 16

## Observed Quality

The Tyro version now matches the STORM workflow shape and produces a longer, more evidence-heavy report than the direct STORM web-search demo. The most important improvement is evidence quality: sources come from scholarly APIs and full-text PDF chunks instead of generic web pages.

Remaining gap: the writer is still one final synthesis call over a structured evidence report. The next upgrade should make writing fully section-isolated: each refined outline section gets its own evidence pack, writer call, citation verifier, and revision pass.

## Clean Final Report Update

The user-facing `report.md` now follows STORM's final article style. It only contains:

- summary
- Background
- System Architecture
- Technological Approaches
- Notable Systems and Implementations
- Applications
- Evaluation and Benchmarking
- Challenges and Limitations
- Ethical and Legal Considerations
- Future Directions
- References

Intermediate materials such as perspective logs, direct/refined outlines, section evidence packs, citation audit, and quality checklists are saved separately as `evidence_report.md` in the same run directory.
