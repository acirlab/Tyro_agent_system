from __future__ import annotations

import re


class ExpressionSelector:
    def __init__(self, llm, available_expressions: list[str], choose_with_llm: bool = True) -> None:
        self.llm = llm
        self.available_expressions = sorted(set(available_expressions))
        self.choose_with_llm = choose_with_llm

    async def select(self, text: str, kind: str = "speech") -> str:
        if not self.available_expressions:
            return "neutral"
        fallback = self._fallback_select(text, kind)
        if not self.choose_with_llm:
            return fallback
        try:
            selected = await self._select_with_llm(text, kind)
        except Exception:
            return fallback
        return selected or fallback

    async def _select_with_llm(self, text: str, kind: str) -> str | None:
        messages = [
            {
                "role": "system",
                "content": (
                    "你只负责给语音助手选择一个表情视频名。"
                    "只能输出一个表情名，不要解释，不要标点。"
                    f"可选表情：{', '.join(self.available_expressions)}。"
                    "neutral 表示平静待机。"
                ),
            },
            {
                "role": "user",
                "content": f"语音类型：{kind}\n助手即将说：{text}",
            },
        ]
        response = (await self.llm.generate(messages)).strip().lower()
        return self._parse_response(response)

    def _parse_response(self, response: str) -> str | None:
        normalized = response.strip().lower().replace("-", "_").replace(" ", "_")
        if normalized in self.available_expressions:
            return normalized
        tokens = re.findall(r"[a-zA-Z_]+", normalized)
        for token in tokens:
            if token in self.available_expressions:
                return token
        return None

    def _fallback_select(self, text: str, kind: str) -> str:
        lower = text.lower()
        if kind == "progress":
            return self._first_available("neutral")
        if any(word in lower for word in ("你好", "您好", "hello", "hi")):
            return self._first_available("say_hallo", "happy", "neutral")
        if any(word in lower for word in ("完成", "好了", "成功", "可以了")):
            return self._first_available("happy", "neutral")
        if any(word in lower for word in ("失败", "错误", "抱歉", "没有找到", "不能")):
            return self._first_available("sad", "sympathy", "neutral")
        if any(word in lower for word in ("取消", "暂停", "等一下")):
            return self._first_available("neutral")
        if any(word in lower for word in ("吓", "危险", "警告")):
            return self._first_available("scared", "surprised", "neutral")
        if any(word in lower for word in ("惊", "突然", "发现")):
            return self._first_available("surprised", "neutral")
        return self._first_available("neutral")

    def _first_available(self, *names: str) -> str:
        for name in names:
            if name in self.available_expressions:
                return name
        return self.available_expressions[0] if self.available_expressions else "neutral"
