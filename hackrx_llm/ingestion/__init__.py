"""Document ingestion utilities.

Each loader returns an iterator of tuples ``(text, metadata)`` where:
- *text*   – extracted plain-text str.
- *metadata* – dict with keys such as *source*, *page*, *chunk_id* …

Use :func:`ingest_dir` to recursively load supported documents from a directory.
"""
from __future__ import annotations

import itertools
from pathlib import Path
from typing import Dict, Iterable, List, Tuple, Type

from ..schema import Clause
from .pdf_loader import PDFLoader  # noqa: F401
from .word_loader import WordLoader  # noqa: F401
from .email_loader import EmailLoader  # noqa: F401


class BaseLoader:
    """Abstract base-class for document loaders."""

    extensions: List[str] = []  # override in subclasses

    def __init__(self, path: Path):
        self.path = path

    def __iter__(self):
        yield from self.load()

    # ---------------------------------------------------------------------
    def load(self) -> Iterable[Tuple[str, Dict]]:  # noqa: D401
        """Yield ``(text, metadata)`` for each chunk."""
        raise NotImplementedError


# -------------------------------------------------------------------------
# Loader registry helpers
# -------------------------------------------------------------------------


def _iter_subclasses(cls):
    for sub in cls.__subclasses__():
        yield sub
        yield from _iter_subclasses(sub)


def get_loader_for(path: Path) -> Type[BaseLoader] | None:
    ext = path.suffix.lower().lstrip(".")
    for loader_cls in _iter_subclasses(BaseLoader):
        if ext in loader_cls.extensions:
            return loader_cls
    return None


def ingest_dir(dir_path: Path) -> List[Clause]:
    """Load **all** supported files in *dir_path* into Clause objects."""
    clauses: List[Clause] = []
    for file in dir_path.rglob("*"):
        if not file.is_file():
            continue
        loader_cls = get_loader_for(file)
        if not loader_cls:
            continue
        for idx, (text, meta) in enumerate(loader_cls(file)):
            clause_id = f"{file.name}:{idx}"
            clauses.append(Clause(id=clause_id, text=text, source=str(file)))
    return clauses

# -------------------------------------------------------------------------
# Single-file helper
# -------------------------------------------------------------------------

def ingest_file(file_path: Path) -> List[Clause]:
    """Ingest a **single** file and return a list of :class:`Clause`."""

    loader_cls = get_loader_for(file_path)
    if not loader_cls:
        raise ValueError(f"Unsupported file type: {file_path.suffix}")
    clauses: List[Clause] = []
    for idx, (text, meta) in enumerate(loader_cls(file_path)):
        clause_id = f"{file_path.name}:{idx}"
        clauses.append(Clause(id=clause_id, text=text, source=str(file_path)))
    return clauses
