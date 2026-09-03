# Phase 4 Demo：科研调研状态机

## 目标

为后续把主 agent 从“一次任务一个 tool”升级成“多步状态机执行”做准备。

## 当前实现

新增轻量 `ResearchStageMachine`，状态如下：

```text
scope -> retrieve -> structure -> verify -> write -> final
```

每个状态都有明确职责：

- `scope`：识别综述或 SOTA 任务。
- `retrieve`：检索学术数据库。
- `structure`：生成大纲、证据包或 SOTAClaim。
- `verify`：检查元数据、引用和可比性风险。
- `write`：写入 Markdown artifact。
- `final`：向用户返回短结论和路径。

## 演示命令

```bash
cd /home/acir/Tyro_duplex
python -m unittest tests.test_academic_research.AcademicResearchTests.test_phase4_research_stage_machine_advances -v
```

## 对应测试

```bash
python -m unittest tests.test_academic_research.AcademicResearchTests.test_phase4_research_stage_machine_advances -v
```

## 组会可讲点

当前主 runtime 仍保持简单稳定，科研状态机先作为独立模块存在。下一步可以让 `AgentRuntime.run_loop` 按状态机循环执行，从而支持中途暂停、继续、追加需求和阶段性汇报。
