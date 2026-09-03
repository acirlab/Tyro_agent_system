# Phase 3 Demo：SOTA Finder 候选图谱

## 目标

参考 AutoSOTA 和 Papers-with-Code-style 工作流，把“找 SOTA”建模为结构化 claim，而不是让 agent 给一个单句答案。

## 当前实现

- 自动识别包含 `SOTA / state of the art / benchmark / leaderboard / 最先进 / 榜单` 的任务。
- 输出 `SOTAClaim` 表。
- 当前证据等级为 `L1: paper self-claim`，表示只从论文标题/摘要识别候选。
- 报告里保留后续验证清单：榜单来源、结果表抽取、setting 可比性、代码复现状态。

## 演示命令

```bash
cd /home/acir/Tyro_duplex
python -m voice_agent.main --text "帮我找科研 agent 在文献综述任务上的 SOTA benchmark" --llm-provider fake --tts-provider fake --no-tts --no-play
```

重点展示报告中的：

- `## SOTA 候选`
- `## 候选论文池`
- `## 后续验证清单`

## 对应测试

```bash
python -m unittest tests.test_academic_research.AcademicResearchTests.test_phase3_sota_report_contains_structured_claim -v
```

## 组会可讲点

当前阶段只完成 SOTA 候选召回和 claim 结构化。真正可靠的 SOTA 需要继续接 benchmark registry、论文表格抽取、metric normalization 和可比性判断。
