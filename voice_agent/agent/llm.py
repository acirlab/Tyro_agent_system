from __future__ import annotations

import asyncio
import os

from voice_agent.config import LLMConfig
from voice_agent.model_loading import fix_unsupported_socks_proxy


class FakeLLM:
    async def generate(self, messages: list[dict[str, str]] | str) -> str:
        if isinstance(messages, str):
            return messages
        for message in reversed(messages):
            if message.get("role") == "user":
                return message.get("content", "")
        return "好的。"


class QwenLLM:
    def __init__(self, config: LLMConfig) -> None:
        fix_unsupported_socks_proxy()
        from openai import OpenAI

        api_key = os.getenv(config.api_key_env)
        if not api_key:
            raise RuntimeError(f"Missing Qwen API key. Set environment variable: {config.api_key_env}")
        self.config = config
        self.client = OpenAI(
            api_key=api_key,
            base_url=config.base_url,
            timeout=config.timeout_seconds,
        )

    def generate_sync(self, messages: list[dict[str, str]] | str) -> str:
        if isinstance(messages, str):
            messages = [
                {"role": "system", "content": self.config.system_prompt},
                {"role": "user", "content": messages},
            ]
        completion = self.client.chat.completions.create(
            model=self.config.model,
            messages=messages,
            temperature=self.config.temperature,
            max_tokens=self.config.max_tokens,
        )
        return (completion.choices[0].message.content or "").strip()

    async def generate(self, messages: list[dict[str, str]] | str) -> str:
        return await asyncio.to_thread(self.generate_sync, messages)


def build_llm(config: LLMConfig):
    provider = config.provider.strip().lower()
    if provider == "fake":
        return FakeLLM()
    if provider == "qwen":
        return QwenLLM(config)
    raise ValueError(f"Unsupported LLM provider: {config.provider}")


def build_qwen_llm(
    *,
    model: str,
    api_key_env: str,
    base_url: str,
    max_tokens: int,
    timeout_seconds: float,
    temperature: float = 0.2,
    system_prompt: str = "你是严谨的科研写作助手。请基于给定证据写作，不要编造来源。",
):
    return QwenLLM(
        LLMConfig(
            provider="qwen",
            model=model,
            api_key_env=api_key_env,
            base_url=base_url,
            system_prompt=system_prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            timeout_seconds=timeout_seconds,
        )
    )
