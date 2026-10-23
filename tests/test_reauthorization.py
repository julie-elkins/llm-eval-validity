import json
from pathlib import Path

from validity.reauthorization import EXPECTED_CONDITIONS, load_report


def test_reauthorization_fixture_is_the_checked_in_pilot_record():
    path = Path(__file__).parents[1] / "fixtures" / "reauthorization_pilot.json"
    report = load_report(path)

    assert report["decision"] == "pass"
    assert tuple(item["condition"] for item in report["conditions"]) == (
        EXPECTED_CONDITIONS
    )
    assert report["conditions"][0]["false_ready_count"] == 12
    assert report["conditions"][2]["correct_escalation_count"] == 18


def test_reauthorization_fixture_has_no_content_bearing_fields():
    path = Path(__file__).parents[1] / "fixtures" / "reauthorization_pilot.json"
    report = json.loads(path.read_text(encoding="utf-8"))

    assert report["metadata_only"] is True
    assert report["raw_payloads_included"] is False
    assert report["provider_output_included"] is False
    assert "results" not in report
