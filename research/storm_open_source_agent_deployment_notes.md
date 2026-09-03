# STORM Open-Source Agent Deployment Notes

## What was deployed

- Open-source agent: STORM from `stanford-oval/storm`
- Local path: `/home/acir/Tyro_duplex/research/open_agents/storm`
- Runner: `/home/acir/Tyro_duplex/research/open_agents/storm/run_storm_dashscope.py`
- LLM provider: Alibaba Cloud DashScope through the OpenAI-compatible endpoint
- Fast model: `qwen-plus-latest`
- Strong model: `qwen3.7-plus`
- Embedding: local `SentenceTransformer` compatibility layer backed by DashScope `text-embedding-v4`
- Retriever: STORM `DuckDuckGoSearchRM`

## Command

```bash
cd /home/acir/Tyro_duplex/research/open_agents/storm
HTTP_PROXY=${HTTP_PROXY/socks:\/\//socks5://} \
HTTPS_PROXY=${HTTPS_PROXY/socks:\/\//socks5://} \
ALL_PROXY=${ALL_PROXY/socks:\/\//socks5://} \
http_proxy=${http_proxy/socks:\/\//socks5://} \
https_proxy=${https_proxy/socks:\/\//socks5://} \
all_proxy=${all_proxy/socks:\/\//socks5://} \
STORM_STRONG_MODEL=qwen3.7-plus \
STORM_FAST_MODEL=qwen-plus-latest \
.venv/bin/python run_storm_dashscope.py \
  --topic "Automated scientific literature review generation using large language model agents" \
  --output-dir /home/acir/Tyro_duplex/research/open_agent_outputs/storm_dashscope \
  --max-conv-turn 2 \
  --max-perspective 3 \
  --max-search-queries-per-turn 2 \
  --search-top-k 3 \
  --retrieve-top-k 4 \
  --max-thread-num 2
```

## Outputs

- Review only: `/home/acir/Tyro_duplex/research/storm_open_source_agent_sample_review.md`
- Outline: `/home/acir/Tyro_duplex/research/storm_open_source_agent_sample_outline.md`
- Review with references: `/home/acir/Tyro_duplex/research/storm_open_source_agent_sample_review_with_references.md`
- Raw STORM outputs: `/home/acir/Tyro_duplex/research/open_agent_outputs/storm_dashscope/Automated_scientific_literature_review_generation_using_large_language_model_agents/`

## Run Metrics

- Knowledge curation: 139.43 seconds
- Outline generation: 103.32 seconds
- Article generation: 268.34 seconds
- Article polish: 43.65 seconds
- Retrieval queries: 16
- Polished article length: 2,398 words
- Unique citation markers: 26
- Reference entries: 26
- Total completion tokens: 40,353

## Quality Observations

STORM's output is much richer than a single prompt: it first creates perspectives, asks questions, searches the web, refines an outline, and writes section by section with citations.

However, the generated sample still has quality issues for serious scientific review work:

- The default web retriever introduces noisy sources, including generic web pages and some non-primary sources.
- Some claims are supported only by snippets, not full paper text.
- The article has good structure but remains closer to a Wikipedia-style overview than an AutoSurvey/OpenScholar-grade scholarly survey.
- Citation markers are dense, but citation grounding is only as good as the retrieved snippets.

For Tyro Duplex, this run confirms that the next optimization should not copy STORM's web retriever directly. The higher-ceiling path is to keep STORM's workflow shape, but replace retrieval and evidence construction with Semantic Scholar, OpenAlex, arXiv, Crossref, Unpaywall/full-text PDF extraction, DashScope embeddings, and DashScope rerank.
