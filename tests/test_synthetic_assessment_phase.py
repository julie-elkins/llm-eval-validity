import json

import pytest

from tools.run_synthetic_assessment_phase import (
    SyntheticPhaseError,
    run_phase,
)


def _write_json(path, value):
    path.write_text(json.dumps(value), encoding="utf-8")


def test_synthetic_phase_reports_metadata_only(tmp_path):
    public_cases = {
        "cases": [
            {
                "case_id": "case-01",
                "case_class": "synthetic_control",
                "final_answer_only": "supported",
                "evidence_aware": "not_supported",
            }
        ]
    }
    reference = {
        "cases": [
            {
                "case_id": "case-01",
                "reference_disposition": "not_supported",
            }
        ]
    }
    public_path = tmp_path / "cases.json"
    reference_path = tmp_path / "reference.json"
    _write_json(public_path, public_cases)
    _write_json(reference_path, reference)

    summary = run_phase(public_path, reference_path)

    assert summary["learner_outcome_observed"] is False
    assert summary["views"]["final_answer_only"]["disagreement_count"] == 1
    assert summary["views"]["evidence_aware"]["agreement_count"] == 1
    assert "case-01" in summary["views"]["final_answer_only"]["disagreement_case_ids"]
    assert summary["views"]["evidence_aware"]["agreement_interval_95"]["high"] == 1.0
    assert summary["case_class_summaries"]["evidence_aware"][0]["case_count"] == 1


def test_synthetic_phase_rejects_mismatched_reference(tmp_path):
    public_path = tmp_path / "cases.json"
    reference_path = tmp_path / "reference.json"
    _write_json(
        public_path,
        {
            "cases": [
                {
                    "case_id": "case-01",
                    "final_answer_only": "supported",
                    "evidence_aware": "supported",
                }
            ]
        },
    )
    _write_json(
        reference_path,
        {
            "cases": [
                {
                    "case_id": "case-02",
                    "reference_disposition": "supported",
                }
            ]
        },
    )

    with pytest.raises(SyntheticPhaseError, match="do not match"):
        run_phase(public_path, reference_path)
