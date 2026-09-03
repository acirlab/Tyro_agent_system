from __future__ import annotations

import asyncio
import html
from html.parser import HTMLParser
from typing import Any
from urllib.parse import parse_qs, quote_plus, unquote, urlparse
from urllib.request import Request, urlopen

from voice_agent.tools.base import ToolResult


class _DDGParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._capture_title = False
        self._current_href = ""
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "a" and "result__a" in attr_map.get("class", ""):
            self._capture_title = True
            self._current_href = attr_map.get("href", "")
            self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_title:
            title = html.unescape(" ".join(self._title_parts)).strip()
            href = _clean_ddg_url(self._current_href)
            if title and href:
                self.results.append({"title": title, "url": href})
            self._capture_title = False


class _DDGLiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._capture_title = False
        self._current_href = ""
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "a" and "result-link" in attr_map.get("class", ""):
            self._capture_title = True
            self._current_href = attr_map.get("href", "")
            self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_title:
            title = html.unescape(" ".join(self._title_parts)).strip()
            href = _clean_ddg_url(self._current_href)
            if title and href:
                self.results.append({"title": title, "url": href})
            self._capture_title = False


class _BingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.results: list[dict[str, str]] = []
        self._inside_result = False
        self._capture_title = False
        self._current_href = ""
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key: value or "" for key, value in attrs}
        if tag == "li" and "b_algo" in attr_map.get("class", ""):
            self._inside_result = True
            return
        if self._inside_result and tag == "a" and not self._capture_title:
            href = attr_map.get("href", "")
            if href.startswith(("http://", "https://")):
                self._capture_title = True
                self._current_href = href
                self._title_parts = []

    def handle_data(self, data: str) -> None:
        if self._capture_title:
            self._title_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._capture_title:
            title = html.unescape(" ".join(self._title_parts)).strip()
            if title and self._current_href:
                self.results.append({"title": title, "url": self._current_href})
            self._capture_title = False
        elif tag == "li" and self._inside_result:
            self._inside_result = False


def _clean_ddg_url(url: str) -> str:
    parsed = urlparse(url)
    if parsed.netloc.endswith("duckduckgo.com") and parsed.path == "/l/":
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        return unquote(target)
    return url


class WebSearchTool:
    name = "web_search"
    description = "Searches the public web using DuckDuckGo HTML results."

    async def execute(self, arguments: dict[str, Any], progress_callback, cancel_token: asyncio.Event) -> ToolResult:
        query = str(arguments.get("query", "")).strip()
        limit = int(arguments.get("limit", 5))
        if not query:
            return ToolResult(ok=False, data={}, error="missing query")
        await progress_callback("我正在搜索相关资料。")
        if cancel_token.is_set():
            return ToolResult(ok=False, data={}, error="cancelled")

        try:
            results = await asyncio.to_thread(self._search_sync, query, limit)
            if not results:
                return ToolResult(ok=False, data={"query": query, "results": []}, error="no search results parsed")
            return ToolResult(ok=True, data={"query": query, "results": results})
        except Exception as exc:
            return ToolResult(ok=False, data={"query": query, "results": []}, error=str(exc))

    def _search_sync(self, query: str, limit: int) -> list[dict[str, str]]:
        for search in (self._search_duckduckgo_lite, self._search_duckduckgo_html, self._search_bing):
            results = search(query, limit)
            if results:
                return results[:limit]
        return []

    def _search_duckduckgo_lite(self, query: str, limit: int) -> list[dict[str, str]]:
        request = Request(
            f"https://lite.duckduckgo.com/lite/?q={quote_plus(query)}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        body = self._read(request)
        parser = _DDGLiteParser()
        parser.feed(body)
        return parser.results[:limit]

    def _search_duckduckgo_html(self, query: str, limit: int) -> list[dict[str, str]]:
        request = Request(
            f"https://duckduckgo.com/html/?q={quote_plus(query)}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        body = self._read(request)
        parser = _DDGParser()
        parser.feed(body)
        return parser.results[:limit]

    def _search_bing(self, query: str, limit: int) -> list[dict[str, str]]:
        request = Request(
            f"https://www.bing.com/search?q={quote_plus(query)}",
            headers={"User-Agent": "Mozilla/5.0"},
        )
        body = self._read(request)
        parser = _BingParser()
        parser.feed(body)
        return parser.results[:limit]

    def _read(self, request: Request) -> str:
        with urlopen(request, timeout=15) as response:
            return response.read().decode("utf-8", errors="replace")
