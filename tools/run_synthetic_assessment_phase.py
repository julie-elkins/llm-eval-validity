"""Run the offline synthetic AI-assessment measurement phase.

The public case file contains metadata only. The reference dispositions are
loaded from a private local file and never copied into the public report.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validity.intervals import wilson


ROOT = Path(__file__).parents[1]
PUBLIC_CASES = ROOT / "research" / "ai-assessment-learning" / "synthetic_cases.json"
DEFAULT_REFERENCE = (
    Path.home()
    / ".codex"
    / "private"
    / "ai-assessment-learning"
    / "synthetic_reference.json"
)
DEFAULT_OUTPUT = (
    Path.home()
    / ".codex"
    / "private"
    / "ai-assessment-learning"
    / "latest-synthetic-summary.json"
)
VIEWS = ("final_answer_only", "evidence_aware")
DISPOSITIONS = {"supported", "not_supported", "unclear"}


class SyntheticPhaseError(ValueError):
    """Raised when the offline synthetic phase cannot produce a valid report."""


def _load_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise SyntheticPhaseError(f"{path} must contain a JSON object")
    return value


def _validate_inputs(
    public_cases: dict[str, Any], reference: dict[str, Any]
) -> tuple[list[dict[str, Any]], dict[str, dict[str, str]]]:
    cases = public_cases.get("cases")
    references = reference.get("cases")
    if not isinstance(cases, list) or not cases:
        raise SyntheticPhaseError("public case set must be a non-empty list")
    if not isinstance(references, list) or not references:
        raise SyntheticPhaseError("reference key must be a non-empty list")

    public_by_id = {case.get("case_id"): case for case in cases}
    reference_by_id = {case.get("case_id"): case for case in references}
    if None in public_by_id or None in reference_by_id:
        raise SyntheticPhaseError("every synthetic case needs a case_id")
    if set(public_by_id) != set(reference_by_id):
        raise SyntheticPhaseError("public cases and reference cases do not match")

    normalized: dict[str, str] = {}
    for case_id, reference_case in reference_by_id.items():
        disposition = reference_case.get("reference_disposition")
        if disposition not in DISPOSITIONS:
            raise SyntheticPhaseError(
                f"{case_id} has invalid reference disposition: {disposition}"
            )
        normalized[case_id] = disposition
    return cases, normalized


def _view_summary(
    cases: list[dict[str, Any]],
    references: dict[str, str],
    view: str,
) -> dict[str, Any]:
    counts = {
        "supported": 0,
        "not_supported": 0,
        "unclear": 0,
        "agreement": 0,
        "disagreement": 0,
    }
    disagreements: list[str] = []
    for case in cases:
        case_id = case["case_id"]
        observed = case.get(view)
        if observed not in DISPOSITIONS:
            raise SyntheticPhaseError(
                f"public case {case_id} is missing an observed {view} disposition"
            )
        expected = references[case_id]
        counts[observed] += 1
        if observed == expected:
            counts["agreement"] += 1
        else:
            counts["disagreement"] += 1
            disagreements.append(case_id)

    agreement_interval = wilson(counts["agreement"], len(cases))
    return {
        "view": view,
        "case_count": len(cases),
        "dispositions": {
            key: counts[key] for key in ("supported", "not_supported", "unclear")
        },
        "agreement_count": counts["agreement"],
        "disagreement_count": counts["disagreement"],
        "agreement_rate": round(counts["agreement"] / len(cases), 6),
        "agreement_interval_95": {
            "low": round(agreement_interval.low, 6),
            "high": round(agreement_interval.high, 6),
        },
        "disagreement_case_ids": disagreements,
    }


def _case_class_summary(
    cases: list[dict[str, Any]],
    references: dict[str, str],
    view: str,
) -> list[dict[str, Any]]:
    """Summarize agreement by planted case class without exposing the key."""

    by_class: dict[str, list[dict[str, Any]]] = {}
    for case in cases:
        case_class = case.get("case_class")
        if not isinstance(case_class, str) or not case_class:
            raise SyntheticPhaseError(
                f"public case {case['case_id']} is missing case_class"
            )
        by_class.setdefault(case_class, []).append(case)

    summaries: list[dict[str, Any]] = []
    for case_class, class_cases in sorted(by_class.items()):
        agreement_count = sum(
            case[view] == references[case["case_id"]] for case in class_cases
        )
        interval = wilson(agreement_count, len(class_cases))
        summaries.append(
            {
                "case_class": case_class,
                "case_count": len(class_cases),
                "agreement_count": agreement_count,
                "agreement_interval_95": {
                    "low": round(interval.low, 6),
                    "high": round(interval.high, 6),
                },
            }
        )
    return summaries


def run_phase(
    public_path: Path = PUBLIC_CASES,
    reference_path: Path = DEFAULT_REFERENCE,
) -> dict[str, Any]:
    """Run the metadata-only synthetic comparison."""

    public_cases, references = _validate_inputs(
        _load_json(public_path), _load_json(reference_path)
    )
    summaries = {
        view: _view_summary(public_cases, references, view) for view in VIEWS
    }
    class_summaries = {
        view: _case_class_summary(public_cases, references, view) for view in VIEWS
    }
    return {
        "schema_version": "0.3-synthetic-summary",
        "protocol_version": "0.3-synthetic",
        "decision": "complete",
        "execution_mode": "offline_metadata_only",
        "learner_outcome_observed": False,
        "case_count": len(public_cases),
        "views": summaries,
        "case_class_summaries": class_summaries,
        "limitations": [
            "Synthetic reference dispositions are not learner outcomes.",
            "The run does not establish that AI assistance improves learning.",
            "The run does not validate the rubric for a student population."
        ]
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--public-cases", type=Path, default=PUBLIC_CASES)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    summary = run_phase(args.public_cases, args.reference)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
