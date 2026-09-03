# Phase 2 Demo：综述生成 Outline 与 Evidence Pack

## 目标

参考 STORM 和 AutoSurvey，把“生成综述”拆成可审阅的中间结构，而不是一次性让 LLM 写长文。

## 当前实现

- pipeline 会为 `academic_survey` 输出建议综述大纲。
- pipeline 会生成 STORM-style 多视角问题。
- 每个候选论文至少生成摘要 evidence chunk；有 PDF 时尝试全文解析。
- evidence chunks 会使用 DashScope `qwen3-rerank` 优先 rerank，失败时降级 embedding 或规则打分。
- 按“基础方法与模型 / 系统与工具 / 评估与 Benchmark / 应用与案例”生成初步分类。
- 每类生成 Section Evidence Pack，列出候选论文和摘要压缩片段。
- 报告中保留代表论文表和参考链接。

## 演示命令

```bash
cd /home/acir/Tyro_duplex
python -m voice_agent.main --text "帮我写一份科研 agent 辅助文献综述的调研" --llm-provider fake --tts-provider fake --no-tts --no-play
```

打开最新报告：

```bash
ls -td research/runs/* | head -1
```

重点展示报告中的：

- `## 摘要`
- `## 关键结论`
- `## 建议综述大纲`
- `## 正文综述`
- `## 综合对比`
- `## Section Evidence Pack`
- `## Citation Audit`
- `## OpenScholar-style 证据覆盖`
- `## 代表论文`

## 对应测试

```bash
python -m unittest tests.test_academic_research.AcademicResearchTests.test_phase2_survey_contains_outline_and_evidence_pack -v
```

## 组会可讲点

这一阶段的核心是把综述生成变成“检索 -> 分类 -> 大纲 -> evidence pack -> 草稿”的流水线。后续可以把分类替换为 embedding clustering 或 STORM 式多视角提问。

当前已经加入多视角问题、全文 chunk、rerank、citation audit。默认模式关闭 Qwen 长文增强以保证现场演示稳定；`research/demos/high_quality_research_config.jsonc` 会打开离线高质量写作。
