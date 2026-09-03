from __future__ import annotations

import asyncio
from collections import deque
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import numpy as np

from voice_agent.config import PVADConfig, SAMPLE_RATE
from voice_agent.turn.asr import ASRRunner
from voice_agent.turn.eot import EOTPrediction
from voice_agent.turn.vad import WindowedPVAD


class TurnState(str, Enum):
    IDLE = "idle"
    SPEECH = "speech"
    EXTRA_WAIT = "extra_wait"


@dataclass(frozen=True)
class UserTurn:
    text: str
    audio: bytes
    eot_probability: float
    finish_reason: str


class UserTurnEngine:
    def __init__(self, config: PVADConfig, asr_runner: ASRRunner, eot_detector) -> None:
        self.config = config
        self.asr_runner = asr_runner
        self.eot_detector = eot_detector
        self.vad = WindowedPVAD(config.activation_threshold)
        self.completed_turns: asyncio.Queue[UserTurn] = asyncio.Queue()
        self.total_samples_processed = 0
        self.asr_segment_index = 0
        self.debug_save_asr_audio_dir: str | None = None
        self.reset_turn()

    async def push_audio(self, frame: np.ndarray) -> None:
        for window in self.vad.iter_windows(frame):
            start_sample = self.total_samples_processed
            turn = await self._handle_window(window, start_sample)
            self.total_samples_processed += len(window)
            if turn is not None:
                await self.completed_turns.put(turn)

    async def inject_audio(self, frames: list[np.ndarray]) -> None:
        for frame in frames:
            await self.push_audio(frame)

    async def get_completed_turn(self) -> UserTurn:
        return await self.completed_turns.get()

    async def finish_stream(self) -> UserTurn | None:
        if self.state == TurnState.SPEECH and self.audio_buffer:
            await self._run_asr_on_current_segment()
        if self.accumulated_text:
            return self._finalize("stream_end")
        self.reset_turn()
        return None

    def reset_turn(self) -> None:
        self.vad.reset()
        self.state = TurnState.IDLE
        self.audio_buffer: list[np.ndarray] = []
        self.turn_audio_buffer: list[np.ndarray] = []
        self.turn_audio_start_sample: int | None = None
        self.pre_speech_max_windows = max(
            0,
            int(round(self.config.pre_speech_padding_seconds / self.vad.window_seconds)),
        )
        self.pre_speech_buffer: deque[tuple[int, np.ndarray]] = deque(
            maxlen=self.pre_speech_max_windows
        )
        self.audio_buffer_start_sample: int | None = None
        self.detected_speech_start_sample: int | None = None
        self.accumulated_text = ""
        self.last_eot_prediction = EOTPrediction(text="", probability=0.0, is_end=False)
        self.silence_seconds = 0.0
        self.extra_wait_seconds = 0.0
        self.pending_speech_buffer: list[tuple[int, np.ndarray]] = []
        self.pending_speech_seconds = 0.0
        self.speaker_embedding_updated = False

    async def _handle_window(self, window: np.ndarray, start_sample: int) -> UserTurn | None:
        probability = self.vad.probability(window)
        has_speech = probability >= self.config.activation_threshold

        if self.state == TurnState.IDLE:
            if has_speech:
                self._append_pending_speech(window, start_sample)
                if self._pending_speech_confirmed():
                    self._start_audio_buffer_from_pending()
                    self.state = TurnState.SPEECH
                    self.silence_seconds = 0.0
            else:
                self._reset_pending_speech()
                self._remember_pre_speech_window(window, start_sample)
            return None

        if self.state == TurnState.SPEECH:
            self.audio_buffer.append(window.copy())
            self.silence_seconds = 0.0 if has_speech else self.silence_seconds + self.vad.window_seconds
            if self.silence_seconds >= self.config.short_silence_seconds:
                segment_text = await self._run_asr_on_current_segment()
                if segment_text:
                    prediction = await self.eot_detector.predict(self.accumulated_text)
                    self.last_eot_prediction = prediction
                    if prediction.is_end:
                        return self._finalize("eot_high")
                self.state = TurnState.EXTRA_WAIT
                self.extra_wait_seconds = 0.0
                self.silence_seconds = 0.0
            return None

        if self.state == TurnState.EXTRA_WAIT:
            if has_speech:
                self._append_pending_speech(window, start_sample)
                if self._pending_speech_confirmed():
                    self._start_audio_buffer_from_pending()
                    self.state = TurnState.SPEECH
                    self.extra_wait_seconds = 0.0
                    self.silence_seconds = 0.0
                return None

            self._reset_pending_speech()
            self._append_turn_audio(window, start_sample)
            self._remember_pre_speech_window(window, start_sample)
            self.extra_wait_seconds += self.vad.window_seconds
            if self.extra_wait_seconds >= self.config.extra_wait_seconds:
                if self.accumulated_text:
                    return self._finalize("extra_wait_timeout")
                self.reset_turn()
            return None

        return None

    def _append_pending_speech(self, window: np.ndarray, start_sample: int) -> None:
        self.pending_speech_buffer.append((start_sample, window.copy()))
        self.pending_speech_seconds += self.vad.window_seconds

    def _pending_speech_confirmed(self) -> bool:
        return self.pending_speech_seconds >= max(0.0, self.config.min_speech_seconds)

    def _reset_pending_speech(self) -> None:
        self.pending_speech_buffer = []
        self.pending_speech_seconds = 0.0

    def _start_audio_buffer_from_pending(self) -> None:
        if not self.pending_speech_buffer:
            return

        if self.turn_audio_buffer:
            prefix_windows: list[tuple[int, np.ndarray]] = []
        else:
            prefix_windows = list(self.pre_speech_buffer)

        all_windows = prefix_windows + self.pending_speech_buffer
        self.audio_buffer_start_sample = all_windows[0][0]
        self.detected_speech_start_sample = self.pending_speech_buffer[0][0]
        self.audio_buffer = [buffered.copy() for _start, buffered in all_windows]
        self.pre_speech_buffer.clear()
        self._reset_pending_speech()

    def _start_audio_buffer(self, window: np.ndarray, start_sample: int) -> None:
        if self.turn_audio_buffer:
            self.audio_buffer_start_sample = start_sample
            self.detected_speech_start_sample = start_sample
            self.audio_buffer = [window.copy()]
            self.pre_speech_buffer.clear()
            return

        prefix_windows = list(self.pre_speech_buffer)
        self.pre_speech_buffer.clear()
        if prefix_windows:
            self.audio_buffer_start_sample = prefix_windows[0][0]
            self.detected_speech_start_sample = start_sample
            self.audio_buffer = [buffered.copy() for _start, buffered in prefix_windows]
            self.audio_buffer.append(window.copy())
            return

        self.audio_buffer_start_sample = start_sample
        self.detected_speech_start_sample = start_sample
        self.audio_buffer = [window.copy()]

    def _remember_pre_speech_window(self, window: np.ndarray, start_sample: int) -> None:
        if self.pre_speech_max_windows > 0:
            self.pre_speech_buffer.append((start_sample, window.copy()))

    def _append_turn_audio(self, audio_data: np.ndarray, start_sample: int) -> None:
        if self.turn_audio_start_sample is None:
            self.turn_audio_start_sample = start_sample
        self.turn_audio_buffer.append(audio_data.copy())

    async def _run_asr_on_current_segment(self) -> str:
        if not self.audio_buffer:
            return ""

        audio_data = np.concatenate(self.audio_buffer).astype(np.float32)
        start_sample = self.audio_buffer_start_sample
        self.audio_buffer = []
        self.audio_buffer_start_sample = None
        self.detected_speech_start_sample = None
        if len(audio_data) < int(self.config.min_segment_seconds * SAMPLE_RATE):
            return ""

        if start_sample is None:
            start_sample = max(0, self.total_samples_processed - len(audio_data))
        self._append_turn_audio(audio_data, start_sample)
        full_audio = np.concatenate(self.turn_audio_buffer).astype(np.float32)
        self._save_asr_audio_segment(full_audio, self.asr_segment_index)
        self.asr_segment_index += 1
        self._update_speaker_embedding(audio_data)

        text = (await self.asr_runner.transcribe(full_audio)).strip()
        if text:
            self.accumulated_text = text
        return text

    def _update_speaker_embedding(self, audio_data: np.ndarray) -> None:
        if (
            not self.config.update_speaker_embedding
            or self.speaker_embedding_updated
            or len(audio_data) < int(self.config.speaker_embedding_min_seconds * SAMPLE_RATE)
        ):
            return
        self.vad.update_speaker(audio_data)
        self.speaker_embedding_updated = True

    def _finalize(self, reason: str) -> UserTurn:
        text = self.accumulated_text.strip()
        audio = np.concatenate(self.turn_audio_buffer).astype(np.float32) if self.turn_audio_buffer else np.empty(0)
        turn = UserTurn(
            text=text,
            audio=audio.tobytes(),
            eot_probability=self.last_eot_prediction.probability,
            finish_reason=reason,
        )
        self.reset_turn()
        return turn

    def _save_asr_audio_segment(self, audio_data: np.ndarray, segment_index: int) -> None:
        if not self.debug_save_asr_audio_dir:
            return
        import soundfile as sf

        output_dir = Path(self.debug_save_asr_audio_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        sf.write(output_dir / f"asr_segment_{segment_index:04d}.wav", audio_data, SAMPLE_RATE)
