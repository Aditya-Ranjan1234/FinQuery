"""Flask web server providing a beautiful UI + JSON API for HackRx LLM system."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Dict

from flask import Flask, jsonify, render_template, request
from flask_cors import CORS

from .decision_engine import evaluate
from .ingestion import ingest_dir
from .parser import parse_query
from .retriever import Retriever

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DOCS_DIR = Path(os.getenv("DOCS_DIR", "sample_docs")).expanduser().resolve()
INDEX_PATH = Path(os.getenv("INDEX_PATH", "index/store")).expanduser().with_suffix("")
TOP_K_DEFAULT = int(os.getenv("TOP_K", "5"))

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

def create_app() -> Flask:  # noqa: D401
    """Return a configured :class:`flask.Flask` application."""

    app = Flask(
        __name__,
        template_folder=str(Path(__file__).with_suffix("").parent / "templates"),
        static_folder=str(Path(__file__).with_suffix("").parent / "static"),
    )
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    retriever = _init_retriever()

    # ------------------------------------------------------------------
    # Routes
    # ------------------------------------------------------------------
    @app.route("/")
    def index():  # noqa: D401
        return render_template("index.html")

    @app.post("/api/ask")
    def api_ask():  # noqa: D401
        data: Dict = request.get_json(force=True)
        query_text: str = data.get("query", "").strip()
        if not query_text:
            return jsonify({"error": "Missing 'query' field"}), 400

        top_k = int(data.get("top_k", TOP_K_DEFAULT))
        q_struct = parse_query(query_text)
        clauses = retriever.retrieve(query_text, top_k=top_k)
        resp = evaluate(q_struct, clauses)
        return app.response_class(
            response=resp.to_json(indent=2), mimetype="application/json"
        )

    return app


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _init_retriever() -> Retriever:
    """Load existing index or build from docs."""

    if INDEX_PATH.with_suffix(".faiss").exists():
        return Retriever(index_path=INDEX_PATH)

    if not DOCS_DIR.exists():
        DOCS_DIR.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Building index from docs in {DOCS_DIR} …")
    clauses = ingest_dir(DOCS_DIR)
    retr = Retriever()
    retr.fit(clauses)
    INDEX_PATH.parent.mkdir(parents=True, exist_ok=True)
    retr.save(INDEX_PATH)
    print(f"[INFO] Saved index to {INDEX_PATH}.faiss")
    return retr


# Stand-alone run -----------------------------------------------------------
if __name__ == "__main__":  # pragma: no cover
    app = create_app()
    app.run(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "8000")))
