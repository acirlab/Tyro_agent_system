from __future__ import annotations

from urllib.parse import urlencode

from voice_agent.research.clients.http import read_json
from voice_agent.research.models import Paper


class OpenAlexClient:
    base_url = "https://api.openalex.org/works"

    def search(self, query: str, limit: int = 10) -> list[Paper]:
        params = urlencode(
            {
                "search": query,
                "per-page": limit,
                "select": "id,title,publication_year,primary_location,doi,cited_by_count,authorships,abstract_inverted_index",
            }
        )
        payload = read_json(f"{self.base_url}?{params}")
        papers: list[Paper] = []
        for item in payload.get("results", []):
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            authors = []
            for authorship in item.get("authorships", []):
                author = authorship.get("author") or {}
                if author.get("display_name"):
                    authors.append(str(author["display_name"]))
            location = item.get("primary_location") or {}
            source = location.get("source") or {}
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=item.get("publication_year"),
                    venue=source.get("display_name") or None,
                    abstract=_restore_abstract(item.get("abstract_inverted_index")),
                    url=location.get("landing_page_url") or item.get("id"),
                    pdf_url=location.get("pdf_url") or None,
                    doi=_clean_doi(item.get("doi")),
                    citation_count=item.get("cited_by_count"),
                    source="openalex",
                )
            )
        return papers


def _clean_doi(value: str | None) -> str | None:
    if not value:
        return None
    return value.removeprefix("https://doi.org/")


def _restore_abstract(index: dict[str, list[int]] | None) -> str | None:
    if not index:
        return None
    positions: list[tuple[int, str]] = []
    for word, offsets in index.items():
        for offset in offsets:
            positions.append((offset, word))
    return " ".join(word for _, word in sorted(positions))
