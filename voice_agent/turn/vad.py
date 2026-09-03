from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

import numpy as np

from voice_agent.config import SAMPLE_RATE
from voice_agent.model_loading import fix_unsupported_socks_proxy


def resources_dir() -> Path:
    from livekit.plugins import fireredchat_pvad

    return Path(fireredchat_pvad.__file__).resolve().parent / "resources"


def required_resource_paths() -> list[Path]:
    root = resources_dir()
    return [
        root / "pvad.onnx",
        root / "spkrec-ecapa-voxceleb" / "hyperparams.yaml",
        root / "spkrec-ecapa-voxceleb" / "embedding_model.ckpt",
        root / "spkrec-ecapa-voxceleb" / "classifier.ckpt",
        root / "spkrec-ecapa-voxceleb" / "mean_var_norm_emb.ckpt",
        root / "spkrec-ecapa-voxceleb" / "label_encoder.ckpt",
    ]


def missing_resources() -> list[Path]:
    return [path for path in required_resource_paths() if not path.exists()]


def load_vad(activation_threshold: float):
    fix_unsupported_socks_proxy()
    from livekit.plugins import fireredchat_pvad

    return fireredchat_pvad.VAD.load(activation_threshold=activation_threshold)


class WindowedPVAD:
    def __init__(self, activation_threshold: float) -> None:
        missing = missing_resources()
        if missing:
            missing_text = "\n".join(f"  {path}" for path in missing)
            raise RuntimeError(f"FireRedChat pVAD resources are missing:\n{missing_text}")
        self.threshold = activation_threshold
        self.vad = load_vad(activation_threshold)
        self.model = self.vad._model
        self.window_samples = int(self.model.window_size_samples)
        self.window_seconds = self.window_samples / SAMPLE_RATE
        self.tail = np.empty(0, dtype=np.float32)

    def reset(self) -> None:
        if hasattr(self.model, "reset"):
            self.model.reset()
        self.tail = np.empty(0, dtype=np.float32)

    def iter_windows(self, chunk: np.ndarray) -> Iterable[np.ndarray]:
        audio = np.asarray(chunk, dtype=np.float32).flatten()
        if len(audio) == 0:
            return
        if len(self.tail) > 0:
            audio = np.concatenate([self.tail, audio])
            self.tail = np.empty(0, dtype=np.float32)

        usable = (len(audio) // self.window_samples) * self.window_samples
        for start in range(0, usable, self.window_samples):
            yield audio[start : start + self.window_samples]
        if usable < len(audio):
            self.tail = audio[usable:]

    def probability(self, window: np.ndarray) -> float:
        return float(self.model(np.asarray(window, dtype=np.float32).flatten()))

    def update_speaker(self, audio_data: np.ndarray) -> None:
        import torch

        audio = torch.from_numpy(np.asarray(audio_data, dtype=np.float32).flatten()).unsqueeze(0)
        self.model.spkemb = self.model._spk_extractor.get_embedding(audio)

