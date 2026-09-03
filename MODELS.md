# 项目模型组件说明

本文档汇总当前项目语音交互链路中各组件使用的具体模型、配置位置和作用范围。默认配置来自 `duplex_config.json`，封装代码主要在 `duplex.py`、`asr.py`、`tts.py`、`eot.py`、`pvad.py`。

## 总体链路

```text
麦克风音频 / WAV 文件
  -> WebRTC APM AEC 回声消除
  -> FireRedChat pVAD 语音活动检测
  -> FunASR / SenseVoice ASR 语音识别
  -> FireRedChat EOT 轮次结束判断
  -> Qwen Flash LLM 回复生成
  -> Kokoro TTS 语音合成
  -> 扬声器播放
```

## 组件与模型

| 组件 | 默认模型 / 实现 | 配置位置 | 作用 |
| --- | --- | --- | --- |
| AEC 回声消除 | LiveKit WebRTC APM `AudioProcessingModule` | `duplex_config.json` 的 `aec` | 播放 TTS 时消除扬声器回声，减少误识别和误打断 |
| pVAD 语音检测 | `FireRedTeam/fireredchat-pvad`，核心文件 `pvad.onnx` | `duplex_config.json` 的 `pvad.activation_threshold` | 判断用户是否正在说话，驱动主状态机 |
| 说话人嵌入 | `fireredchat-pvad` 附带的 `spkrec-ecapa-voxceleb` 资源 | `duplex_config.json` 的 `pvad.update_speaker_embedding` | 在足够长的用户语音后更新 pVAD 的说话人特征 |
| ASR 语音识别 | ModelScope `iic/SenseVoiceSmall` | `duplex_config.json` 的 `asr.model` | 将用户语音转文字 |
| EOT 结束判断 | Hugging Face `FireRedTeam/FireRedChat-turn-detector`，模型文件 `chinese_best_model_q8.onnx` | `duplex_config.json` 的 `eot` | 判断用户这轮话是否已经说完 |
| EOT Tokenizer | `google-bert/bert-base-multilingual-cased` | `duplex_config.json` 的 `eot.tokenizer` | 给 EOT ONNX 模型做文本编码 |
| LLM 回复生成 | DashScope 兼容 OpenAI 接口的 `qwen-flash` | `duplex_config.json` 的 `llm` | 根据用户文本生成助手回复 |
| TTS 语音合成 | Hugging Face `hexgrad/Kokoro-82M` | `duplex_config.json` 的 `tts.repo_id` | 将助手回复合成为语音 |
| TTS 音色 | Kokoro voice `zf_xiaoyi` | `duplex_config.json` 的 `tts.voice` | 中文女声音色 |

## 本机绝对路径

以下路径是在本机 `duplex_model` conda 环境下确认的实际本地位置。

运行环境：

```text
/home/acir/anaconda3/envs/duplex_model
```

### AEC / WebRTC APM

AEC 是 LiveKit WebRTC APM 音频处理实现，不是单独的神经网络模型文件。

```text
Python 封装:
/home/acir/anaconda3/envs/duplex_model/lib/python3.12/site-packages/livekit/rtc/apm.py

LiveKit FFI 动态库:
/home/acir/anaconda3/envs/duplex_model/lib/python3.12/site-packages/livekit/rtc/resources/liblivekit_ffi.so
```

### FireRedChat pVAD

当前项目加载的是 `third_party` 里的 FireRedChat pVAD 插件资源。

```text
pVAD 插件包:
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/__init__.py

pVAD 资源目录:
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources

pVAD ONNX 模型:
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/pvad.onnx
```

### 说话人嵌入资源

这些文件随 `fireredchat-pvad` 资源一起使用，用于更新 pVAD 的说话人特征。

