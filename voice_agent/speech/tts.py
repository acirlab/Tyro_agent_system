from __future__ import annotations

import asyncio

import numpy as np

from voice_agent.config import ModelLoadingConfig, TTSConfig
from voice_agent.model_loading import resolve_device, resolve_hf_file


def kokoro_lang_code(language: str | None, lang_code: str) -> str:
    if language is not None:
        normalized = language.strip().lower()
        return "z" if normalized in {"zh", "cn", "chinese", "z"} else "a"
    normalized = str(lang_code).strip().lower()
    if normalized in {"zh", "z"}:
        return "z"
    if normalized in {"en", "a"}:
        return "a"
    return normalized or "z"


def load_local_kokoro_model(repo_id: str, model_loading: ModelLoadingConfig, device: str):
    from kokoro.model import KModel

    model_filename = KModel.MODEL_NAMES.get(repo_id)
    if model_filename is None:
        if model_loading.local_files_only:
            raise RuntimeError(f"Unsupported Kokoro repo_id for local loading: {repo_id}")
        return None
    config_path = resolve_hf_file(repo_id, "config.json", model_loading, "Kokoro config")
    model_path = resolve_hf_file(repo_id, model_filename, model_loading, "Kokoro model")
    if config_path is None or model_path is None:
        return None
    return KModel(repo_id=repo_id, config=config_path, model=model_path).to(device).eval()


def resolve_kokoro_voice(voice: str, repo_id: str, model_loading: ModelLoadingConfig) -> str:
    if not model_loading.prefer_local_cache or voice.endswith(".pt"):
        return voice
    paths = []
    for voice_name in voice.split(","):
        voice_name = voice_name.strip()
        if not voice_name:
            continue
        voice_path = resolve_hf_file(repo_id, f"voices/{voice_name}.pt", model_loading, "Kokoro voice")
        paths.append(voice_path or voice_name)
    return ",".join(paths) if paths else voice


class TTSRunner:
    def __init__(self, config: TTSConfig, model_loading: ModelLoadingConfig) -> None:
        self.config = config
        self.model_loading = model_loading
        self.device = resolve_device(config.device)
        self._kokoro_pipeline = None

    def synthesize_sync(self, text: str) -> tuple[list[np.ndarray], int]:
        provider = self.config.provider.strip().lower()
        if provider == "fake":
            return [np.zeros(int(0.08 * self.config.sample_rate), dtype=np.float32)], self.config.sample_rate
        if provider == "kokoro":
            from kokoro import KPipeline

            if self._kokoro_pipeline is None:
                local_model = None
                if self.config.repo_id and self.model_loading.prefer_local_cache:
                    local_model = load_local_kokoro_model(self.config.repo_id, self.model_loading, self.device)
                self._kokoro_pipeline = KPipeline(
                    lang_code=kokoro_lang_code(self.config.language, self.config.lang_code),
                    repo_id=self.config.repo_id,
                    model=local_model if local_model is not None else True,
                    device=self.device,
                )
            voice = self.config.voice
            if self.config.repo_id:
                voice = resolve_kokoro_voice(voice, self.config.repo_id, self.model_loading)
            chunks = []
            for _gs, _ps, audio in self._kokoro_pipeline(text, voice=voice, speed=self.config.speed):
                chunks.append(np.asarray(audio, dtype=np.float32))
            return chunks, self.config.sample_rate

        raise ValueError(f"Unsupported TTS provider: {self.config.provider}")

    async def synthesize(self, text: str) -> tuple[list[np.ndarray], int]:
        return await asyncio.to_thread(self.synthesize_sync, text)

