# 综述生成效果对齐说明

## 开源项目的“好综述”长什么样

### STORM

STORM 的目标是从 topic 自动生成 Wikipedia-like full-length article。它不是简单列搜索结果，而是先做 pre-writing：收集 references、生成 outline，再进入 writing：基于 outline 和 references 写完整长文并带 citations。其关键机制是 perspective-guided question asking 和 simulated conversation，用不同视角主动提出问题，提升覆盖面。

对齐到 Tyro Duplex：

- 报告必须有 `建议综述大纲`。
- 正文必须是多章节文章，而不是只有论文列表。
- 正文中的观点要引用 `[P#]`，并能回到参考文献。
- 后续要补多视角问题生成。

### AutoSurvey / AutoSurvey2

AutoSurvey 面向 academic survey generation，典型参数包括 section 数、subsection 长度、RAG 论文数、outline reference 数。AutoSurvey2 进一步强调四阶段：retrieval-guided outline、section-level retrieval and analysis、grounded section generation、post-processing into LaTeX。

对齐到 Tyro Duplex：

- 报告要按 section 组织。
- 每个 section 都要有自己的 evidence pack。
- 需要有方法 taxonomy、代表论文表、未来方向。
- 后续要把 section 级检索和 section 级写作拆开。

### OpenScholar / PaperQA2

这类系统的重点不是文章结构，而是 citation grounding。OpenScholar 强调 retrieval-augmented scientific synthesis、citation accuracy 和 self-feedback refinement；PaperQA2/PaperQA 将 search、gather evidence、answer question 拆成 agent tools，并让 evidence 成为中间对象。

对齐到 Tyro Duplex：

- 每个结论都要能追溯到具体论文。
- 当前 `[P#]` 是论文级引用，下一步应升级为 page/section/chunk 级证据。
- 需要 citation audit，区分“论文存在”和“claim 被原文支撑”。

## 本轮已经完成的对齐

- 由“简单列表”升级为“综述文章骨架”。
- 增加 `摘要`、`调研范围与方法`、`关键结论`、`主题脉络`、`方法与系统分类`、`正文综述`、`综合对比`、`未来方向`。
- 增加 `[P#]` 论文编号，正文、表格、evidence pack 和参考文献共用同一引用体系。
- 增加 relevance rerank，减少只含通用 `survey` 的噪声。
- 增加 STORM-style 多视角问题。
- 增加 PDF 全文获取、PyMuPDF 解析、chunk evidence、DashScope embedding/rerank。
- 增加 Citation Audit 和 OpenScholar-style 证据覆盖统计。
- 真实 LLM writer 可通过 `research.use_llm_writer` 打开，生成 `LLM 增强综述`。

## 还没有达到开源最佳效果的部分

- 还没有 STORM 式多视角提问和 simulated conversation。
- 还没有完整 simulated conversation。
- section-level 独立检索已经有雏形，但还没有独立写作、全局修订和多轮 evaluator。
- 已有全文 chunk 和 citation audit，但还没有真正 claim-level entailment 判断。
- 当前 taxonomy 仍是规则分类，后续应换成 embedding clustering + LLM rerank。
