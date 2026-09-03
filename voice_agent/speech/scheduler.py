from __future__ import annotations

import asyncio
import itertools
from dataclasses import dataclass, field
from enum import IntEnum

import numpy as np


class SpeechPriority(IntEnum):
    PROGRESS = 10
    CHAT = 20
    FINAL = 30
    QUESTION = 40
    ERROR = 50


@dataclass(order=True)
class SpeechJob:
    sort_index: tuple[int, int] = field(init=False, repr=False)
    priority: int
    sequence: int
    text: str = field(compare=False)
    kind: str = field(default="speech", compare=False)

    def __post_init__(self) -> None:
        self.sort_index = (-int(self.priority), self.sequence)


class SpeechScheduler:
    def __init__(
        self,
        tts_runner,
        transport,
        no_tts: bool = False,
        no_play: bool = False,
        expression_controller=None,
        expression_selector=None,
        reset_expression_after_speech: bool = True,
    ) -> None:
        self.tts_runner = tts_runner
        self.transport = transport
        self.no_tts = no_tts
        self.no_play = no_play
        self.expression_controller = expression_controller
        self.expression_selector = expression_selector
        self.reset_expression_after_speech = reset_expression_after_speech
        self.queue: asyncio.PriorityQueue[SpeechJob] = asyncio.PriorityQueue()
        self._sequence = itertools.count()
        self._worker: asyncio.Task | None = None
        self._current_task: asyncio.Task | None = None
        self._interrupted = asyncio.Event()
        self._last_progress: str | None = None
        self.spoken_texts: list[str] = []

    @property
    def is_playing(self) -> bool:
        return self._current_task is not None and not self._current_task.done()

    def start(self) -> None:
        if self.expression_controller is not None:
            self.expression_controller.start()
        if self._worker is None:
            self._worker = asyncio.create_task(self._run())

    async def stop(self) -> None:
        await self.interrupt()
        if self._worker is not None:
            self._worker.cancel()
            try:
                await self._worker
            except asyncio.CancelledError:
                pass
            self._worker = None
        if self.expression_controller is not None:
            await self.expression_controller.stop()

    async def say(self, text: str, priority: int = SpeechPriority.CHAT, kind: str = "speech") -> None:
        text = text.strip()
        if not text:
            return
        if kind != "progress" and priority >= SpeechPriority.CHAT:
            self._drop_queued_progress()
        await self.queue.put(SpeechJob(priority=int(priority), sequence=next(self._sequence), text=text, kind=kind))

    async def replace_progress(self, text: str) -> None:
        text = text.strip()
        if not text or text == self._last_progress:
            return
        self._last_progress = text
        retained: list[SpeechJob] = []
        while not self.queue.empty():
            job = self.queue.get_nowait()
            if job.kind != "progress":
                retained.append(job)
        for job in retained:
            await self.queue.put(job)
        await self.say(text, SpeechPriority.PROGRESS, kind="progress")

    async def interrupt(self) -> None:
        # Speech interruption only stops the current spoken output and clears
        # queued speaker audio. It deliberately does not cancel Agent tasks.
        self._interrupted.set()
        if self._current_task is not None:
            self._current_task.cancel()
        await self.transport.clear_playback()

    async def _run(self) -> None:
        while True:
            job = await self.queue.get()
            self._interrupted.clear()
            self._current_task = asyncio.create_task(self._speak(job.text, job.kind))
            try:
                await self._current_task
            except asyncio.CancelledError:
                if asyncio.current_task() and asyncio.current_task().cancelling():
                    raise
                pass
            finally:
                self._current_task = None

    async def _speak(self, text: str, kind: str) -> None:
        self.spoken_texts.append(text)
        print(f"ASSISTANT: {text}")
        await self._set_expression_for_speech(text, kind)
        try:
            if self.no_tts or self.tts_runner is None:
                return
            chunks, sample_rate = await self.tts_runner.synthesize(text)
            if self.no_play:
                return
            for chunk in chunks:
                if self._interrupted.is_set():
                    return
                await self.transport.play_frame(np.asarray(chunk, dtype=np.float32), sample_rate)
            wait_for_playback = getattr(self.transport, "wait_for_playback", None)
            if wait_for_playback is not None:
                await wait_for_playback()
        finally:
            if (
                self.expression_controller is not None
                and self.reset_expression_after_speech
                and kind != "progress"
            ):
                await self.expression_controller.reset_to_default()

    async def _set_expression_for_speech(self, text: str, kind: str) -> None:
        if self.expression_controller is None or self.expression_selector is None:
            return
        expression = await self.expression_selector.select(text, kind)
        await self.expression_controller.set_expression_async(expression)

    def _drop_queued_progress(self) -> None:
        retained: list[SpeechJob] = []
        while not self.queue.empty():
            job = self.queue.get_nowait()
            if job.kind != "progress":
                retained.append(job)
        for job in retained:
            self.queue.put_nowait(job)
