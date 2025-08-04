"""Utility script to build a vector database (embeddings + FAISS index)
from the documents stored in *docs* directory.

It re-uses the existing ingestion & retrieval utilities from the
``hackrx_llm`` package and simply wraps them in a small CLI so that you can
run it independently of the Typer CLI defined in ``hackrx_llm.cli``.

Usage
-----

    # Build index from default documents folder and store under backend_index/
    python create_vector_db.py

    # Build index from a custom docs dir and output location
    python create_vector_db.py --docs ./my_docs --index ./vector_store/my_index

Two files will be produced at the *index* prefix location:

* ``<index>.faiss``   – the FAISS index with L2-normalised embedding vectors
* ``<index>.meta.pkl`` – pickled list[Clause] containing texts + metadata
"""
from __future__ import annotations

import argparse
from pathlib import Path

from hackrx_llm.ingestion import ingest_dir
from hackrx_llm.retriever import Retriever


DEFAULT_DOCS_DIR = Path("documents")  # relative to repo root
DEFAULT_INDEX_PREFIX = Path("backend_index/store")  # will create parent dirs if missing


def build_vector_db(docs_path: Path, index_prefix: Path):
    """Ingest *docs_path* directory and save vector DB to *index_prefix*.

    The *index_prefix* is the path *without* extension. The function will
    create ``<prefix>.faiss`` and ``<prefix>.meta.pkl`` under the same parent
    directory.
    """

    docs_path = docs_path.expanduser().resolve()
    index_prefix = index_prefix.expanduser().with_suffix("")  # ensure no ext

    if not docs_path.is_dir():
        raise FileNotFoundError(f"Documents directory not found: {docs_path}")

    # Ensure output directory exists
    index_prefix.parent.mkdir(parents=True, exist_ok=True)

    print(f"[1/3] Loading documents from {docs_path} …")
    clauses = ingest_dir(docs_path)
    print(f"    → Loaded {len(clauses)} clauses")

    print("[2/3] Building embeddings & FAISS index …")
    retriever = Retriever()
    retriever.fit(clauses)

    print(f"[3/3] Saving index to {index_prefix}.* …")
    retriever.save(index_prefix)
    print("✓ Vector database created successfully.")


def parse_args():
    parser = argparse.ArgumentParser(description="Create vector DB (FAISS) from documents")
    parser.add_argument(
        "--docs",
        type=Path,
        default=DEFAULT_DOCS_DIR,
        help="Path to documents directory (default: ./documents)",
    )
    parser.add_argument(
        "--index",
        type=Path,
        default=DEFAULT_INDEX_PREFIX,
        help="Output index *prefix* (default: ./backend_index/store)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    build_vector_db(args.docs, args.index)


if __name__ == "__main__":
    main()
