# 开源科研 Agent 调研：综述生成与 SOTA 发现

调研日期：2026-08-27  
关注点：开源科研/调研 agent 如何实现“给定领域生成综述”和“给定任务找到 SOTA/前沿工作”。

## 1. 结论摘要

开源科研 agent 大体分成四类：

| 类型 | 代表项目 | 最适合的任务 | 实现核心 |
| --- | --- | --- | --- |
| Deep research 报告生成 | GPT Researcher、LangChain Open Deep Research、dzhng/deep-research | 给定问题生成带来源的调研报告 | 查询规划、多轮搜索、网页抓取、并行摘要、最终报告合成 |
| 综述/百科式文章生成 | STORM、AutoSurvey、AutoSurvey2、LitLLM | 给定领域生成长文综述、related work 或 Wikipedia-like article | 多视角提问、检索增强、分节并行写作、迭代修订 |
| 科研文献 RAG/问答 | PaperQA2、OpenScholar、ResearchPilot | 文献问答、证据抽取、引用可靠性较高的长答案 | 学术库检索、PDF/全文解析、chunk embedding、rerank、证据级引用 |
| 科研全流程/实验优化 | Agent Laboratory、AutoSOTA | 从 idea 到实验、报告，或复现并改进 SOTA | 多 agent 分工、代码执行、实验监控、评分反馈、有效性监督 |

总体判断：

- 如果目标是“输入一个领域，生成一篇综述文章”，最值得拆解的是 **STORM + AutoSurvey/AutoSurvey2 + OpenScholar/PaperQA2**。STORM 擅长从多视角提问构建结构，AutoSurvey 擅长把长综述拆成 outline/section/subsection 管线，OpenScholar/PaperQA2 擅长把引用和证据做实。
- 如果目标是“输入一个任务，尽可能找到所有 SOTA”，单纯让 LLM 搜网页不可靠。更稳的实现应当是：任务规范化 -> 学术数据库召回 -> benchmark/leaderboard 召回 -> paper-code 映射 -> 结果表抽取 -> 可比性判断 -> 时间线排序 -> 人工可审计证据输出。
- 目前真正开源且能直接复用的多为“调研报告/综述生成”框架；“自动发现新 SOTA”还偏研究原型。AutoSOTA 有论文和结果仓库，但公开仓库主要是优化结果榜与 CLI/结果材料，不等价于完整 agent 源码开放。

## 2. 代表项目详析

### 2.1 GPT Researcher

