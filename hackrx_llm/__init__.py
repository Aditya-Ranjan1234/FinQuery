"""HackRx LLM Document Processing System package.

High-level helpers are exposed for quick consumption.

Example:
    >>> from hackrx_llm import ingest_docs, ask
    >>> ingest_docs("./my_docs")
    >>> ask("46M knee surgery Pune 3-month policy")
"""

from pathlib import Path
from typing import List, Optional

from .cli import ingest, ask  # re-export Typer callback functions

__all__: List[str] = [
    "ingest",
    "ask",
]

# Semantic versioning (sync with pyproject if later added)
__version__: str = "0.1.0"

# Convenience wrappers -----------------------------------------------------

def ingest_docs(docs_dir: str | Path, index_path: Optional[str | Path] = None) -> None:
    """Programmatic wrapper around :pyfunc:`hackrx_llm.cli.ingest` command."""

    ingest.callback(docs=Path(docs_dir), index=index_path)


def ask(query: str, docs_dir: Optional[str | Path] = None, top_k: int = 5):
    """Programmatic wrapper around :pyfunc:`hackrx_llm.cli.ask` command."""

    return ask.callback(query=query, docs=docs_dir, top_k=top_k)