```text
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/spkrec-ecapa-voxceleb/hyperparams.yaml
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/spkrec-ecapa-voxceleb/embedding_model.ckpt
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/spkrec-ecapa-voxceleb/classifier.ckpt
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/spkrec-ecapa-voxceleb/mean_var_norm_emb.ckpt
/home/acir/Duplex_Model/third_party/fireredchat-agents/fireredchat-plugins/livekit-plugins-fireredchat-pvad/livekit/plugins/fireredchat_pvad/resources/spkrec-ecapa-voxceleb/label_encoder.ckpt
```

### ASR / SenseVoiceSmall

`resolve_modelscope_model_path("iic/SenseVoiceSmall", ...)` 在本机解析到下面这个 ModelScope 快照目录：

```text
ASR 快照目录:
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master

ASR 主模型:
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/model.pt

ASR 配置:
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/config.yaml
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/configuration.json

ASR tokenizer / 词表相关:
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/chn_jpn_yue_eng_ko_spectok.bpe.model
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/tokens.json

ASR 归一化参数:
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master/am.mvn
```

本机还存在一份 ModelScope 旧版 hub 布局缓存：

```text
/home/acir/.cache/modelscope/hub/models/iic/SenseVoiceSmall
```

但按当前项目的 `snapshot_download(..., local_files_only=True)` 解析结果，实际使用的是：

```text
/home/acir/.cache/modelscope/models/iic--SenseVoiceSmall/snapshots/master
```

### EOT / FireRedChat Turn Detector

```text
EOT ONNX 模型:
/home/acir/.cache/huggingface/hub/models--FireRedTeam--FireRedChat-turn-detector/snapshots/1a53b2145cdac39f247a8d55922630635aadfaef/chinese_best_model_q8.onnx
```

### EOT Tokenizer / multilingual BERT

```text
Tokenizer 快照目录:
/home/acir/.cache/huggingface/hub/models--google-bert--bert-base-multilingual-cased/snapshots/3f076fdb1ab68d5b2880cb87a0886f315b8146f8

Tokenizer 配置:
/home/acir/.cache/huggingface/hub/models--google-bert--bert-base-multilingual-cased/snapshots/3f076fdb1ab68d5b2880cb87a0886f315b8146f8/config.json
/home/acir/.cache/huggingface/hub/models--google-bert--bert-base-multilingual-cased/snapshots/3f076fdb1ab68d5b2880cb87a0886f315b8146f8/tokenizer_config.json

Tokenizer 文件:
/home/acir/.cache/huggingface/hub/models--google-bert--bert-base-multilingual-cased/snapshots/3f076fdb1ab68d5b2880cb87a0886f315b8146f8/tokenizer.json
/home/acir/.cache/huggingface/hub/models--google-bert--bert-base-multilingual-cased/snapshots/3f076fdb1ab68d5b2880cb87a0886f315b8146f8/vocab.txt
```

### LLM / Qwen Flash

`qwen-flash` 是 DashScope 远程 API 模型，本项目本地没有 `qwen-flash` 权重文件。项目本地只安装了 OpenAI 兼容 SDK，用它调用远程服务。

```text
OpenAI SDK:
/home/acir/anaconda3/envs/duplex_model/lib/python3.12/site-packages/openai/__init__.py

远程接口:
https://dashscope.aliyuncs.com/compatible-mode/v1

API Key 环境变量:
DASHSCOPE_API_KEY
```

### TTS / Kokoro

```text
Kokoro Python 包:
/home/acir/anaconda3/envs/duplex_model/lib/python3.12/site-packages/kokoro/__init__.py

Kokoro 快照目录:
/home/acir/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987

Kokoro 主模型:
/home/acir/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/kokoro-v1_0.pth

Kokoro 配置:
/home/acir/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/config.json

Kokoro 默认音色 zf_xiaoyi:
/home/acir/.cache/huggingface/hub/models--hexgrad--Kokoro-82M/snapshots/f3ff3571791e39611d31c381e3a41a3af07b4987/voices/zf_xiaoyi.pt
```

### 可选 easy_tts_server

