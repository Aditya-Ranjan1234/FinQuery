"""DOCX document loader using **python-docx** (aka *docx*)."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

from docx import Document

from . import BaseLoader


class WordLoader(BaseLoader):
    """Load .docx files into one chunk per paragraph (non-empty)."""

    extensions = ["docx"]

    # ------------------------------------------------------------------
    def load(self) -> Iterable[Tuple[str, Dict]]:  # noqa: D401
        doc: Document = Document(self.path)  # type: ignore[arg-type]
        for idx, para in enumerate(doc.paragraphs):
            text = para.text.strip()
            if not text:
                continue
            meta: Dict[str, str | int] = {"source": str(self.path), "para": idx + 1}
            yield text, meta
