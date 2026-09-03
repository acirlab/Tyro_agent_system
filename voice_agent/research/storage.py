from __future__ import annotations

from pathlib import Path
from time import strftime


class ResearchStorage:
    def __init__(self, root: Path | str = "research/runs") -> None:
        self.root = Path(root)

    def save_markdown(self, task_id: str, slug: str, markdown: str) -> Path:
        safe_slug = "".join(char if char.isalnum() or char in "-_" else "_" for char in slug).strip("_")
        safe_slug = safe_slug[:48] or "research"
        run_dir = self.root / f"{strftime('%Y%m%d_%H%M%S')}_{task_id[:8]}_{safe_slug}"
        run_dir.mkdir(parents=True, exist_ok=True)
        path = run_dir / "report.md"
        path.write_text(markdown, encoding="utf-8")
        return path
