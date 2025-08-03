"""Semantic retrieval over document clauses.

Embeds text with *sentence-transformers* and stores vectors in a FAISS index.
"""
from __future__ import annotations

import pickle
from pathlib import Path
from typing import List, Sequence

import faiss
from sentence_transformers import SentenceTransformer

from .schema import Clause

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class Retriever:
    """Vector-store wrapper (embeddings + FAISS) for fast semantic search."""

    def __init__(self, model_name: str = _MODEL_NAME, index_path: Path | None = None):
        self.model = SentenceTransformer(model_name)
        self.clauses: List[Clause] = []
        self.index: faiss.IndexFlatIP | None = None
        self.index_path = Path(index_path) if index_path else None
        if self.index_path and self.index_path.exists():
            self._load_index(self.index_path)

    # ------------------------------------------------------------------
    def fit(self, clauses: Sequence[Clause]):
        """Build FAISS index from *clauses*."""
        self.clauses = list(clauses)
        texts = [c.text for c in clauses]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
        self.index = faiss.IndexFlatIP(embeddings.shape[1])
        faiss.normalize_L2(embeddings)
        self.index.add(embeddings)

    def save(self, path: Path):
        """Persist index + metadata to *path* (two files: *.faiss, *.pkl)."""
        assert self.index is not None, "Index not built"
        faiss.write_index(self.index, str(path.with_suffix(".faiss")))
        with open(path.with_suffix(".meta.pkl"), "wb") as fp:
            pickle.dump(self.clauses, fp)

    # ------------------------------------------------------------------
    def add_clauses(self, new_clauses: Sequence[Clause]):
        """Incrementally add *new_clauses* to the index in-memory."""

        if not new_clauses:
            return
        texts = [c.text for c in new_clauses]
        embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=False)
        faiss.normalize_L2(embeddings)

        if self.index is None:
            # Fresh index
            self.index = faiss.IndexFlatIP(embeddings.shape[1])
        self.index.add(embeddings)
        self.clauses.extend(new_clauses)

    # ------------------------------------------------------------------
    def retrieve(self, query: str, top_k: int = 5) -> List[Clause]:
        """Return top-*k* most similar clauses to *query*."""
        assert self.index is not None, "Index not built. Call fit() or load index first."
        q_emb = self.model.encode([query], convert_to_numpy=True)
        faiss.normalize_L2(q_emb)
        scores, idxs = self.index.search(q_emb, top_k)
        return [self.clauses[i] for i in idxs[0] if i < len(self.clauses)]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------
    def _load_index(self, path: Path):
        self.index = faiss.read_index(str(path.with_suffix(".faiss")))
        with open(path.with_suffix(".meta.pkl"), "rb") as fp:
            self.clauses = pickle.load(fp)
