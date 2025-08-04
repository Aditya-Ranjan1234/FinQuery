"""Natural-language query parser.

First performs fast regex/rule extraction. If any critical fields are missing *and* the
environment variable ``OPENAI_API_KEY`` is present, calls an LLM (GPT-4o or similar)
for robust completion / correction.
"""
from __future__ import annotations

import os
import re
from typing import Dict, Pattern

from pydantic import ValidationError

from .schema import Query

# ---------------------------------------------------------------------------
# Regex patterns (very simple, can be improved)
# ---------------------------------------------------------------------------
_REGEXES: Dict[str, Pattern[str]] = {
    "age": re.compile(r"(\d{1,3})\s*(?:yo|year|yrs|y/o|-?old)", re.I),
    "procedure": re.compile(r"knee surgery|hip replacement|cataract|angioplasty", re.I),
    "location": re.compile(r"\b(pune|mumbai|delhi|kolkata|bengaluru)\b", re.I),
    # policy age: e.g. "3-month policy", "18 months policy"
    "policy_age_months": re.compile(r"(\d{1,2})\s*-?month", re.I),
}

_GENDER_RE = re.compile(r"\b(male|female|m|f)\b", re.I)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def parse_query(text: str) -> Query:  # noqa: D401
    """Return :class:`hackrx_llm.schema.Query` from *text*.

    This is *best-effort* – downstream stages should cope with missing fields.
    """

    data: Dict[str, str | int] = {"raw": text}

    # Gender first (simple)
    if m := _GENDER_RE.search(text):
        data["gender"] = m.group(1)

    # Other fields
    for key, regex in _REGEXES.items():
        if m := regex.search(text):
            # Use first capture group if present, otherwise entire match
            if m.lastindex:
                val = m.group(1)
            else:
                val = m.group(0)
            if key in {"age", "policy_age_months"}:
                val = int(val)
            data[key] = val

    # Optional LLM enrichment
    if os.getenv("OPENAI_API_KEY") and not _all_required(data):
        _enrich_via_llm(text, data)

    try:
        return Query(**data)
    except ValidationError as exc:  # pragma: no cover – developer debug aid
        raise RuntimeError(f"Parser produced invalid fields: {exc}")


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

_REQUIRED = {"age", "procedure", "location"}


def _all_required(d: Dict[str, object]) -> bool:
    return _REQUIRED.issubset(d.keys())


def _enrich_via_llm(prompt: str, data: Dict):  # pragma: no cover
    """Call OpenAI chat completion to fill missing keys in *data* in-place."""

    try:
        import openai  # heavyweight import guarded

        client = openai.OpenAI()
        messages = [
            {
                "role": "system",
                "content": (
                    "You are an expert medical insurance NLP assistant. "
                    "Extract age, gender (M/F), procedure, location, and policy duration in months "
                    "from the user's query. Respond ONLY as JSON like:\n"
                    "{\n 'age': 46, 'gender': 'M', 'procedure': 'knee surgery', 'location': 'Pune', 'policy_age_months': 3}\n"
                ),
            },
            {"role": "user", "content": prompt},
        ]
        completion = client.chat.completions.create(model="gpt-4o-mini", messages=messages)
        json_data = completion.choices[0].message.content
        data.update(eval(json_data))  # quick-and-dirty; production: use json lib
    except Exception as exc:  # noqa: BLE001
        # Fail gracefully – log to stderr but don't break flow
        import logging

        logging.getLogger(__name__).warning("LLM enrichment failed: %s", exc)
