from pathlib import Path

from validity.reauthorization import load_report


def test_robustness_fixture_records_the_held_out_matrix():
    path = (
        Path(__file__).parents[1]
        / "fixtures"
        / "reauthorization_robustness.json"
    )
    report = load_report(path)

    assert report["report_kind"] == "agent-reauthorization-robustness-v1"
    assert report["case_count"] == 30
    assert report["case_set_sha256"] == (
        "bae8a87462aadb05ee1d6ade23d7e6e839be580cad5f8f29bf042d19b95740f2"
    )
    assert report["conditions"][2]["false_ready_count"] == 0
    assert report["conditions"][2]["correct_escalation_count"] == 30
