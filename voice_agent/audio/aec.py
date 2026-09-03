from __future__ import annotations

import numpy as np

from voice_agent.config import AECConfig, SAMPLE_RATE


def float_to_int16(audio: np.ndarray) -> np.ndarray:
    return (np.clip(audio, -1.0, 1.0) * np.iinfo(np.int16).max).astype(np.int16)


def int16_to_float(audio: np.ndarray) -> np.ndarray:
    return np.asarray(audio, dtype=np.float32) / np.iinfo(np.int16).max


def resample_audio(audio: np.ndarray, source_rate: int, target_rate: int) -> np.ndarray:
    audio = np.asarray(audio, dtype=np.float32).flatten()
    if source_rate == target_rate or len(audio) == 0:
        return audio
    old_index = np.linspace(0, 1, num=len(audio), endpoint=False)
    new_length = int(round(len(audio) * target_rate / source_rate))
    new_index = np.linspace(0, 1, num=new_length, endpoint=False)
    return np.interp(new_index, old_index, audio).astype(np.float32)


class WebRTCAEC:
    def __init__(self, config: AECConfig, sample_rate: int = SAMPLE_RATE) -> None:
        from livekit import rtc
        from livekit.rtc.apm import AudioProcessingModule

        self.rtc = rtc
        self.sample_rate = sample_rate
        self.apm = AudioProcessingModule(
            echo_cancellation=True,
            noise_suppression=config.noise_suppression,
            high_pass_filter=config.high_pass_filter,
            auto_gain_control=config.auto_gain_control,
        )
        self.apm.set_stream_delay_ms(config.stream_delay_ms)

    def process(self, near: np.ndarray, far: np.ndarray) -> np.ndarray:
        far_frame = self._make_frame(np.asarray(far, dtype=np.int16))
        near_frame = self._make_frame(np.asarray(near, dtype=np.int16))
        self.apm.process_reverse_stream(far_frame)
        self.apm.process_stream(near_frame)
        return np.asarray(near_frame.data, dtype=np.int16).copy()

    def _make_frame(self, samples: np.ndarray):
        return self.rtc.AudioFrame(
            data=bytearray(np.asarray(samples, dtype=np.int16).tobytes()),
            sample_rate=self.sample_rate,
            num_channels=1,
            samples_per_channel=len(samples),
        )

