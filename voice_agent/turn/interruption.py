from __future__ import annotations

from collections import deque

import numpy as np

from voice_agent.config import InterruptionConfig, PVADConfig
from voice_agent.turn.engine import UserTurnEngine
from voice_agent.turn.vad import WindowedPVAD


class InterruptionController:
    """Detects real user speech while the assistant is speaking.

    This controller only handles speech interruption. It intentionally does not
    cancel Agent tasks; task cancellation is handled by ConversationController
    after the user's interrupted turn is transcribed and classified.
    """

    def __init__(
        self,
        config: InterruptionConfig,
        turn_config: PVADConfig,
        turn_engine: UserTurnEngine,
        speech_scheduler,
    ) -> None:
        self.config = config
        self.turn_config = turn_config
        self.turn_engine = turn_engine
        self.speech_scheduler = speech_scheduler
        # Use a separate pVAD instance and a higher threshold for interruption,
        # so speaker echo or short noise is less likely to stop playback.
        self.vad = WindowedPVAD(config.vad_activation_threshold)
        max_prefix_windows = max(
            0,
            int(round(turn_config.pre_speech_padding_seconds / self.vad.window_seconds)),
        )
        # Keeps a small amount of audio before confirmed speech, so the first
        # syllable is not clipped when the interrupted turn is sent back.
        self.pre_speech_buffer: deque[np.ndarray] = deque(maxlen=max_prefix_windows)
        self.candidate_chunks: list[np.ndarray] = []
        self.consecutive_speech_seconds = 0.0
        self.silence_seconds = 0.0

    async def on_audio(self, frame: np.ndarray) -> bool:
        # Interruption detection is only meaningful while assistant speech is
        # actively playing. Outside playback, the normal UserTurnEngine handles
        # microphone audio.
        if not self.config.enabled or not self.speech_scheduler.is_playing:
            self.reset()
            return False

        for window in self.vad.iter_windows(frame):
            confirmed = await self._process_window(window)
            if confirmed:
                return True
        return False

    async def interrupt_speech(self) -> None:
        # Stop the current spoken response immediately. Background tools and
        # Agent tasks keep running unless the next user turn explicitly cancels.
        await self.speech_scheduler.interrupt()

    async def cancel_task(self) -> None:
        # Kept as a separate API boundary for future explicit task cancellation.
        # Today it only stops speech; AgentRuntime.cancel_task handles task state.
        await self.speech_scheduler.interrupt()

    def reset(self) -> None:
        self.vad.reset()
        self.pre_speech_buffer.clear()
        self.candidate_chunks = []
        self.consecutive_speech_seconds = 0.0
        self.silence_seconds = 0.0

    async def _process_window(self, window: np.ndarray) -> bool:
        probability = self.vad.probability(window)
        has_speech = probability >= self.config.vad_activation_threshold

        if has_speech:
            if not self.candidate_chunks:
                # First speech window in a possible interruption. Attach the
                # pre-speech padding collected before the VAD crossed threshold.
                self.candidate_chunks = [item.copy() for item in self.pre_speech_buffer]
                self.pre_speech_buffer.clear()
            self.candidate_chunks.append(window.copy())
            self.consecutive_speech_seconds += self.vad.window_seconds
            self.silence_seconds = 0.0
            if self.consecutive_speech_seconds >= self.config.min_speech_seconds:
                # Confirmed as real user speech: stop playback, then inject the
                # captured audio into the normal turn engine for ASR/EOT.
                frames = [item.copy() for item in self.candidate_chunks]
                self.reset()
                await self.interrupt_speech()
                await self.turn_engine.inject_audio(frames)
                return True
            return False

        if self.candidate_chunks:
            # A short speech-like blip that did not last long enough is allowed
            # to expire after enough silence, so accidental sounds are ignored.
            self.candidate_chunks.append(window.copy())
            self.consecutive_speech_seconds = 0.0
            self.silence_seconds += self.vad.window_seconds
            if self.silence_seconds >= self.turn_config.short_silence_seconds:
                self.reset()
            return False

        self.pre_speech_buffer.append(window.copy())
        return False
