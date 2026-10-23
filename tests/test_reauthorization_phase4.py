from pathlib import Path

from validity.reauthorization import load_report


def test_phase4_fixture_records_the_split_aware_matrix():
    path = Path(__file__).parents[1] / "fixtures" / "reauthorization_phase4.json"
    report = load_report(path)

    assert report["report_kind"] == "agent-reauthorization-phase4-v1"
    assert report["case_count"] == 210
    assert report["base_case_count"] == 180
    assert report["compound_holdout_case_count"] == 30
    assert report["split_counts"]["locked_holdout"] == 54
    assert all(report["controls"].values())

    full = next(
        item for item in report["conditions"]
        if item["condition"] == "reauthorization"
    )
    assert full["false_ready_count"] == 0
    assert full["correct_escalation_count"] == 210
