# Tyro Duplex

按 `ARCHITECTURE.md` 实现的双工语音 Agent MVP。

## 运行环境

推荐使用已准备好的 conda 环境：

```bash
conda activate duplex_model
```

默认基础配置在 `duplex_config.json`。常调参数在 `tuning_config.jsonc`，例如 pVAD 阈值、普通 VAD 最短说话时间、EOT 阈值、打断阈值、静音等待时间、TTS 语速和表情视频开关。这个文件支持 `//` 和 `/* */` 注释。模型路径和本地缓存说明见 `MODELS.md`。

## 快速验证

不加载真实 LLM/TTS，只验证对话控制和 Agent 执行链路：

```bash
python -m voice_agent.main --text 你好 --llm-provider fake --tts-provider fake --no-tts --no-play
python -m voice_agent.main --text 测试长任务 --llm-provider fake --tts-provider fake --no-tts --no-play
python -m voice_agent.main --text "帮我调研科研 agent 的综述论文" --llm-provider fake --tts-provider fake --no-tts --no-play
```

科研调研会检索学术来源并把完整 Markdown 报告写入 `research/runs/.../report.md`。每个阶段的组会 demo 记录在 `research/demos/`。

默认科研调研模式会使用 Semantic Scholar、OpenAlex、arXiv 检索，尝试 PDF 全文解析，使用 DashScope embedding/rerank 做证据排序，并输出 STORM-style 多视角问题、AutoSurvey-style section evidence pack、OpenScholar-style citation audit。默认会打开 Qwen 长文增强，适合作为后台任务运行；实时语音模式下不会阻塞收音，完成后会播报报告路径。快速现场演示可使用：

```bash
python -m voice_agent.main \
  --text "帮我调研科研 agent 的综述论文" \
  --tuning-config research/demos/fast_research_config.jsonc \
  --tts-provider fake --no-tts --no-play --disable-expression
```

运行测试：

```bash
python -m unittest discover -s tests -v
```

## 运行方式

文本输入：

```bash
python -m voice_agent.main --text "帮我查三款手机的区别"
```

音频文件输入：

```bash
python -m voice_agent.main --file /path/to/user.wav
```

实时麦克风和扬声器：

```bash
python -m voice_agent.main --live
```

默认会自动打开一个固定表情窗口，播放 `expression_video/neutral.mp4` 作为空闲表情。说话时会让 LLM 从 `expression_video` 目录里可用的视频名中选择表情，并在同一个窗口内切换视频，播报结束后回到 neutral。

临时关闭表情窗口：

```bash
python -m voice_agent.main --live --disable-expression
```

使用另一份调参文件：

```bash
python -m voice_agent.main --live --tuning-config tuning_config.local.jsonc
```

默认 LLM 使用 DashScope 兼容 OpenAI 接口，需要：

```bash
export DASHSCOPE_API_KEY=...
```

## 目录

```text
voice_agent/
├── audio/          麦克风、扬声器、AEC
├── turn/           pVAD、ASR、EOT、用户轮次、打断检测
├── speech/         TTS、语音调度、反馈播报
├── conversation/   意图分类和任务控制
├── agent/          任务状态、规划、执行循环、LLM
├── tools/          Tool 接口、注册表、内置工具
├── skills/         Skill 注册表和默认 skill 描述
└── infrastructure/ 事件总线
```
