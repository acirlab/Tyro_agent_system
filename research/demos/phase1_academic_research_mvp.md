# Phase 1 Demo：科研调研 MVP Tool

## 目标

把科研调研能力作为一个高层 tool 融合进现有 Tyro Duplex 语音 agent，不重构主 runtime。

## 当前实现

- 新增 `academic_research` tool。
- 新增 `academic_research` skill。
- 接入 Semantic Scholar、OpenAlex、arXiv、Crossref client。
- 用户说“论文 / 文献 / 综述 / SOTA / benchmark / 前沿 / 顶会”等关键词时，会进入科研调研 skill。
- tool 运行后把完整 Markdown 报告写入 `research/runs/.../report.md`。

## 演示命令

```bash
cd /home/acir/Tyro_duplex
python -m voice_agent.main --text "帮我调研科研 agent 的综述论文" --llm-provider fake --tts-provider fake --no-tts --no-play
```

预期效果：

- 终端输出用户输入。
- agent 返回“科研调研完成，模式是 academic_survey，整理了 N 篇候选论文。”
- `research/runs/` 下出现新的 `report.md`。

## 对应测试

```bash
python -m unittest tests.test_academic_research.AcademicResearchToolTests -v
python -m unittest tests.test_tool_registry.ToolRegistryTests -v
python -m unittest tests.test_conversation_controller.ConversationControllerTests.test_classifies_academic_research_start -v
```

## 组会可讲点

第一阶段没有改动双工语音主链路，只扩展 tool/skill，因此风险低；长任务进度通过已有 `progress_callback` 回传，保留打断和查询进度能力。
