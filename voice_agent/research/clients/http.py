from __future__ import annotations

import json
from urllib.request import Request, urlopen


def read_json(url: str, headers: dict[str, str] | None = None, timeout: int = 8) -> dict:
    request_headers = {"User-Agent": "TyroDuplexResearch/0.1"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def read_text(url: str, headers: dict[str, str] | None = None, timeout: int = 8) -> str:
    request_headers = {"User-Agent": "TyroDuplexResearch/0.1"}
    if headers:
        request_headers.update(headers)
    request = Request(url, headers=request_headers)
    with urlopen(request, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")
