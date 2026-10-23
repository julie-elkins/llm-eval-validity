"""Validate and render the metadata-only agent reauthorization pilot result."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

EXPECTED_CONDITIONS = ("pass_fail", "revision_aware", "reauthorization")
PILOT_CONTROL_KEYS = (
    "case_count_is_18",
    "each_condition_has_full_coverage",
    "each_family_has_three_variants",
    "reauthorization_blocks_all_negative_controls",
    "revision_condition_detects_all_affected_cases",
)
ROBUSTNESS_CONTROL_KEYS = (
    "case_count_is_expected",
    "reference_manifest_is_complete",
    "each_family_has_base_variants",
    "each_condition_has_full_coverage",
    "reauthorization_blocks_all_negative_controls",
    "revision_condition_detects_all_affected_cases",
)


def load_report(path: Path) -> dict[str, Any]:
    """Load and validate the compact pilot record."""

    report = json.loads(path.read_text(encoding="utf-8"))
    if report.get("report_kind") not in {
        "agent-reauthorization-pilot-v1",
        "agent-reauthorization-robustness-v1",
    }:
        raise ValueError("Unexpected reauthorization pilot report kind.")
    if report.get("condition_count") != 3:
        raise ValueError("The report does not contain three conditions.")
    if report.get("metadata_only") is not True:
        raise ValueError("The pilot record must declare metadata_only=true.")
    if (
        report["report_kind"] == "agent-reauthorization-robustness-v1"
        and not report.get("artifact_merge_commit")
    ):
        raise ValueError(
            "The robustness record must identify the merged artifact revision."
        )
    controls = report.get("controls")
    if not isinstance(controls, dict):
        raise ValueError("The pilot report is missing its control results.")
    required_controls = (
        PILOT_CONTROL_KEYS
        if report["report_kind"] == "agent-reauthorization-pilot-v1"
        else ROBUSTNESS_CONTROL_KEYS
    )
    missing = [key for key in required_controls if key not in controls]
    if missing:
        raise ValueError(f"Missing pilot controls: {', '.join(missing)}")
    if not all(controls.values()):
        raise ValueError("The pilot integrity controls did not all pass.")
    conditions = report.get("conditions")
    if not isinstance(conditions, list):
        raise ValueError("The pilot report is missing condition summaries.")
    names = tuple(item.get("condition") for item in conditions)
    if names != EXPECTED_CONDITIONS:
        raise ValueError(f"Unexpected condition order: {names!r}")
    return report


def render_markdown(report: dict[str, Any]) -> str:
    """Render a reviewer-facing result summary."""

    heading = (
        "# Agent reauthorization robustness results"
        if report["report_kind"] == "agent-reauthorization-robustness-v1"
        else "# Agent reauthorization pilot results"
    )
    lines = [
        heading,
        "",
        f"- **Source commit:** `{report['source_commit']}`",
        *(
            [f"- **Artifact merge commit:** `{report['artifact_merge_commit']}`"]
            if report.get("artifact_merge_commit")
            else []
        ),
        f"- **Case-set SHA-256:** `{report['case_set_sha256']}`",
        f"- **Cases:** `{report['case_count']}` synthetic cases",
        "",
        "| condition | false-ready | stale detected | correct escalation | evaluation runs | review steps | time units |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in report["conditions"]:
        lines.append(
            "| `{condition}` | {false_ready_count} | "
            "{stale_claim_detection_count}/{stale_claims_requiring_detection} | "
            "{correct_escalation_count}/{case_count} | "
            "{evaluation_runs_total} | {review_steps_total} | "
            "{synthetic_time_units_total} |".format(**item)
        )
    lines.extend(
        [
            "",
            "A false-ready decision is an approval when the reference decision was "
            "`review_required` or `blocked`.",
            "",
            "## Interpretation boundary",
            "",
            "This is one deterministic synthetic pilot matrix. It shows that the "
            "implemented conditions produce the pre-specified control differences. "
            "It does not establish production safety, live model quality, or general "
            "organizational effectiveness.",
            "",
        ]
    )
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate and render the agent reauthorization pilot result."
    )
    parser.add_argument(
        "path",
        nargs="?",
        type=Path,
        default=Path("fixtures/reauthorization_pilot.json"),
    )
    args = parser.parse_args(argv)
    report = load_report(args.path)
    print(render_markdown(report), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
