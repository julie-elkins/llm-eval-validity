from __future__ import annotations

import json
from pathlib import Path

from tools.analyze_response_quality_stats import render


ROOT = Path(__file__).resolve().parents[1]


def test_frozen_aggregate_summary_contains_bounded_intervals():
    data = json.loads(
        (ROOT / "research/response-quality/FROZEN_AGGREGATES.json").read_text()
    )
    report = render(data)
    assert "93.3% [78.7, 98.2]" in report
    assert "10.0% [3.5, 25.6]" in report
    assert "paired comparison is not computed" in report


def test_public_aggregate_data_has_no_raw_response_fields():
    data = json.loads(
        (ROOT / "research/response-quality/FROZEN_AGGREGATES.json").read_text()
    )
    forbidden = {"prompt", "response", "tool_arguments", "answer_key", "trace"}
    for condition in data["conditions"]:
        assert not forbidden.intersection(condition)
