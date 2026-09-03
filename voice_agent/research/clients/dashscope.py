from __future__ import annotations

import json
import math
import os
from urllib.request import Request, urlopen


class DashScopeEmbeddingClient:
    def __init__(
        self,
        *,
        model: str = "text-embedding-v4",
        api_key_env: str = "DASHSCOPE_API_KEY",
        base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.base_url = base_url.rstrip("/")

    def embed(self, texts: list[str]) -> list[list[float]]:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing DashScope API key: {self.api_key_env}")
        vectors: list[list[float]] = []
        for batch in _batches(texts, 10):
            payload = json.dumps({"model": self.model, "input": batch}).encode("utf-8")
            request = Request(
                f"{self.base_url}/embeddings",
                data=payload,
                headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
                method="POST",
            )
            with urlopen(request, timeout=25) as response:
                data = json.loads(response.read().decode("utf-8", errors="replace"))
            ordered = sorted(data.get("data", []), key=lambda item: item.get("index", 0))
            vectors.extend([item["embedding"] for item in ordered if "embedding" in item])
        if len(vectors) != len(texts):
            raise RuntimeError("embedding response size mismatch")
        return vectors


class DashScopeReranker:
    def __init__(
        self,
        *,
        model: str = "qwen3-rerank",
        api_key_env: str = "DASHSCOPE_API_KEY",
        endpoint: str = "https://dashscope.aliyuncs.com/api/v1/services/rerank/text-rerank/text-rerank",
    ) -> None:
        self.model = model
        self.api_key_env = api_key_env
        self.endpoint = endpoint

    def rerank(self, query: str, documents: list[str], top_n: int | None = None) -> list[tuple[int, float]]:
        api_key = os.getenv(self.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing DashScope API key: {self.api_key_env}")
        payload = {
            "model": self.model,
            "input": {"query": query, "documents": documents},
            "parameters": {"return_documents": False},
        }
        if top_n is not None:
            payload["parameters"]["top_n"] = top_n
        request = Request(
            self.endpoint,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(request, timeout=25) as response:
            data = json.loads(response.read().decode("utf-8", errors="replace"))
        results = (data.get("output") or {}).get("results") or data.get("results") or []
        scored: list[tuple[int, float]] = []
        for item in results:
            index = item.get("index")
            score = item.get("relevance_score", item.get("score", 0.0))
            if index is not None:
                scored.append((int(index), float(score)))
        if not scored:
            raise RuntimeError("empty rerank response")
        return scored


def cosine_similarity(left: list[float], right: list[float]) -> float:
    dot = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left))
    right_norm = math.sqrt(sum(b * b for b in right))
    if left_norm == 0 or right_norm == 0:
        return 0.0
    return dot / (left_norm * right_norm)


def _batches(values: list[str], size: int):
    for index in range(0, len(values), size):
        yield values[index : index + size]
