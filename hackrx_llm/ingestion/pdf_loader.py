"""PDF document loader using **pdfplumber**.

Splits each page of the PDF into a single clause (chunk).
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, Tuple

import pdfplumber

from . import BaseLoader


class PDFLoader(BaseLoader):
    """Load PDF files into text chunks per page."""

    extensions = ["pdf"]

    # ------------------------------------------------------------------
    def load(self) -> Iterable[Tuple[str, Dict]]:  # noqa: D401
        """Yield ``(text, metadata)`` for each page in the PDF."""

        with pdfplumber.open(self.path) as pdf:
            for page_num, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                text = text.strip()
                if not text:
                    continue  # skip blank pages
                meta = {"source": str(self.path), "page": page_num}
                yield text, meta