来源：[GitHub](https://github.com/assafelovic/gpt-researcher)、[实现说明](https://docs.gptr.dev/blog/building-gpt-researcher)

定位：通用 open deep research agent，可面向网页和本地资料生成带引用的调研报告。GitHub 页面显示约 29k stars，Apache-2.0 license。

实现方式：

- 采用 planner/executor/publisher 架构。planner 先把研究问题拆成一组子问题；executor/crawler 针对子问题抓取网页、过滤并摘要；publisher 聚合所有摘要生成最终报告。
- 设计上追求“有限步骤完成”，避免 AutoGPT 式无限循环。核心是先生成固定 research questions，再并行执行。
- 使用 asyncio 并行抓取/总结多个 URL，以降低调研耗时。
- 引用通过 source tracking 保存，每个资源先摘要再进入最终上下文，最终报告只基于聚合信息生成。

适用性：

- 适合做业务/技术/政策/市场类调研报告，也可做科研初筛。
- 对学术综述的弱点是：默认依赖通用 web search，文献元数据、引用质量、benchmark 结构化信息需要额外接 Semantic Scholar/OpenAlex/Crossref/PubMed/Papers-with-code-style 数据源。

可复用点：

- planner -> 并行 crawler -> summarizer -> publisher 是实现 deep research 的最小可靠架构。
- 对科研场景应把 crawler 换成 scholar retriever，并增加 DOI/venue/year/citation/benchmark 字段。

### 2.2 STORM / Co-STORM

来源：[GitHub](https://github.com/stanford-oval/storm)、[在线 demo](https://storm.genie.stanford.edu/)

定位：Stanford OVAL 的开源知识整理系统，输入 topic，生成带引用的 Wikipedia-like 长文。GitHub 页面显示约 31k stars，MIT license。

实现方式：

- 两阶段：pre-writing 和 writing。pre-writing 阶段先基于互联网研究收集 reference 并生成 outline；writing 阶段再按 outline 和 references 生成完整文章。
- STORM 的关键不是“直接让 LLM 写提纲”，而是先发现多种 perspective，再让不同视角驱动 question asking。
- 使用 simulated conversation：模拟 Wikipedia writer 与 topic expert 的对话，expert 回答必须 grounded in external sources，writer 基于回答追问，从而扩展 topic 覆盖面。
- Co-STORM 在此基础上加入多人协作协议：LLM experts、moderator、human user 共同推进讨论，并维护动态 mind map。
- 代码模块化，使用 DSPy，并可替换语言模型与检索模块；支持搜索引擎，也支持 VectorRM 读取用户文档。

适用性：

- 很适合“给定领域生成结构化综述草稿”，尤其是需要覆盖不同视角、先做 pre-writing 的场景。
- 生成目标偏 Wikipedia-like，不是严格学术 survey；要产出论文式综述，需要替换写作 prompt、引用格式和学术检索源。

可复用点：

- “多视角提问”是提高综述广度的有效机制。
- mind map/outline 应作为中间产物持久化，方便人工审阅后再写正文。

### 2.3 AutoSurvey / AutoSurvey2

来源：[AutoSurvey GitHub](https://github.com/AutoSurveys/AutoSurvey)、[AutoSurvey 论文](https://arxiv.org/abs/2406.10252)、[AutoSurvey2 论文](https://arxiv.org/html/2510.26012v2)

定位：专门为“自动生成学术 survey”设计。AutoSurvey 已开源，MIT license，仓库提供 53 万 arXiv CS abstracts 数据库下载说明；AutoSurvey2 论文声称代码资源在 `annihi1ation/auto_research`。

AutoSurvey 实现方式：

- 使用 embedding-based retrieval 先从论文库召回候选文献。
- outline generation 使用大量参考文献，示例参数 `outline_reference_num=1500`。
- 正文按 section/subsection 拆分生成，示例参数支持 `section_num`、`subsection_len`、`rag_num`。
- 通过 RAG 解决 LLM 训练知识过时和上下文窗口限制。
- 论文中包含 citation quality、content coverage、structure 等评估思路。

AutoSurvey2 实现方式：

- 四阶段管线：检索指导的 survey outline 构建；section 级文献检索与分析；基于证据生成 section 内容；后处理并组装为 LaTeX。
- 增加实时检索增强，强调纳入近期论文。
- 增加 multi-LLM evaluation，用多个模型评估 coverage、structure、relevance。
- 论文描述为 graph-based execution framework，把长文生成拆成可复现的协调阶段。

适用性：

- 最贴近“给定领域生成一篇综述文章”的目标。
- AutoSurvey 第一版主要依赖 arXiv CS abstract 数据库；如果需要跨学科、高引用可靠性或全文证据，需要扩展数据源和 PDF/full-text pipeline。

可复用点：

- 综述生成不宜一次性端到端生成，应拆成：检索 -> 聚类/主题树 -> outline -> section evidence pack -> section draft -> cross-section consistency revise -> citation audit。
- 对长综述，section 级并行写作比单 prompt 更可控。

### 2.4 PaperQA2 / WikiCrow / ContraCrow

来源：[GitHub](https://github.com/Future-House/paper-qa)、[FutureHouse 公告](https://www.futurehouse.org/news/wikicrow)、[PaperQA 论文](https://arxiv.org/html/2312.07559v2)

定位：面向科学论文的高准确率 agentic RAG。GitHub 页面显示 Apache-2.0 license。PaperQA2 支持 PDF、文本、Office 文档和代码文件，重点是科学文献。

实现方式：

- 早期 PaperQA 明确把 RAG 拆成 agent tools：search、gather_evidence、answer_question。
- search 负责从 arXiv/PubMed 等数据库找论文、解析全文、切 chunk、embedding 后写入向量库。
- gather_evidence 用 query embedding + MMR 找多样化相关 chunk，再用 summary LLM 生成与问题相关的 evidence，并给相关性评分。
- answer_question 基于积累 evidence 生成带引用答案；agent 可以在证据不足时改写 query、多次 search 或 gather evidence。
- PaperQA2 README 提到的升级包括 metadata-aware embeddings、LLM reranking、contextual summarization、citation/journal quality metadata、多 provider 元数据冗余获取、本地全文搜索引擎。
- WikiCrow 是基于 PaperQA2 的百科式科学总结 agent；ContraCrow 用于检查论文 claim 与文献中的矛盾。

适用性：

- 适合科研 QA、证据总结、局部综述、引用可追溯回答。
- 生成完整综述时，需要额外的 outline/planning 层，否则更像“回答问题”而非“组织领域知识”。

可复用点：

- 科研 agent 应把“证据”作为一等对象存储：paper_id、DOI、title、year、chunk、page/section、quote/summary、score。
- citation audit 不应只检查标题存在，还要检查 claim 是否由 evidence 支撑。

### 2.5 OpenScholar

来源：[GitHub](https://github.com/AkariAsai/OpenScholar)、[Nature 论文](https://www.nature.com/articles/s41586-025-10072-4)、[Ai2 博文](https://allenai.org/blog/nature-openscilm)

定位：Ai2/UW 的开放检索增强科学文献合成系统。代码、模型 checkpoints、数据和 benchmark 开放。GitHub 页面显示 Apache-2.0 license，约 1.6k stars。

实现方式：

- 使用 open-weight LLM 与训练过的 retrieval models，而不是只用闭源 API prompt。
- 构建 OpenScholar DataStore，论文称包含大规模开放科学语料；Ai2 博文提到构建了 4500 万开放获取科学论文语料及 full-text snippet index，并通过 Semantic Scholar API 提供相关检索能力。
- 系统包含 adaptive retrieval 和 self-feedback-guided generation，生成后会根据反馈迭代修正长答案。
- 仓库结构包含 `src/` 推理代码、`training/` 训练代码、`retriever/` 离线检索与在线 retrieval server 代码。
- 同时发布 ScholarQABench，用于评估 scientific synthesis 与 citation quality。

适用性：

- 很适合作为“严肃科研综述/问答”的底座，特别是希望使用开放模型、开放索引和可复现实验时。
- 部署复杂度高于 GPT Researcher/STORM，需要处理模型、检索服务和数据索引。

可复用点：

- 若目标是低幻觉科研综述，核心壁垒在 retriever 和 citation grounding，而不是 UI 或 prompt。
- 可以把 OpenScholar 式 retrieval/synthesis 作为后端 evidence engine，再接 STORM/AutoSurvey 的 planning/writing。

### 2.6 LangChain Open Deep Research / Deep Research From Scratch

来源：[Open Deep Research GitHub](https://github.com/langchain-ai/open_deep_research)、[Deep Research From Scratch](https://github.com/langchain-ai/deep_research_from_scratch)、[LangChain 博文](https://www.langchain.com/blog/open-deep-research)

定位：LangGraph 实现的开源 deep research agent。注意：GitHub 页面显示 `open_deep_research` 仓库已在 2026-08-21 归档，仍可作为实现参考。

实现方式：

- 官方 README 把流程拆为 scope、research、write。
- scope 阶段通过结构化输出判断是否需要澄清，并把用户对话转成 detailed research brief。
- research 阶段采用 ReAct-style agent loop：LLM decision node + tool execution node，迭代调用 Tavily、原生 web search 或 MCP tools。
- 对长上下文使用 search result summarization、research findings compression，再交给 final report model。
- 配置上把 summarization、research、compression、final report model 拆开，便于不同成本/能力模型组合。
- legacy multi-agent implementation 使用 supervisor-researcher 架构，多 researcher 并行。

适用性：

- 适合构建可配置的通用调研 agent，尤其是已有 LangChain/LangGraph 技术栈时。
- 学术 SOTA 场景需要把 MCP/search tools 换成 Semantic Scholar、OpenAlex、arXiv、PubMed、Crossref、Hugging Face、CodeSOTA 等专用工具。

可复用点：

- 明确区分 scoping model、search agent、compression model、writer model，有助于控制成本和质量。
- LangGraph 的 state/conditional routing 很适合实现“证据不足则继续检索，证据足够则写作”。

### 2.7 dzhng/deep-research

来源：[GitHub](https://github.com/dzhng/deep-research)

定位：极简 deep research agent，目标是用少于 500 行代码展示核心机制。GitHub 页面显示 MIT license，约 19.6k stars。

实现方式：

- 输入 query、breadth、depth。
- 先生成 SERP queries，再处理搜索结果，抽取 learnings 和 next directions。
- 如果 depth > 0，则基于 prior goals、new questions、learnings 递归继续探索。
- 最终把所有 findings 编译成 Markdown report，并包含 sources/references。

适用性：

- 很适合学习和二次开发最小 deep research loop。
- 不适合直接用于高可靠科研综述；缺少学术元数据、全文解析、引用核验、benchmark 可比性检查。

可复用点：

- breadth/depth 是一个实用的用户可控抽象：breadth 控制横向召回，depth 控制递归追问层数。

### 2.8 Agent Laboratory

来源：[GitHub](https://github.com/SamuelSchmidgall/AgentLaboratory)、[项目页](https://agentlaboratory.github.io/)、[论文](https://arxiv.org/abs/2501.04227)

定位：从研究 idea 到文献综述、实验、报告写作的端到端科研助手。GitHub 页面显示 MIT license，约 5.8k stars。

实现方式：

- 三阶段：Literature Review、Experimentation、Report Writing。
- 使用多个 specialized LLM agents，集成 arXiv、Hugging Face、Python、LaTeX 等外部工具。
- mle-solver 负责 ML 实验代码迭代：根据 task instructions、command descriptions、distilled knowledge 生成 REPLACE/EDIT 修改，运行后按 scoring function 更新 top programs，报错时自动 repair。
- paper-solver 根据 research plan、实验结果、insights 和 literature review 生成标准 academic paper。
- 支持人在每阶段给 feedback/guidance，不把 agent 设计成完全替代研究者。

适用性：

- 适合“已有研究 idea，要补文献、做实验、写报告”的 workflow。
- 不是专门的“领域综述生成器”；文献综述只是整个实验研究管线的一环。

可复用点：

- 对 SOTA 任务，代码执行与评分闭环是必要的。没有复现实验，agent 只能“报告别人声称的 SOTA”，无法判断是否可复现或可比。

### 2.9 ResearchPilot

来源：[论文](https://arxiv.org/abs/2603.14629)

定位：local-first、自托管、多 agent 文献综述辅助系统。论文描述为开源系统。

实现方式：

- 输入自然语言 research question。
- 从 Semantic Scholar 和 arXiv 检索论文。
- 基于 abstracts 抽取 structured findings。
- 综合跨论文模式，生成 citation-aware related-work section。
- 技术栈：FastAPI、Next.js、DSPy、SQLite、Qdrant；支持 BYOK 模型访问、本地或远程 embeddings。
- 强调 typed agent interfaces、persistence、history search 和本地可审计架构。

适用性：

- 很适合“自托管文献 synthesis 工作台”的工程形态参考。
- 论文也明确限制：abstract-only extraction、外部 API rate limit、coverage 不完整、缺少 citation verification。

可复用点：

- 本地优先架构应包含：任务历史、证据库、向量库、结构化 agent 输出 schema、可追踪生成记录。

### 2.10 AutoSOTA

来源：[论文](https://arxiv.org/html/2604.05550v1)、[GitHub 结果仓库](https://github.com/tsinghua-fib-lab/AutoSOTA)、[结果板](https://tsinghua-fib-lab.github.io/AutoSOTA/)

定位：面向“复现并改进 SOTA AI 模型”的端到端自动研究系统。严格说，它更偏实验优化 agent，而不是文献综述 agent。

实现方式：

- 三阶段：resource preparation and goal setting；experiment evaluation；reflection and ideation。
- 八个 specialized agents：资源发现/获取、objective rubric 构建、环境初始化、实验监控、错误修复、idea 生成、调度、有效性监督。
- AgentResource 把论文映射到代码仓库和依赖；AgentObjective 把论文目标拆成可验证的树状评价 rubric。
- AgentMonitor 处理长时间实验状态、deadlock 和外部记忆；AgentFix 修复运行时冲突；AgentSupervisor 用红线系统避免无效优化或投机结果。
- 论文声称在多类 AI 任务中自动发现 105 个新 SOTA，平均每篇约 5 小时。

开源状态判断：

- GitHub 仓库为 MIT license，页面描述为“自动优化研究代码库的 curated leaderboard”，跟踪内部 pipeline 的优化结果。
- 公开材料很有工程参考价值，但从仓库说明看，更像结果与 CLI/榜单，不应等同于完整 AutoSOTA agent 源码已开放。

可复用点：

- “找 SOTA”如果升级为“验证/改进 SOTA”，必须加入代码仓库 grounding、环境修复、实验调度、metric/rubric 审计。

### 2.11 其他相关开源项目

- LitLLM：[GitHub](https://github.com/shubhamagarwal92/LitLLM)、[论文](https://arxiv.org/abs/2402.01788)。从用户 abstract 出发，先用 LLM 摘出关键词检索相关论文，再 rerank，最后生成 related work。适合“已有论文草稿，补 related work”。
- prismAId：[GitHub](https://github.com/Open-and-Sustainable/prismAId)、[官网](https://prismaid.review/)。偏 PRISMA/systematic review 的筛选、获取、转换、抽取和协议核查，不是自由式综述写作 agent，但其可复现审查流程值得借鉴。
- OpenDraft：[GitHub](https://github.com/federicodeponte/opendraft)。开源研究论文写作工具，介绍称使用多 agent 生成长论文，并用 Crossref/OpenAlex/arXiv 等校验引用。更偏论文写作产品化。

## 3. 实现模式横向比较

### 3.1 检索层

科研 agent 的检索层通常需要多源融合：

- 学术元数据：Semantic Scholar API、OpenAlex API、Crossref REST API。
- 预印本/学科库：arXiv、PubMed、bioRxiv、ACL Anthology 等。
- 代码与实现：GitHub、Hugging Face、CatalyzeX、历史 Papers with Code 数据、CodeSOTA 等。
- 通用网页：Tavily、Bing、Google、DuckDuckGo、Firecrawl/Crawl4AI 等。
- 本地材料：PDF 文件夹、Zotero library、已有 bibtex、实验日志、用户上传文档。

可实现的数据结构：

```text
Paper {
  paper_id, doi, title, authors, year, venue,
  abstract, url, pdf_url, code_urls,
  citation_count, influential_citation_count,
  references, citations,
  tasks, datasets, metrics, reported_results
}

Evidence {
  paper_id, section, page, chunk_text,
  claim_supported, relevance_score,
  quote_or_span, summary, source_url
}

BenchmarkResult {
  task, dataset, metric, score,
  direction: higher_is_better | lower_is_better,
  model_or_method, paper_id, code_url,
  date, eval_setting, comparability_notes
}
```

### 3.2 Planning 层

常见策略：

- GPT Researcher：先生成研究子问题，确保任务有限可完成。
- STORM：用 perspective-guided question asking 扩展广度。
- AutoSurvey：先生成 outline，再按章节召回 evidence。
- Open Deep Research：先 scope/clarify，再生成 detailed research brief。
- WisPaper 类系统：将复杂 query 拆成可编辑 verification criteria，再验证候选论文是否真正满足。

最佳实践：

- 对“综述生成”，planning 的输出不应只是标题列表，而应包含每节的 research questions、关键词、必含 seminal papers、排除条件、证据需求。
- 对“SOTA 查找”，planning 的输出应包含 task/dataset/metric 三元组，以及可比性约束，例如 zero-shot/fine-tuned、closed/open model、train data、test split、input resolution、hardware budget。

### 3.3 读文献与证据抽取

常见实现：

- PDF/text 解析后按 section-aware chunking 切块。
- embedding 检索初筛，再用 LLM reranking 或 cross-encoder reranking。
- MMR 保证 evidence 多样性，避免所有证据来自同一篇论文或同一段文字。
- LLM 对 chunk 做 query-focused summary，并给 relevance/confidence 分数。
- evidence pack 按章节或 claim 聚合，供 writer 使用。

关键要求：

- 证据对象必须保留来源位置，至少有 paper_id/title/year/url，最好有 page/section/原文 span。
- 生成正文时 writer 只能引用 evidence pack 中存在的 source，不能自由发明引用。

### 3.4 长文生成

常见实现：

- Map-reduce：每篇/每 chunk 先 map 成 evidence，再 reduce 成答案。
- Hierarchical writing：先生成 outline，再 section，再 subsection，再全局 revise。
- Parallel section drafting：章节并行写作，最后做 cross-section consistency。
- Compression：把中间检索发现压缩成 structured notes，避免上下文爆炸。
- Multi-LLM judge：从 coverage、structure、relevance、citation quality 角度打分，触发迭代修订。

### 3.5 引用与事实校验

推荐从弱到强分层：

1. 元数据存在性校验：标题、作者、年份、DOI 是否能在 Crossref/OpenAlex/Semantic Scholar 查到。
2. 引用相关性校验：被引用论文是否与句子 claim 主题相关。
3. 证据支撑校验：claim 是否能由具体 chunk/quote 支撑。
4. 覆盖性校验：是否遗漏 seminal/highly cited/recent papers。
5. 可比性校验：SOTA 表格中的 score 是否来自同一 dataset、metric、split 和 evaluation protocol。

OpenScholar、PaperQA2 的启示是：引用准确性不是最后格式化 bibliography 就能解决，必须从检索和 evidence 抽取阶段开始约束。

## 4. 如何实现“给定领域生成综述”

推荐架构：

```text
User topic
  -> scope/clarify
  -> query expansion: keywords + subfields + time range + venues
  -> broad scholar retrieval
  -> dedup + metadata enrichment
  -> topic clustering / taxonomy / perspective discovery
  -> outline generation
  -> per-section targeted retrieval
  -> evidence extraction and reranking
  -> section drafting in parallel
  -> cross-section merge and consistency revision
  -> citation audit and missing-paper search
  -> final Markdown/LaTeX/PDF
```

实现建议：

- 先用 Semantic Scholar/OpenAlex 做 metadata 召回，再用 arXiv/PubMed/出版社页面补 PDF/full text。
- 对 AI/ML 领域，必须单独接 code/benchmark 源，否则综述会缺少方法复现与 SOTA 信息。
- outline 生成前先做 clustering 或 perspective discovery，避免 LLM 只按常识生成泛泛章节。
- 每个 section 生成前都构建 evidence pack，包含 10-30 篇关键论文的结构化摘要。
- 综述输出应包含“代表论文表”“方法分类表”“benchmark/SOTA 表”“开放问题表”，而不只是自然语言段落。

## 5. 如何实现“给定任务找到所有 SOTA”

“所有 SOTA”在工程上需要谨慎定义。SOTA 不是单个事实，而是某个 `task/dataset/metric/eval setting/date` 下的最优结果。推荐流程：

```text
Task description
  -> task normalization
  -> generate benchmark candidates
  -> search academic papers by task/dataset/metric
  -> search leaderboard / benchmark registries
  -> search code repositories and model cards
  -> extract result tables from papers
  -> normalize scores and metric direction
  -> judge comparability
  -> rank by benchmark setting and date
  -> produce auditable SOTA map
```

需要的 agent/tool 分工：

- Query Planner：把自然语言任务拆成 task、dataset、metric、领域别名。
- Scholar Retriever：查 Semantic Scholar/OpenAlex/arXiv/ACL Anthology/PubMed。
- Leaderboard Retriever：查 Hugging Face leaderboards、CodeSOTA、历史 Papers with Code 数据、领域专属榜单。
- Code Retriever：查 GitHub/Hugging Face model cards、论文 official repo、CatalyzeX 类 paper-code 映射。
- Table Extractor：从 PDF/HTML/LaTeX/README 抽取 result tables。
- Comparability Judge：判断数据集 split、训练设定、模型规模、外部数据、推理 budget 是否可比。
- Verifier：要求每个候选 SOTA 都有 source URL、paper、score、metric、date、代码或复现状态。

输出格式建议：

```text
SOTAClaim {
  task, dataset, metric, setting,
  method, score, rank,
  paper_title, authors, year, venue,
  code_url, model_url,
  evidence_url, table_or_section,
  comparable: yes/no/uncertain,
  notes
}
```

重要现实约束：

- Papers With Code 的 GitHub 组织仍保留历史数据仓库和 SOTA extractor 等项目，但实时 leaderboards 生态已发生变化；截至本次调研，GitHub 上 `paperswithcode-data` 仍可访问但不应当作为唯一实时来源。
- 新兴替代品和 Hugging Face leaderboards 往往覆盖局部任务，不能保证跨领域完整。
- 对前沿 AI 论文，很多 “SOTA” 来自论文自报表格；agent 需要明确标记“论文声称”“榜单记录”“第三方复现”“本地复现”四种证据等级。

## 6. 推荐组合方案

如果要在项目中落地一个科研 agent，建议组合如下：

### 方案 A：快速搭建调研报告 agent

- 基础框架：GPT Researcher 或 LangGraph/Open Deep Research 思路。
- 搜索层：Tavily/web search + Semantic Scholar + OpenAlex。
- 输出：Markdown report with citations。
- 适合：技术调研、领域入门、非严格学术综述。

### 方案 B：严肃综述生成 agent

- Planning：STORM 的 perspective-guided question asking。
- Retrieval/Evidence：PaperQA2 或 OpenScholar 思路。
- Writing：AutoSurvey/AutoSurvey2 的 outline/section/subsection 分层生成。
- Verification：Crossref/OpenAlex/Semantic Scholar 元数据校验 + claim-evidence 校验。
- 输出：LaTeX/Markdown 综述、论文表、方法分类表、开放问题。

### 方案 C：SOTA 发现 agent

- Retrieval：Semantic Scholar/OpenAlex/arXiv/ACL Anthology/PubMed。
- Benchmark：Hugging Face leaderboards、CodeSOTA、历史 Papers with Code 数据、领域专属榜单。
- Code：GitHub/Hugging Face/CatalyzeX-style paper-code mapping。
- Extraction：PDF table extraction + LLM structured extraction。
- Verification：benchmark comparability judge + citation/source audit。
- 输出：按 task/dataset/metric 分组的 SOTA map，而不是单一答案。

### 方案 D：SOTA 复现/改进 agent

- 基础思路：Agent Laboratory + AutoSOTA。
- 必需能力：仓库克隆、环境构建、依赖修复、实验运行、日志监控、metric 解析、版本管理、红线规则。
- 输出：复现实验报告、改动 diff、score 对比、失败日志。

## 7. 工程注意事项

- 不要让 writer 直接访问全网。writer 只消费已审计 evidence pack。
- 检索要记录 query history，否则无法解释“为什么没找到某篇论文”。
- 每轮检索都要 dedup：同一论文可能以 arXiv、conference、OpenReview、publisher 多个版本出现。
- 综述生成要有 coverage check：高被引论文、近 6-12 个月新论文、顶会/顶刊论文应分别覆盖。
- 对 SOTA 表格要记录 metric direction 和 eval setting；否则 “更高/更低更好” 或不同 split 会混淆。
- 对 citation hallucination，最低限度要做 DOI/title 存在性检查；更好的做法是 claim-level evidence check。
- Human-in-the-loop 很关键：让用户审 outline、审 included/excluded papers、审 SOTA comparability，比最后审一篇长文有效得多。

## 8. 来源索引

- GPT Researcher GitHub: https://github.com/assafelovic/gpt-researcher
- GPT Researcher implementation note: https://docs.gptr.dev/blog/building-gpt-researcher
- STORM GitHub: https://github.com/stanford-oval/storm
- STORM demo: https://storm.genie.stanford.edu/
- AutoSurvey GitHub: https://github.com/AutoSurveys/AutoSurvey
- AutoSurvey paper: https://arxiv.org/abs/2406.10252
- AutoSurvey2 paper: https://arxiv.org/html/2510.26012v2
- PaperQA2 GitHub: https://github.com/Future-House/paper-qa
- PaperQA paper: https://arxiv.org/html/2312.07559v2
- FutureHouse PaperQA2/WikiCrow announcement: https://www.futurehouse.org/news/wikicrow
- OpenScholar GitHub: https://github.com/AkariAsai/OpenScholar
- OpenScholar Nature paper: https://www.nature.com/articles/s41586-025-10072-4
- Ai2 OpenScholar blog: https://allenai.org/blog/nature-openscilm
- LangChain Open Deep Research: https://github.com/langchain-ai/open_deep_research
- LangChain Deep Research From Scratch: https://github.com/langchain-ai/deep_research_from_scratch
- LangChain blog: https://www.langchain.com/blog/open-deep-research
- dzhng/deep-research: https://github.com/dzhng/deep-research
- Agent Laboratory GitHub: https://github.com/SamuelSchmidgall/AgentLaboratory
- Agent Laboratory project page: https://agentlaboratory.github.io/
- Agent Laboratory paper: https://arxiv.org/abs/2501.04227
- ResearchPilot paper: https://arxiv.org/abs/2603.14629
- AutoSOTA paper: https://arxiv.org/html/2604.05550v1
- AutoSOTA GitHub: https://github.com/tsinghua-fib-lab/AutoSOTA
- AutoSOTA results board: https://tsinghua-fib-lab.github.io/AutoSOTA/
- LitLLM GitHub: https://github.com/shubhamagarwal92/LitLLM
- LitLLM paper: https://arxiv.org/abs/2402.01788
- prismAId GitHub: https://github.com/Open-and-Sustainable/prismAId
- prismAId site: https://prismaid.review/
- OpenDraft GitHub: https://github.com/federicodeponte/opendraft
- Semantic Scholar API: https://www.semanticscholar.org/product/api
- OpenAlex API docs: https://help.openalex.org/api/
- Crossref REST API docs: https://github.com/Crossref/rest-api-doc
- Papers with Code GitHub org/data: https://github.com/paperswithcode
- CodeSOTA discussion of post-PWC leaderboard landscape: https://www.codesota.com/papers-with-code
