"""Decision logic that maps *Query* and retrieved *Clause*s into a structured
:class:`hackrx_llm.schema.DecisionResponse`.

For demo purposes the logic is intentionally **simplistic**:

1. If *procedure* is mentioned in **any** clause **and** the clause doesn't contain
   the phrase "not covered", the claim is *approved*.
2. If at least one clause mentions "payout up to Rs X" (regex), we include that
   numeric amount in the response.
3. Otherwise the claim is *rejected* with justification citing top clauses.

Real production systems would implement complex policy rules or chain-of-thought
LLM reasoning here.
"""
from __future__ import annotations

import re
from typing import List, Optional

from .schema import Clause, DecisionResponse, Query

_PAYOUT_RE = re.compile(r"payout\s+up\s+to\s+rs\s*(\d+[\d,]*)", re.I)


# ---------------------------------------------------------------------------
# Core public API
# ---------------------------------------------------------------------------

def evaluate(query: Query, clauses: List[Clause]) -> DecisionResponse:
    """Return :class:`DecisionResponse` for *query* given retrieved *clauses*."""

    procedure = (query.procedure or "").lower()
    approved = False
    amount: Optional[float] = None

    for c in clauses:
        text_l = c.text.lower()
        if procedure and procedure in text_l and "not covered" not in text_l:
            approved = True
        if m := _PAYOUT_RE.search(text_l):
            # Remove commas, convert to float
            amt_str = m.group(1).replace(",", "")
            amount = float(amt_str)

    decision = "approved" if approved else "rejected"
    justification = _render_justification(decision, amount, clauses, query)
    return DecisionResponse(
        decision=decision,
        amount=amount,
        justification=justification,
        clauses=clauses,
    )


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------

def _render_justification(decision: str, amount: Optional[float], clauses: List[Clause], query: Query) -> str:
    lead = (
        f"Claim for {query.procedure or 'procedure'} has been {decision.upper()}. "
        f"(Policy age: {query.policy_age_months or 'N/A'} months)"
    )
    amt_txt = f" Payout: Rs {amount:.2f}." if amount else ""
    clause_refs = ", ".join(c.id for c in clauses[:3])
    return f"{lead}{amt_txt} Based on clauses: {clause_refs}."
