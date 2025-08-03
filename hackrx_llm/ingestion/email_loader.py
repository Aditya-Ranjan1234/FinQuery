"""E-mail loader for raw *.eml* files using *email* stdlib."""
from __future__ import annotations

import email
from email import policy
from email.parser import BytesParser
from pathlib import Path
from typing import Dict, Iterable, Tuple

from . import BaseLoader


class EmailLoader(BaseLoader):
    """Load plain-text body from .eml files (skip attachments)."""

    extensions = ["eml"]

    # ------------------------------------------------------------------
    def load(self) -> Iterable[Tuple[str, Dict]]:  # noqa: D401
        with open(self.path, "rb") as fp:
            msg = BytesParser(policy=policy.default).parse(fp)

        text_parts = []
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    text_parts.append(part.get_content())
        else:
            text_parts.append(msg.get_content())

        body = "\n".join(t.strip() for t in text_parts if t)
        if not body:
            return  # type: ignore[return-value]

        meta: Dict[str, str] = {
            "source": str(self.path),
            "subject": msg.get("subject", ""),
            "date": msg.get("date", ""),
        }
        yield body, meta
