from __future__ import annotations

import asyncio
import os
import queue
import threading
import time
from dataclasses import dataclass
from pathlib import Path

from voice_agent.config import ExpressionConfig


VIDEO_SUFFIXES = {".mp4", ".mov", ".mkv", ".webm", ".avi"}


@dataclass(frozen=True)
class _SetExpressionCommand:
    expression: str
    path: Path


@dataclass(frozen=True)
class _StopCommand:
    pass


class ExpressionVideoController:
    def __init__(self, config: ExpressionConfig, project_root: Path | None = None) -> None:
        self.config = config
        self.project_root = project_root or Path(__file__).resolve().parents[2]
        self.video_dir = self._resolve_video_dir(config.video_dir)
        self.videos = self._scan_videos()
        self.current_expression: str | None = None
        self._window: _TkAvVideoWindow | None = None
        self._disabled_reason: str | None = None

    @property
    def enabled(self) -> bool:
        return self.config.enabled and self._disabled_reason is None

    @property
    def available_expressions(self) -> list[str]:
        return sorted(self.videos)

    def start(self) -> None:
        if not self.config.enabled:
            return
        self._disabled_reason = self._validate()
        if self._disabled_reason is not None:
            print(f"Expression video disabled: {self._disabled_reason}")
            return
        self._window = _TkAvVideoWindow(
            title=self.config.window_title,
            display_size=(self.config.display_width, self.config.display_height),
            keep_aspect_ratio=self.config.keep_aspect_ratio,
        )
        self._window.start()
        self.set_expression(self.config.default_expression)

    def set_expression(self, expression: str) -> None:
        if not self.enabled:
            return
        normalized = self.normalize_expression(expression)
        if normalized == self.current_expression:
            return
        path = self.videos.get(normalized)
        if path is None:
            normalized = self.config.default_expression
            path = self.videos.get(normalized)
        if path is None:
            return

        if self._window is None:
            self._window = _TkAvVideoWindow(
                title=self.config.window_title,
                display_size=(self.config.display_width, self.config.display_height),
                keep_aspect_ratio=self.config.keep_aspect_ratio,
            )
            self._window.start()
        self._window.set_expression(normalized, path)
        self.current_expression = normalized

    async def set_expression_async(self, expression: str) -> None:
        await asyncio.to_thread(self.set_expression, expression)

    async def reset_to_default(self) -> None:
        await self.set_expression_async(self.config.default_expression)

    async def stop(self) -> None:
        window = self._window
        self._window = None
        self.current_expression = None
        if window is not None:
            await asyncio.to_thread(window.stop)

    def normalize_expression(self, expression: str) -> str:
        normalized = expression.strip().lower().replace("-", "_").replace(" ", "_")
        return normalized if normalized in self.videos else self.config.default_expression

    def _resolve_video_dir(self, video_dir: str) -> Path:
        path = Path(video_dir)
        if path.is_absolute():
            return path
        return self.project_root / path

    def _scan_videos(self) -> dict[str, Path]:
        if not self.video_dir.exists():
            return {}
        return {
            path.stem.lower().replace("-", "_").replace(" ", "_"): path
            for path in self.video_dir.iterdir()
            if path.is_file() and path.suffix.lower() in VIDEO_SUFFIXES
        }

    def _validate(self) -> str | None:
        if not self.video_dir.exists():
            return f"video directory not found: {self.video_dir}"
        if self.config.default_expression not in self.videos:
            return f"default expression video not found: {self.config.default_expression}"
        if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
            return "no DISPLAY/WAYLAND_DISPLAY found"
        try:
            import av  # noqa: F401
            import tkinter  # noqa: F401
            from PIL import ImageTk  # noqa: F401
        except Exception as exc:
            return f"fixed-window video dependencies unavailable: {exc}"
        return None


class _TkAvVideoWindow:
    def __init__(self, title: str, display_size: tuple[int, int], keep_aspect_ratio: bool) -> None:
        self.title = title
        self.display_size = display_size
        self.keep_aspect_ratio = keep_aspect_ratio
        self._commands: queue.Queue[_SetExpressionCommand | _StopCommand] = queue.Queue()
        self._thread = threading.Thread(target=self._run, name="expression-video", daemon=True)
        self._started = False

    def start(self) -> None:
        if self._started:
            return
        self._started = True
        self._thread.start()

    def set_expression(self, expression: str, path: Path) -> None:
        self._commands.put(_SetExpressionCommand(expression=expression, path=path))

    def stop(self) -> None:
        self._commands.put(_StopCommand())
        if self._started and self._thread.is_alive():
            self._thread.join(timeout=3)

    def _run(self) -> None:
        import av
        import tkinter as tk
        from PIL import ImageTk
        from PIL import Image

        root = tk.Tk()
        root.title(self.title)
        root.configure(background="black")
        root.geometry(f"{self.display_size[0]}x{self.display_size[1]}")
        root.minsize(self.display_size[0], self.display_size[1])
        root.maxsize(self.display_size[0], self.display_size[1])
        label = tk.Label(root, background="black", borderwidth=0, highlightthickness=0)
        label.pack(fill=tk.BOTH, expand=True)
        root.protocol("WM_DELETE_WINDOW", lambda: self._commands.put(_StopCommand()))

        current: _SetExpressionCommand | None = None
        stopped = False

        while not stopped:
            command = self._next_command(block=current is None)
            if isinstance(command, _StopCommand):
                stopped = True
                break
            if isinstance(command, _SetExpressionCommand):
                current = command
                root.title(f"{self.title} - {current.expression}")

            if current is None:
                self._safe_update(root)
                time.sleep(0.03)
                continue

            try:
                stopped, current = self._play_once(av, Image, ImageTk, root, label, current)
            except Exception as exc:
                print(f"Expression video playback error ({current.expression}): {exc}")
                current = None
                time.sleep(0.2)

        root.destroy()

    def _play_once(self, av, Image, ImageTk, root, label, current: _SetExpressionCommand):
        container = av.open(str(current.path))
        stream = container.streams.video[0]
        fps = float(stream.average_rate) if stream.average_rate else 24.0
        frame_delay = 1.0 / max(1.0, fps)
        next_current = current
        stopped = False

        try:
            for frame in container.decode(video=0):
                command = self._next_command(block=False)
                if isinstance(command, _StopCommand):
                    stopped = True
                    break
                if isinstance(command, _SetExpressionCommand):
                    next_current = command
                    root.title(f"{self.title} - {next_current.expression}")
                    break

                started_at = time.perf_counter()
                image = self._fit_frame(frame.to_image(), Image)
                photo = ImageTk.PhotoImage(image)
                label.configure(image=photo)
                label.image = photo
                self._safe_update(root)
                elapsed = time.perf_counter() - started_at
                time.sleep(max(0.0, frame_delay - elapsed))
        finally:
            container.close()

        return stopped, next_current

    def _fit_frame(self, image, Image):
        width, height = self.display_size
        if not self.keep_aspect_ratio:
            return image.resize((width, height), Image.Resampling.LANCZOS)

        fitted = image.copy()
        fitted.thumbnail((width, height), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (width, height), "black")
        x = (width - fitted.width) // 2
        y = (height - fitted.height) // 2
        canvas.paste(fitted, (x, y))
        return canvas

    def _next_command(self, block: bool):
        try:
            if block:
                return self._commands.get(timeout=0.1)
            return self._commands.get_nowait()
        except queue.Empty:
            return None

    def _safe_update(self, root) -> None:
        try:
            root.update_idletasks()
            root.update()
        except Exception:
            self._commands.put(_StopCommand())
