"""Vérifie que le scoring est reproductible et que les règles s'appliquent."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from scoring.engine import adjust_for_status, rank, score_company  # noqa: E402
from scoring.loader import load_companies, load_config  # noqa: E402

CONFIG = load_config()


def test_weights_sum_to_100():
    assert sum(c["weight"] for c in CONFIG["criteria"].values()) == 100


def test_score_is_reproducible():
    companies = load_companies()
    assert rank(companies, CONFIG) == rank(companies, CONFIG)


def test_hypothesis_moves_one_point_toward_neutral():
    u = CONFIG["uncertainty"]
    assert adjust_for_status(5, "hypothesis", u) == 4
    assert adjust_for_status(0, "hypothesis", u) == 1
    assert adjust_for_status(3, "hypothesis", u) == 2.5
    assert adjust_for_status(5, "unknown", u) == 2.5


def test_methodology_example_gives_80_5():
    f = lambda v, s: {"value": v, "status": s, "source": None}  # noqa: E731
    company = {
        "name": "Exemple",
        "business_model": f("commissionnaire", "fact"),
        "volume_level": f("eleve", "hypothesis"),
        "free_text_requests": f(True, "hypothesis"),
        "email_or_pdf_orders": f(True, "hypothesis"),
        "case_match": f("same_business", "fact"),
        "employees": f(35, "hypothesis"),
        "signals": [],
    }
    result = score_company(company, CONFIG)
    assert result["score"] == 80.5
    assert result["confidence"] == 0.4
    assert result["priority"] == "À approfondir"


def test_false_positives_are_excluded():
    results = {r["name"]: r for r in rank(load_companies(), CONFIG)}
    assert results["Transcoma"]["disqualified"]
    assert results["Grupo Moldtrans"]["disqualified"]
    assert results["Grupo Navec"]["disqualified"]
    assert results["Copcisa"]["details"][-1]["kept_note"] == 0  # signal négatif vérifié
