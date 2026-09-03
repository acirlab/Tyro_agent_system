from __future__ import annotations

import json
from dataclasses import dataclass, fields, is_dataclass
from pathlib import Path
from typing import Any


SAMPLE_RATE = 16000
DEFAULT_CONFIG_PATH = Path(__file__).resolve().parent.parent / "duplex_config.json"
DEFAULT_TUNING_CONFIG_PATH = Path(__file__).resolve().parent.parent / "tuning_config.jsonc"


@dataclass
class RuntimeConfig:
    max_turns: int = 0
    mock_asr_text: str | None = None
    no_tts: bool = False
    no_play: bool = False
    output: str | None = None
    quiet: bool = False
    debug_save_asr_audio_dir: str | None = None


@dataclass
class AudioConfig:
    sample_rate: int = SAMPLE_RATE
    chunk_seconds: float = 0.03


@dataclass
class ModelLoadingConfig:
    prefer_local_cache: bool = True
    local_files_only: bool = True
    huggingface_cache_dir: str | None = None
    modelscope_cache_dir: str | None = None


@dataclass
class AECConfig:
    enabled: bool = True
    stream_delay_ms: int = 120
    frame_ms: int = 10
    latency: str = "high"
    high_pass_filter: bool = True
    noise_suppression: bool = False
    auto_gain_control: bool = False


@dataclass
class InterruptionConfig:
    enabled: bool = True
    vad_activation_threshold: float = 0.75
    min_speech_seconds: float = 0.25
    max_interruption_seconds: float = 30.0


@dataclass
class ASRConfig:
    model: str = "iic/SenseVoiceSmall"
    device: str = "auto"


@dataclass
class PVADConfig:
    activation_threshold: float = 0.5
    min_speech_seconds: float = 0.2
    short_silence_seconds: float = 0.35
    extra_wait_seconds: float = 2.0
    pre_speech_padding_seconds: float = 0.4
    min_segment_seconds: float = 0.1
    speaker_embedding_min_seconds: float = 1.0
    update_speaker_embedding: bool = True


@dataclass
class EOTConfig:
    repo_id: str = "FireRedTeam/FireRedChat-turn-detector"
    model_file: str = "chinese_best_model_q8.onnx"
    tokenizer: str = "google-bert/bert-base-multilingual-cased"
    threshold: float = 0.7
    max_length: int = 128
    strip_trailing_punctuation: bool = True
    trailing_punctuation: str = "。！？!?，,；;：:、."


@dataclass
class LLMConfig:
    provider: str = "qwen"
    model: str = "qwen-flash"
    api_key_env: str = "DASHSCOPE_API_KEY"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    system_prompt: str = (
        "你是一个语音对话助手。请用中文自然回答，尽可能简短，通常不超过两句话。"
        "不要复述用户问题，直接回答。"
    )
    temperature: float = 0.3
    max_tokens: int = 256
    timeout_seconds: float = 20.0


@dataclass
class ResearchConfig:
    enabled: bool = True
    planner_model: str = "qwen3.7-plus"
    writer_model: str = "qwen3.7-plus"
    verifier_model: str = "qwen3.7-plus"
    api_key_env: str = "DASHSCOPE_API_KEY"
    base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1"
    writer_max_tokens: int = 8192
    timeout_seconds: float = 300.0
    use_llm_writer: bool = True
    embedding_model: str = "text-embedding-v4"
    rerank_model: str = "qwen3-rerank"
    use_embeddings: bool = True
    use_rerank: bool = True
    fetch_full_text: bool = True
    max_full_text_papers: int = 8
    max_search_queries: int = 10
    search_timeout_seconds: float = 90.0
    max_chunks_per_report: int = 120
    chunk_chars: int = 1800
    chunk_overlap: int = 240
    full_text_cache_dir: str = "research/cache/full_text"
    pipeline_timeout_seconds: float = 900.0
    writer_timeout_seconds: float = 600.0


@dataclass
class TTSConfig:
    provider: str = "kokoro"
    language: str = "zh"
    lang_code: str = "z"
    repo_id: str | None = "hexgrad/Kokoro-82M"
    voice: str = "zf_xiaoyi"
    speed: float = 1.0
    sample_rate: int = 24000
    device: str = "auto"


@dataclass
class ExpressionConfig:
    enabled: bool = True
    video_dir: str = "expression_video"
    default_expression: str = "neutral"
    display_width: int = 640
    display_height: int = 368
    keep_aspect_ratio: bool = True
    window_title: str = "Tyro Expression"
    choose_with_llm: bool = True
    reset_to_neutral_after_speech: bool = True


@dataclass
class AppConfig:
    runtime: RuntimeConfig
    audio: AudioConfig
    model_loading: ModelLoadingConfig
    aec: AECConfig
    interruption: InterruptionConfig
    asr: ASRConfig
    pvad: PVADConfig
    eot: EOTConfig
    llm: LLMConfig
    research: ResearchConfig
    tts: TTSConfig
    expression: ExpressionConfig


def _from_dict(cls: type, data: dict[str, Any]) -> Any:
    if not is_dataclass(cls):
        return cls(**data)
    allowed = {field.name for field in fields(cls)}
    return cls(**{key: value for key, value in data.items() if key in allowed})


def _read_json_if_exists(path: str | Path | None) -> dict[str, Any]:
    if path is None:
        return {}
    config_path = Path(path)
    if not config_path.exists():
        return {}
    return json.loads(_strip_json_comments(config_path.read_text(encoding="utf-8")))


def _strip_json_comments(text: str) -> str:
    output: list[str] = []
    index = 0
    in_string = False
    escape = False
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""

        if in_string:
            output.append(char)
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            index += 1
            continue

        if char == '"':
            in_string = True
            output.append(char)
            index += 1
            continue

        if char == "/" and next_char == "/":
            index += 2
            while index < len(text) and text[index] not in "\r\n":
                index += 1
            continue

        if char == "/" and next_char == "*":
            index += 2
            while index + 1 < len(text) and not (text[index] == "*" and text[index + 1] == "/"):
                index += 1
            index += 2
            continue

        output.append(char)
        index += 1
    return "".join(output)


def _deep_merge(base: dict[str, Any], overlay: dict[str, Any]) -> dict[str, Any]:
    merged = dict(base)
    for key, value in overlay.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = value
    return merged


def load_app_config(
    path: str | Path = DEFAULT_CONFIG_PATH,
    tuning_path: str | Path | None = DEFAULT_TUNING_CONFIG_PATH,
) -> AppConfig:
    data: dict[str, Any] = {}
    data = _deep_merge(data, _read_json_if_exists(path))
    data = _deep_merge(data, _read_json_if_exists(tuning_path))

    return AppConfig(
        runtime=_from_dict(RuntimeConfig, data.get("runtime", {})),
        audio=_from_dict(AudioConfig, data.get("audio", {})),
        model_loading=_from_dict(ModelLoadingConfig, data.get("model_loading", {})),
        aec=_from_dict(AECConfig, data.get("aec", {})),
        interruption=_from_dict(InterruptionConfig, data.get("interruption", {})),
        asr=_from_dict(ASRConfig, data.get("asr", {})),
        pvad=_from_dict(PVADConfig, data.get("pvad", {})),
        eot=_from_dict(EOTConfig, data.get("eot", {})),
        llm=_from_dict(LLMConfig, data.get("llm", {})),
        research=_from_dict(ResearchConfig, data.get("research", {})),
        tts=_from_dict(TTSConfig, data.get("tts", {})),
        expression=_from_dict(ExpressionConfig, data.get("expression", {})),
    )
