from __future__ import annotations

import numpy as np

from voice_agent.audio.transport import SoundDeviceAudioTransport
from voice_agent.config import AECConfig, AudioConfig
from voice_agent.turn.asr import read_audio_file


def read_file_chunks(path: str, chunk_seconds: float) -> list[np.ndarray]:
    audio_data = read_audio_file(path)
    chunk_samples = max(160, int(chunk_seconds * 16000))
    return [audio_data[start : start + chunk_samples] for start in range(0, len(audio_data), chunk_samples)]


def build_audio_transport(audio_config: AudioConfig, aec_config: AECConfig) -> SoundDeviceAudioTransport:
    return SoundDeviceAudioTransport(audio_config, aec_config)

