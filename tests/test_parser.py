"""Unit tests for the query parser."""
from hackrx_llm.parser import parse_query


def test_basic_parse():
    q = parse_query("46-year-old male, knee surgery in Pune, 3-month policy")
    assert q.age == 46
    assert q.gender == "M"
    assert q.procedure.lower().startswith("knee surgery")
    assert q.location.lower() == "pune"
    assert q.policy_age_months == 3
