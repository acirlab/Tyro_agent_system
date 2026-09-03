# 科研调研能力阶段 Demo 索引

每个阶段完成后保留一份可在组会上展示的 demo/test 记录：

- Phase 1: `phase1_academic_research_mvp.md`
- Phase 2: `phase2_survey_generation.md`
- Phase 3: `phase3_sota_finder.md`
- Phase 4: `phase4_research_state_machine.md`
- 综述效果对齐说明：`../survey_quality_alignment.md`

统一测试命令：

```bash
cd /home/acir/Tyro_duplex
python -m unittest discover -s tests -v
```

默认后台高质量命令：

```bash
cd /home/acir/Tyro_duplex
python -m voice_agent.main --text "帮我调研科研 agent 的综述论文" --tts-provider fake --no-tts --no-play --disable-expression
```

默认配置会打开 Qwen writer、更多检索和更多全文解析，适合后台运行。实时语音模式下任务在后台执行，完成后播报报告路径。

快速现场演示配置：

```bash
cd /home/acir/Tyro_duplex
python -m voice_agent.main \
  --text "帮我调研科研 agent 的综述论文" \
  --tuning-config research/demos/fast_research_config.jsonc \
  --tts-provider fake --no-tts --no-play --disable-expression
```

说明：快速模式启用学术检索、全文解析、embedding/rerank 和 evidence audit，但关闭 LLM 长文增强，保证现场可控。`high_quality_research_config.jsonc` 与默认配置一致，保留为会前离线生成材料的显式配置。
