"""Typer-powered CLI for HackRx LLM Document Processing System.

Usage examples.
--------------

Build vector index from documents in *docs* folder::

    python -m hackrx_llm ingest --docs docs/ --index index/store

Ask a question using an existing index::

    python -m hackrx_llm ask --query "46M knee surgery Pune 3-month policy" --index index/store --top-k 5

If *--index* is not provided, *ask* will fallback to building an ephemeral
index from *--docs*.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Optional

import typer
from rich import print
from rich.progress import Progress

from .decision_engine import evaluate
from .ingestion import ingest_dir
from .parser import parse_query
from .retriever import Retriever

app = typer.Typer(add_completion=False, help="LLM-powered document query CLI.")

# ---------------------------------------------------------------------------
# Paths helpers
# ---------------------------------------------------------------------------

def _resolve_path(p: str | Path | None) -> Optional[Path]:
    return Path(p).expanduser().resolve() if p else None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

@app.command()
def ingest(
    docs: Path = typer.Option(..., exists=True, file_okay=False, help="Directory with documents"),
    index: Path = typer.Option(
        "index/store",
        help="Path *prefix* for output FAISS + metadata files (without extension).",
    ),
):
    """Ingest *DOCS* directory, build vector index, and save to *INDEX*."""

    docs = docs.expanduser().resolve()
    index = index.expanduser().with_suffix("")  # strip ext if provided

    with Progress() as progress:
        task = progress.add_task("[green]Loading documents…", start=False)
        clauses = ingest_dir(docs)
        progress.update(task, completed=1)

        progress.add_task("[cyan]Building embeddings…", start=False)
        retr = Retriever()
        retr.fit(clauses)

        progress.add_task("[magenta]Saving index…", start=False)
        retr.save(index)

    print(f"[bold green]✓ Index saved to {index}.faiss")


@app.command()
def ask(
    query: str = typer.Option(..., prompt="Your query", help="Natural language question"),
    docs: Optional[Path] = typer.Option(None, help="Docs directory (if no index)", exists=True),
    index: Optional[Path] = typer.Option(None, help="Existing index prefix (.faiss + .meta.pkl)"),
    top_k: int = typer.Option(5, help="Number of clauses to retrieve"),
):
    """Answer *QUERY* using semantic search over documents or an existing index."""

    index = _resolve_path(index)
    docs = _resolve_path(docs)

    retr = None
    if index and index.with_suffix(".faiss").exists():
        retr = Retriever(index_path=index)
    elif docs and docs.is_dir():
        clauses = ingest_dir(docs)
        retr = Retriever()
        retr.fit(clauses)
    else:
        typer.echo("[red]Error: Provide either --index or --docs.", err=True)
        raise typer.Exit(1)

    # Process query
    q_struct = parse_query(query)
    clauses = retr.retrieve(query, top_k=top_k)
    decision = evaluate(q_struct, clauses)
    json_resp = decision.to_json(indent=2)
    print(json_resp)


@app.callback(invoke_without_command=True)
def _main(ctx: typer.Context):  # noqa: D401
    """Entry point when called without subcommand."""
    if ctx.invoked_subcommand is None:
        typer.echo(app.get_help())
        ctx.exit()


# Enable `python -m hackrx_llm …`
if __name__ == "__main__":  # pragma: no cover
    app()
