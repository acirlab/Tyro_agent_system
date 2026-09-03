from __future__ import annotations

import asyncio
import queue
import threading
from collections.abc import AsyncIterator
from typing import Protocol

import numpy as np

from voice_agent.audio.aec import WebRTCAEC, float_to_int16, int16_to_float, resample_audio
from voice_agent.config import AECConfig, AudioConfig


class AudioTransport(Protocol):
    async def read_frames(self) -> AsyncIterator[np.ndarray]:
        """Continuously read microphone frames as 16 kHz mono float32 audio."""

    async def play_frame(self, frame: np.ndarray, sample_rate: int | None = None) -> None:
        """Queue one frame for speaker playback."""

    async def clear_playback(self) -> None:
        """Immediately stop current playback."""


class NullAudioTransport:
    def __init__(self) -> None:
        self.played: list[np.ndarray] = []
        self.is_playing = False

    async def read_frames(self) -> AsyncIterator[np.ndarray]:
        while False:
            yield np.empty(0, dtype=np.float32)

    async def play_frame(self, frame: np.ndarray, sample_rate: int | None = None) -> None:
        self.played.append(np.asarray(frame, dtype=np.float32).copy())

    async def clear_playback(self) -> None:
        self.played.clear()
        self.is_playing = False


class SoundDeviceAudioTransport:
    def __init__(self, audio_config: AudioConfig, aec_config: AECConfig) -> None:
        import sounddevice as sd

        self.sd = sd
        self.audio_config = audio_config
        self.aec_config = aec_config
        self.sample_rate = audio_config.sample_rate
        self.frame_samples = int(round(self.sample_rate * aec_config.frame_ms / 1000))
        self.aec = WebRTCAEC(aec_config, self.sample_rate) if aec_config.enabled else None
        self._mic_queue: queue.Queue[np.ndarray] = queue.Queue(maxsize=400)
        self._lock = threading.Condition()
        self._playback_buffer = np.empty(0, dtype=np.int16)
        self._closed = False
        self.status_messages: list[str] = []
        self.stream = self.sd.Stream(
            samplerate=self.sample_rate,
            blocksize=self.frame_samples,
            dtype="int16",
            channels=1,
            latency=aec_config.latency,
            callback=self._callback,
        )

    @property
    def is_playing(self) -> bool:
        with self._lock:
            return len(self._playback_buffer) > 0

    def start(self) -> None:
        self.stream.start()

    def close(self) -> None:
        self._closed = True
        with self._lock:
            self._lock.notify_all()
        self.stream.stop()
        self.stream.close()

    async def read_frames(self) -> AsyncIterator[np.ndarray]:
        while not self._closed:
            chunk = await asyncio.to_thread(self._mic_queue.get)
            yield chunk

    async def play_frame(self, frame: np.ndarray, sample_rate: int | None = None) -> None:
        sample_rate = sample_rate or self.sample_rate
        audio = resample_audio(np.asarray(frame, dtype=np.float32), sample_rate, self.sample_rate)
        playback = float_to_int16(audio)
        with self._lock:
            self._playback_buffer = np.concatenate([self._playback_buffer, playback])
            self._lock.notify_all()

    async def clear_playback(self) -> None:
        with self._lock:
            self._playback_buffer = np.empty(0, dtype=np.int16)

    async def wait_for_playback(self) -> None:
        while self.is_playing:
            await asyncio.sleep(0.02)
        await asyncio.sleep(max(0.05, self.aec_config.stream_delay_ms / 1000))

    def _callback(self, indata, outdata, frames, _time_info, status) -> None:
        if status:
            self.status_messages.append(str(status))
        if frames != self.frame_samples:
            raise self.sd.CallbackAbort(f"Expected {self.frame_samples} frames, got {frames}")

        with self._lock:
            take = min(frames, len(self._playback_buffer))
            far_block = np.zeros(frames, dtype=np.int16)
            if take:
                far_block[:take] = self._playback_buffer[:take]
                self._playback_buffer = self._playback_buffer[take:]

        outdata[:, 0] = far_block
        raw_block = np.asarray(indata[:, 0], dtype=np.int16).copy()
        processed = self.aec.process(raw_block, far_block) if self.aec is not None else raw_block
        self._put_mic_chunk(int16_to_float(processed))

    def _put_mic_chunk(self, chunk: np.ndarray) -> None:
        try:
            self._mic_queue.put_nowait(chunk)
        except queue.Full:
            try:
                self._mic_queue.get_nowait()
            except queue.Empty:
                pass
            self._mic_queue.put_nowait(chunk)

