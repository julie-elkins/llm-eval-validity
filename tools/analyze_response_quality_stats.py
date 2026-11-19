"""Generate descriptive uncertainty summaries for the frozen response-quality study.

This tool consumes metadata-only aggregate counts. It deliberately refuses to
invent paired outcomes from aggregate totals. A paired comparison requires the
private case-level outcome file described in
research/response-quality/PAIRED_ANALYSIS_SPEC.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from validity.intervals import wilson


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "research/response-quality/FROZEN_AGGREGATES.json"
DEFAULT_OUTPUT = ROOT / "research/response-quality/STATISTICAL_SUMMARY.md"


def _pct(interval) -> str:
    return f"{interval.point * 100:.1f}% [{interval.low * 100:.1f}, {interval.high * 100:.1f}]"


def _row(condition: dict, metric: str, successes: int, denominator: int) -> str:
    interval = wilson(successes, denominator)
    label = {
        "acceptance": "protocol acceptance",
        "evidence_all_attempts": "evidence-contract satisfaction / all attempts",
        "evidence_accepted": "evidence-contract satisfaction / accepted",
    }[metric]
    return (
        f"| {condition['model']} | {condition['output_condition']} | {label} | "
        f"{successes}/{denominator} | {_pct(interval)} |"
    )


def render(data: dict) -> str:
    lines = [
        "# Frozen response-quality statistical summary",
        "",
        "This report uses 95% Wilson score intervals, which are bounded "
        "uncertainty intervals for a proportion. They are descriptive here; "
        "they do not turn the fixed synthetic pilot into a population estimate.",
        "",
        "| Model | Condition | Outcome | Count | Estimate [95% interval] |",
        "|---|---|---|---:|---:|",
    ]
    for condition in data["conditions"]:
        lines.append(_row(condition, "acceptance", condition["accepted"], condition["attempted"]))
        lines.append(
            _row(
                condition,
                "evidence_all_attempts",
                condition["evidence_satisfying_accepted"],
                condition["attempted"],
            )
        )
        lines.append(
            _row(
                condition,
                "evidence_accepted",
                condition["evidence_satisfying_accepted"],
                condition["accepted"],
            )
        )
    lines.extend(
        [
            "",
            "## Paired comparison status",
            "",
            "The paired comparison is not computed from this file. The public "
            "artifact has aggregate counts only, and aggregate counts do not "
            "identify which matched scenario/replicate outcomes changed between "
            "conditions. The required private-input contract is documented in "
            "[PAIRED_ANALYSIS_SPEC.md](PAIRED_ANALYSIS_SPEC.md).",
            "",
            "No provider runs, prompts, responses, or private traces are emitted "
            "by this analysis.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    data = json.loads(args.input.read_text())
    if data.get("study_status") != "frozen":
        raise SystemExit("refusing to analyze a non-frozen study")
    args.output.write_text(render(data))
    print(args.output)


if __name__ == "__main__":
    main()
