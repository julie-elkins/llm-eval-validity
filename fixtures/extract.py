"""Extract the validity study's fixture from northwind-connect-ai. Run once, from there.

    cd ~/northwind-connect-ai && uv run python /path/to/this/extract.py OUT.json

This exists because the study needs *two* label sets over the same 216 replies and only
one of them is stored. `evals/output/results.json` froze the grades as the run wrote them
on 2026-08-26. The corrected grades live nowhere: `evals.report.regrade` recomputes them
from the stored replies every time it runs, using a grader that was narrowed after a
human read the transcripts. That audit is the human pass this study validates against,
so both sets have to be captured together, once, with the code version recorded.

Vendoring the output rather than importing northwind is deliberate. Its `evals` package
reaches into `agent_tools`, `load` and boto3; a study about measurement should not need
an AWS SDK to compute a kappa, and it should still run when the source repo has moved on.
"""

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, ".")

from evals import cases, report  # noqa: E402  (needs cwd on the path first)

SOURCE = Path("evals/output/results.json")
RECHECK = Path("evals/output/results-recheck.json")


def git(*args: str) -> str:
    return subprocess.run(("git", *args), capture_output=True, text=True).stdout.strip()


def main(out: str) -> int:
    if not SOURCE.exists():
        raise SystemExit(f"run this from the northwind-connect-ai checkout; no {SOURCE}")

    raw = json.loads(SOURCE.read_text())
    records = raw["records"]

    # `regrade` mutates the records in place and *returns* them; the list of differences
    # it builds is printed and thrown away. So the pre-audit labels have to be copied out
    # before the call, and both fields matter: it re-derives `grade` on the policy family
    # and `violation` on the behaviour family, and the published "26 of 216 verdicts"
    # spans both.
    pre = [(r.get("grade"), r.get("violation")) for r in records]
    report.regrade(records)
    post = [(r.get("grade"), r.get("violation")) for r in records]

    items = []
    for record, (grade_before, viol_before), (grade_after, viol_after) in zip(records, pre, post):
        items.append(
            {
                "family": record.get("family"),
                "case": record.get("case"),
                "model": record.get("model"),
                "prompt": record.get("prompt"),
                "corpus": record.get("corpus"),
                "retriever": record.get("retriever"),
                "asked": record.get("asked"),
                "reply": record.get("say"),
                "next_action": record.get("next_action"),
                "rounds": record.get("rounds"),
                "usage": record.get("usage"),
                # The two label sets, per family. Policy turns carry a four-way `grade`;
                # behaviour turns carry a three-state `violation` (True / False / None for
                # "never reached the tool, so tested nothing"). `_preaudit` is what the run
                # wrote on 2026-08-26; `_postaudit` is what the narrowed grader says about
                # the same untouched reply.
                "grade_preaudit": grade_before,
                "grade_postaudit": grade_after,
                "violation_preaudit": viol_before,
                "violation_postaudit": viol_after,
                "corrected_by_audit": (grade_before, viol_before) != (grade_after, viol_after),
                # A fact about the tool calls, not the reply, so the grader reads it back
                # rather than recomputing it. Kept because it decides the denominator.
                "reached": record.get("reached"),
            }
        )

    fixture = {
        "provenance": {
            "source_repo": "https://github.com/JulieElkinsAWS/northwind-connect-ai",
            "source_commit": git("rev-parse", "HEAD"),
            "source_dirty": bool(git("status", "--porcelain")),
            "source_file": str(SOURCE),
            "run_date": "2026-08-26",
            "extracted_by": "fixtures/extract.py",
            "axes": raw.get("axes"),
            "held_constant": raw.get("held_constant"),
            "grader_note": (
                "grade_preaudit is the label the 2026-08-26 run wrote. grade_postaudit is "
                "evals.grade applied to the same stored reply at source_commit, after the "
                "audit narrowed five markers. The 26 disagreements are the human-adjudicated "
                "corrections this study treats as the reference standard."
            ),
        },
        "outcomes": list(getattr(__import__("evals.grade", fromlist=["OUTCOMES"]), "OUTCOMES")),
        "harmful": list(getattr(__import__("evals.grade", fromlist=["HARMFUL"]), "HARMFUL")),
        "policy_cases": [c.topic for c in cases.POLICY_CASES],
        "behaviour_cases": [c.key for c in cases.BEHAVIOUR_CASES],
        # The answer key. Captured because the judge stage needs something to judge
        # *against*, and the stored eval output has only the replies and the labels -- the
        # ground truth lived in the harness, which is exactly the part that does not
        # survive a teardown.
        #
        # Two statements per policy topic, not one. The corpus contains both documents:
        # `current_doc` states the correct policy and `superseded_doc` states the wrong one,
        # and both are retrievable in the v1 arm. So "wrong" here does not mean invented --
        # it means sourced from the stale document, which is the failure mode the whole eval
        # was built to detect. A judge given only the correct statement would have to infer
        # what the plausible wrong answer looks like; the grader never had to, and giving
        # the judge less information than the grader had would confound the comparison.
        "reference": {
            "policy": {
                c.topic: {
                    "asked": c.asked,
                    "correct_statement": c.correct_statement,
                    "wrong_statement": c.wrong_statement,
                    "current_doc": c.current_doc,
                    "superseded_doc": cases.ANSWER_KEY[c.topic]["superseded_doc"],
                    # Whether the source grader's regexes could see negation on this topic.
                    # Two topics they could not, and the source project reports their
                    # wrong-answer rate as a lower bound because of it. That asymmetry is a
                    # property of the reference standard, so it travels with it.
                    "negation_sensitive": c.negation_sensitive,
                }
                for c in cases.POLICY_CASES
            },
            "behaviour": {
                c.key: {
                    "asked": c.asked,
                    "violation": c.violation,
                    "detector": c.detector,
                    "identified_in_advance": c.identified,
                    "why_restricted": c.why_restricted,
                }
                for c in cases.BEHAVIOUR_CASES
            },
        },
        "n_corrected": sum(1 for i in items if i["corrected_by_audit"]),
        "items": items,
    }

    Path(out).write_text(json.dumps(fixture, indent=2) + "\n")
    print(f"wrote {out}: {len(items)} records, {fixture['n_corrected']} audit corrections")
    print(f"source commit {fixture['provenance']['source_commit'][:8]}"
          f"{' (DIRTY)' if fixture['provenance']['source_dirty'] else ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1] if len(sys.argv) > 1 else "turns.json"))
