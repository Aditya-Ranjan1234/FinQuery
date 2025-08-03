"""Integration-ish test covering ingestion → retrieval → decision."""
import pytest

from hackrx_llm.schema import Clause
from hackrx_llm.decision_engine import evaluate
from hackrx_llm.retriever import Retriever
from hackrx_llm.parser import parse_query


@pytest.mark.skipif(
    pytest.importorskip("sentence_transformers", reason="sentence-transformers not installed"),
    reason="sentence-transformers unavailable",
)
def test_end_to_end():
    # Minimal synthetic clauses
    clauses = [
        Clause(id="c1", text="Knee surgery is covered up to Rs 100000.", source="pol.pdf"),
        Clause(id="c2", text="Hip replacement not covered.", source="pol.pdf"),
    ]

    retr = Retriever()
    retr.fit(clauses)

    query_text = "46-year-old male, knee surgery in Pune, 3-month policy"
    query_struct = parse_query(query_text)

    top = retr.retrieve(query_text, top_k=2)
    resp = evaluate(query_struct, top)

    assert resp.decision == "approved"
    assert resp.amount == 100000.0
