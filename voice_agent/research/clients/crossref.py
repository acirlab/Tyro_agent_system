from __future__ import annotations

from urllib.parse import urlencode

from voice_agent.research.clients.http import read_json


class CrossrefClient:
    base_url = "https://api.crossref.org/works"

    def find_doi(self, title: str) -> str | None:
        params = urlencode({"query.title": title, "rows": 1, "select": "DOI,title"})
        payload = read_json(f"{self.base_url}?{params}")
        items = (payload.get("message") or {}).get("items") or []
        if not items:
            return None
        doi = items[0].get("DOI")
        return str(doi) if doi else None
