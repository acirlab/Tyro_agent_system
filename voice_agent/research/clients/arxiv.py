from __future__ import annotations

import xml.etree.ElementTree as ET
from urllib.parse import urlencode

from voice_agent.research.clients.http import read_text
from voice_agent.research.models import Paper


class ArxivClient:
    base_url = "https://export.arxiv.org/api/query"

    def search(self, query: str, limit: int = 10) -> list[Paper]:
        params = urlencode(
            {
                "search_query": f"all:{query}",
                "start": 0,
                "max_results": limit,
                "sortBy": "relevance",
                "sortOrder": "descending",
            }
        )
        body = read_text(f"{self.base_url}?{params}")
        root = ET.fromstring(body)
        ns = {"atom": "http://www.w3.org/2005/Atom"}
        papers: list[Paper] = []
        for entry in root.findall("atom:entry", ns):
            title = _child_text(entry, "title")
            if not title:
                continue
            authors = [_child_text(author, "name") for author in entry.findall("atom:author", ns)]
            published = _child_text(entry, "published") or _child_text(entry, "updated")
            papers.append(
                Paper(
                    title=" ".join(title.split()),
                    authors=[author for author in authors if author],
                    year=_parse_year(published),
                    venue="arXiv",
                    abstract=" ".join((_child_text(entry, "summary") or "").split()) or None,
                    url=_child_text(entry, "id"),
                    pdf_url=_pdf_url(entry),
                    doi=None,
                    citation_count=None,
                    source="arxiv",
                )
            )
        return papers


def _text(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    return element.text.strip()


def _child_text(element: ET.Element, child_name: str) -> str | None:
    for child in element:
        if child.tag.rsplit("}", 1)[-1] == child_name:
            return _text(child)
    return None


def _parse_year(value: str | None) -> int | None:
    if not value or len(value) < 4:
        return None
    try:
        return int(value[:4])
    except ValueError:
        return None


def _pdf_url(entry: ET.Element) -> str | None:
    for link in entry.findall("{http://www.w3.org/2005/Atom}link"):
        attrs = link.attrib
        if attrs.get("title") == "pdf" or attrs.get("type") == "application/pdf":
            return attrs.get("href")
    entry_id = _child_text(entry, "id")
    if entry_id and "/abs/" in entry_id:
        return entry_id.replace("/abs/", "/pdf/")
    return None
