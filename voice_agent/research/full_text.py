from __future__ import annotations

import hashlib
from pathlib import Path
from urllib.request import Request, urlopen

from voice_agent.research.models import Paper


class FullTextFetcher:
    def __init__(self, cache_dir: str | Path = "research/cache/full_text", max_bytes: int = 20_000_000) -> None:
        self.cache_dir = Path(cache_dir)
        self.max_bytes = max_bytes

    def fetch_text(self, paper: Paper) -> str | None:
        if not paper.pdf_url:
            return None
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha256(paper.pdf_url.encode("utf-8")).hexdigest()[:24]
        pdf_path = self.cache_dir / f"{digest}.pdf"
        text_path = self.cache_dir / f"{digest}.txt"
        if text_path.exists():
            cached = text_path.read_text(encoding="utf-8", errors="replace")
            if _looks_like_valid_full_text(cached):
                return cached
            text_path.unlink(missing_ok=True)
            return None
        if not pdf_path.exists():
            self._download(paper.pdf_url, pdf_path)
        text = self._extract_pdf_text(pdf_path)
        if _looks_like_valid_full_text(text):
            text_path.write_text(text, encoding="utf-8")
            return text
        return None

    def _download(self, url: str, output_path: Path) -> None:
        request = Request(url, headers={"User-Agent": "TyroDuplexResearch/0.1"})
        with urlopen(request, timeout=12) as response:
            content = response.read(self.max_bytes + 1)
        if len(content) > self.max_bytes:
            raise RuntimeError("PDF is too large")
        output_path.write_bytes(content)

    def _extract_pdf_text(self, pdf_path: Path) -> str:
        try:
            import pymupdf
        except Exception as exc:
            raise RuntimeError("PyMuPDF is required for PDF parsing") from exc
        parts: list[str] = []
        with pymupdf.open(pdf_path) as document:
            for index, page in enumerate(document, start=1):
                text = page.get_text("text").strip()
                if text:
                    parts.append(f"\n[page {index}]\n{text}")
        return "\n".join(parts)


def _looks_like_valid_full_text(text: str) -> bool:
    normalized = " ".join(text.split()).lower()
    if len(normalized) < 1000:
        return False
    bad_markers = (
        "javascript is disabled",
        "enable javascript",
        "access denied",
        "captcha",
        "cloudflare",
        "cookies are disabled",
    )
    if any(marker in normalized for marker in bad_markers):
        return False
    academic_markers = ("abstract", "introduction", "references", "method", "conclusion")
    return any(marker in normalized for marker in academic_markers)
