from __future__ import annotations

from urllib.parse import urlencode

from voice_agent.research.clients.http import read_json
from voice_agent.research.models import Paper


class SemanticScholarClient:
    base_url = "https://api.semanticscholar.org/graph/v1/paper/search"

    def search(self, query: str, limit: int = 10) -> list[Paper]:
        fields = "title,authors,year,venue,abstract,url,citationCount,externalIds,openAccessPdf"
        params = urlencode({"query": query, "limit": limit, "fields": fields})
        payload = read_json(f"{self.base_url}?{params}")
        papers: list[Paper] = []
        for item in payload.get("data", []):
            title = str(item.get("title") or "").strip()
            if not title:
                continue
            external_ids = item.get("externalIds") or {}
            authors = [str(author.get("name")) for author in item.get("authors", []) if author.get("name")]
            papers.append(
                Paper(
                    title=title,
                    authors=authors,
                    year=item.get("year"),
                    venue=item.get("venue") or None,
                    abstract=item.get("abstract") or None,
                    url=item.get("url") or None,
                    pdf_url=((item.get("openAccessPdf") or {}).get("url") or None),
                    doi=external_ids.get("DOI"),
                    citation_count=item.get("citationCount"),
                    source="semantic_scholar",
                )
            )
        return papers
