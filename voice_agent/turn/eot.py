from __future__ import annotations

import asyncio
from dataclasses import dataclass

import numpy as np

from voice_agent.config import EOTConfig, ModelLoadingConfig
from voice_agent.model_loading import fix_unsupported_socks_proxy


@dataclass(frozen=True)
class EOTPrediction:
    text: str
    probability: float
    is_end: bool


def _softmax(logits: np.ndarray) -> np.ndarray:
    logits = logits - np.max(logits, axis=-1, keepdims=True)
    exp_logits = np.exp(logits)
    return exp_logits / np.sum(exp_logits, axis=-1, keepdims=True)


class EndOfTurnDetector:
    def __init__(self, config: EOTConfig, model_loading: ModelLoadingConfig) -> None:
        fix_unsupported_socks_proxy()
        import onnxruntime as ort
        from huggingface_hub import hf_hub_download
        from transformers import AutoTokenizer

        self.config = config
        model_path = hf_hub_download(
            repo_id=config.repo_id,
            filename=config.model_file,
            local_files_only=model_loading.local_files_only,
            cache_dir=model_loading.huggingface_cache_dir,
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            config.tokenizer,
            truncation_side="left",
            local_files_only=model_loading.local_files_only,
            cache_dir=model_loading.huggingface_cache_dir,
        )
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])

    def text_for_eot(self, text: str) -> str:
        clean_text = text.strip()
        if self.config.strip_trailing_punctuation:
            clean_text = clean_text.rstrip(self.config.trailing_punctuation).strip()
        return clean_text

    def predict_sync(self, text: str) -> EOTPrediction:
        clean_text = self.text_for_eot(text)
        if not clean_text:
            return EOTPrediction(text=clean_text, probability=0.0, is_end=False)

        inputs = self.tokenizer(
            clean_text,
            truncation=True,
            padding="max_length",
            add_special_tokens=False,
            return_tensors="np",
            max_length=self.config.max_length,
        )
        ort_inputs = {
            item.name: inputs[item.name].astype(np.int64)
            for item in self.session.get_inputs()
            if item.name in inputs
        }
        outputs = self.session.run(None, ort_inputs)
        probability = float(_softmax(outputs[0]).flatten()[-1])
        return EOTPrediction(
            text=clean_text,
            probability=probability,
            is_end=probability >= self.config.threshold,
        )

    async def predict(self, text: str) -> EOTPrediction:
        return await asyncio.to_thread(self.predict_sync, text)


class AlwaysEndDetector:
    def __init__(self, probability: float = 1.0) -> None:
        self.probability = probability

    async def predict(self, text: str) -> EOTPrediction:
        return EOTPrediction(text=text.strip(), probability=self.probability, is_end=True)

