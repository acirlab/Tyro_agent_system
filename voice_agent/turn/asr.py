from __future__ import annotations

import asyncio
import re

import numpy as np

from voice_agent.config import ASRConfig, ModelLoadingConfig, SAMPLE_RATE
from voice_agent.model_loading import (
    fix_unsupported_socks_proxy,
    resolve_device,
    resolve_modelscope_model_path,
)


SENSEVOICE_TAG_RE = re.compile(r"<\|[^|]+?\|>")


def prepare_audio(audio_data: np.ndarray, sample_rate: int) -> np.ndarray:
    audio = np.asarray(audio_data)
    source_dtype = audio.dtype
    if audio.ndim > 1:
        audio = audio.mean(axis=1)
    audio = audio.astype(np.float32).flatten()
    if np.issubdtype(source_dtype, np.integer):
        audio = audio / np.iinfo(source_dtype).max
    if sample_rate != SAMPLE_RATE and len(audio) > 0:
        old_index = np.linspace(0, 1, num=len(audio), endpoint=False)
        new_length = int(len(audio) * SAMPLE_RATE / sample_rate)
        new_index = np.linspace(0, 1, num=new_length, endpoint=False)
        audio = np.interp(new_index, old_index, audio).astype(np.float32)
    return audio


def read_audio_file(path: str) -> np.ndarray:
    import soundfile as sf

    audio_data, sample_rate = sf.read(path)
    return prepare_audio(audio_data, sample_rate)


class ASRRunner:
    def __init__(
        self,
        config: ASRConfig,
        model_loading: ModelLoadingConfig,
        mock_text: str | None = None,
    ) -> None:
        self.mock_text = mock_text
        self.model = None
        if mock_text is not None:
            return

        fix_unsupported_socks_proxy()
        from funasr import AutoModel

        device = resolve_device(config.device)
        model_path = resolve_modelscope_model_path(config.model, model_loading)
        self.model = AutoModel(
            model=model_path,
            device=device,
            disable_update=True,
            check_latest=False,
        )

    def transcribe_sync(self, audio_data: np.ndarray) -> str:
        if self.mock_text is not None:
            return self.mock_text
        if self.model is None:
            raise RuntimeError("ASR model is not loaded.")

        audio_input = np.asarray(audio_data).flatten().astype(np.float32)
        if len(audio_input) < int(0.1 * SAMPLE_RATE):
            return ""

        result = self.model.generate(
            input=audio_input,
            cache={},
            language="auto",
            use_itn=True,
        )
        if result and len(result) > 0:
            return SENSEVOICE_TAG_RE.sub("", result[0].get("text", "")).strip()
        return ""

    async def transcribe(self, audio_data: np.ndarray) -> str:
        return await asyncio.to_thread(self.transcribe_sync, audio_data)