`easy_tts_server` 是代码里保留的可选 TTS provider，但当前 `duplex_model` 环境未安装该包，默认配置也没有启用它，因此本机没有可确认的 `easy_tts_server` 模型路径。

## 组件细节

### AEC

AEC 不是神经网络模型，而是 LiveKit WebRTC APM 的音频处理模块。实时模式下，系统把当前播放给扬声器的 TTS 音频作为 far-end 信号送入 APM，再把麦克风输入作为 near-end 信号处理，输出 AEC 后的麦克风音频。

默认参数：

```json
"aec": {
  "enabled": true,
  "stream_delay_ms": 120,
  "frame_ms": 10,
  "latency": "high",
  "high_pass_filter": true,
  "noise_suppression": false,
  "auto_gain_control": false
}
```

### pVAD

pVAD 使用 FireRedChat 的 LiveKit 插件资源，核心模型为：

```text
FireRedTeam/fireredchat-pvad
  - pvad.onnx
  - spkrec-ecapa-voxceleb/*
```

项目通过 `pvad.load_vad(activation_threshold)` 加载模型。主链路默认阈值是 `0.5`，播放中打断检测使用更严格的 `0.75`。

### ASR

ASR 默认使用：

```text
iic/SenseVoiceSmall
```

代码通过 FunASR `AutoModel` 加载，设备默认为 `auto`，会优先使用 CUDA，否则使用 CPU。输入音频会被统一处理成 16 kHz、mono、float32。

默认配置：

```json
"asr": {
  "model": "iic/SenseVoiceSmall",
  "device": "auto"
}
```

### EOT

EOT 用来判断用户是否说完一轮话。默认模型为：

```text
repo_id: FireRedTeam/FireRedChat-turn-detector
model_file: chinese_best_model_q8.onnx
tokenizer: google-bert/bert-base-multilingual-cased
```

默认阈值是 `0.7`。ASR 文本送入 EOT 前会默认去掉末尾标点，避免 SenseVoice 自动补出的句号、逗号、问号影响结束判断。

### LLM

默认 LLM 是：

```text
provider: qwen
model: qwen-flash
base_url: https://dashscope.aliyuncs.com/compatible-mode/v1
api_key_env: DASHSCOPE_API_KEY
```

项目用 OpenAI Python SDK 访问 DashScope 兼容接口。系统提示要求中文自然回答、尽量简短、不要复述用户问题。

也支持 `llm.provider=fake`，此时 `FakeLLM` 会直接把用户文本原样返回，主要用于链路调试。

### TTS

默认 TTS 使用 Kokoro：

```text
repo_id: hexgrad/Kokoro-82M
voice: zf_xiaoyi
language: zh
lang_code: z
sample_rate: 24000
device: auto
```

项目会缓存 `KPipeline`，首次合成时加载 Kokoro 模型。合成后的 24 kHz 音频如果进入实时 AEC 播放链路，会重采样到系统主链路的 16 kHz。

代码中还保留了 `easy_tts_server` 作为可选 TTS provider，但默认配置没有使用它，具体模型取决于本地 `easy_tts_server` 的实现。

## 本地缓存策略

默认模型加载策略是只使用本地缓存：

```json
"model_loading": {
  "prefer_local_cache": true,
  "local_files_only": true
}
```

这意味着 ASR、EOT、TTS 默认不会自动联网下载模型。缺少缓存时会快速报错。需要补模型时，可以临时关闭 `local_files_only` 或按 README 中的命令下载 pVAD 资源。

## 打断检测中的模型复用

播放 TTS 时的人声打断仍然使用 FireRedChat pVAD，但它独立创建一个 `InterruptionGate`，使用 `interruption.vad_activation_threshold` 和 `interruption.min_speech_seconds` 判断是否是真人插话。确认打断后，系统停止当前 TTS，把打断音频重新送回主 `CascadeDuplexModel`，继续走 pVAD、ASR、EOT、LLM、TTS 链路。
