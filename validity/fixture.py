"""Loading the 216 turns, and refusing to proceed if they are not the published ones.

The fixture is a vendored copy of another project's eval output (see `fixtures/extract.py`
for how it was produced and why it is vendored rather than imported). That makes it
evidence, and evidence that nothing checks is just a large file.

So `load` does not merely parse. It re-derives the four headline accuracy figures the
source repository publishes in its README and raises if any of them has moved. A fixture
that silently drifted -- a re-extraction against a different grader, a truncated copy, a
merge that dropped records -- would otherwise produce a study whose every downstream number
is internally consistent and describes nothing.
"""

import json
from dataclasses import dataclass
from pathlib import Path

FIXTURE = Path(__file__).resolve().parent.parent / "fixtures" / "turns.json"

CORRECT = "correct"
WRONG = "wrong"
CONFUSED = "confused"
ABSTAINED = "abstained"

# The two grades that mean the customer was told something untrue. Carried over from the
# source harness rather than reinvented: `confused` counts as harmful there because a reply
# hedging between the superseded and the current policy leaves a customer unable to act.
HARMFUL = (WRONG, CONFUSED)

POLICY = "policy"
BEHAVIOUR = "behaviour"

AXES = ("model", "prompt", "corpus", "retriever")

# What the source README publishes, as whole percents, from the post-audit grader. Each is
# a marginal over 96 or 64 policy turns. These are assertions about the fixture, not
# parameters -- if a re-extraction moves one, the load fails and the reason gets read.
PUBLISHED_ACCURACY = {
    ("corpus", "v1"): 5,
    ("corpus", "v2"): 77,
    ("retriever", "keyword"): 33,
    ("retriever", "kb"): 49,
    ("model", "haiku"): 27,
    ("model", "opus"): 52,
    ("prompt", "naive"): 43,
    ("prompt", "tuned"): 40,
}

PUBLISHED_N_TURNS = 216
PUBLISHED_N_POLICY = 192
PUBLISHED_N_CORRECTIONS = 26


@dataclass(frozen=True)
class Turn:
    """One model reply, with both label sets over it.

    `grade_*` is populated for the policy family and `violation_*` for the behaviour
    family, never both -- they are different measurements and averaging them would produce
    a number that means nothing. `violation` is three-state: True, False, or None for a
    turn that never reached the tool and therefore tested nothing.
    """

    family: str
    case: str
    model: str
    prompt: str
    corpus: str
    retriever: str
    asked: str | None
    reply: str | None
    grade_preaudit: str | None
    grade_postaudit: str | None
    violation_preaudit: bool | None
    violation_postaudit: bool | None
    corrected_by_audit: bool
    reached: bool | None

    @property
    def cell(self) -> str:
        """The grid cell this turn belongs to, as the source harness names it."""
        return f"{self.model}/{self.prompt}/{self.corpus}/{self.retriever}"

    @property
    def is_correct(self) -> bool:
        """Post-audit correctness, for the policy family only.

        Deliberately a property and not a stored field: which label set counts as the
        reference standard is the central choice of this study, and it should be stated in
        one place rather than baked into every call site.
        """
        return self.grade_postaudit == CORRECT

    @property
    def is_harmful_preaudit(self) -> bool:
        return self.grade_preaudit in HARMFUL

    @property
    def is_harmful_postaudit(self) -> bool:
        return self.grade_postaudit in HARMFUL


@dataclass(frozen=True)
class Fixture:
    turns: tuple[Turn, ...]
    provenance: dict
    policy_cases: tuple[str, ...]
    behaviour_cases: tuple[str, ...]

    def family(self, name: str) -> tuple[Turn, ...]:
        return tuple(t for t in self.turns if t.family == name)

    @property
    def policy(self) -> tuple[Turn, ...]:
        return self.family(POLICY)

    @property
    def behaviour(self) -> tuple[Turn, ...]:
        return self.family(BEHAVIOUR)

    @property
    def corrections(self) -> tuple[Turn, ...]:
        """The turns the human audit relabelled. The reference standard's disagreements."""
        return tuple(t for t in self.turns if t.corrected_by_audit)

    def cells(self) -> tuple[str, ...]:
        return tuple(sorted({t.cell for t in self.policy}))

    def levels(self, axis: str) -> tuple[str, ...]:
        return tuple(sorted({getattr(t, axis) for t in self.policy}))


def accuracy(turns) -> tuple[int, int]:
    """Correct count and denominator, post-audit. Returned as a pair, not a ratio.

    Callers that want a percentage can divide; callers that want a confidence interval need
    both numbers, and handing back only the ratio is how an interval silently becomes
    impossible to compute two modules downstream.
    """
    turns = tuple(turns)
    return sum(1 for t in turns if t.is_correct), len(turns)


def load(path: Path | str = FIXTURE, *, verify: bool = True) -> Fixture:
    raw = json.loads(Path(path).read_text())
    turns = tuple(
        Turn(
            family=i["family"],
            case=i["case"],
            model=i["model"],
            prompt=i["prompt"],
            corpus=i["corpus"],
            retriever=i["retriever"],
            asked=i.get("asked"),
            reply=i.get("reply"),
            grade_preaudit=i.get("grade_preaudit"),
            grade_postaudit=i.get("grade_postaudit"),
            violation_preaudit=i.get("violation_preaudit"),
            violation_postaudit=i.get("violation_postaudit"),
            corrected_by_audit=i["corrected_by_audit"],
            reached=i.get("reached"),
        )
        for i in raw["items"]
    )
    fixture = Fixture(
        turns=turns,
        provenance=raw["provenance"],
        policy_cases=tuple(raw["policy_cases"]),
        behaviour_cases=tuple(raw["behaviour_cases"]),
    )
    if verify:
        _verify(fixture)
    return fixture


def _verify(f: Fixture) -> None:
    """Re-derive what the source repository publishes, and raise on any drift."""
    problems = []

    if len(f.turns) != PUBLISHED_N_TURNS:
        problems.append(f"{len(f.turns)} turns, published run has {PUBLISHED_N_TURNS}")
    if len(f.policy) != PUBLISHED_N_POLICY:
        problems.append(f"{len(f.policy)} policy turns, published run has {PUBLISHED_N_POLICY}")
    if len(f.corrections) != PUBLISHED_N_CORRECTIONS:
        problems.append(
            f"{len(f.corrections)} audit corrections, published audit reports "
            f"{PUBLISHED_N_CORRECTIONS}"
        )

    # 24 cells, and every one of them non-empty. A missing cell would not change any
    # marginal enough to notice but would quietly break the discrimination analysis, whose
    # unit of observation is the cell.
    if len(f.cells()) != 24:
        problems.append(f"{len(f.cells())} grid cells, expected 24")

    for (axis, level), expected in PUBLISHED_ACCURACY.items():
        correct, n = accuracy(t for t in f.policy if getattr(t, axis) == level)
        if n == 0:
            problems.append(f"{axis}={level} has no turns")
            continue
        got = round(100 * correct / n)
        if got != expected:
            problems.append(
                f"{axis}={level} accuracy is {got}% ({correct}/{n}), published table says "
                f"{expected}%"
            )

    # The source project's headline claim, and the one most worth pinning: it holds only
    # after the audit. If a re-extraction ever makes this pass pre-audit too, the audit has
    # been silently folded into the stored labels and this study has lost its two raters.
    if any(t.is_harmful_postaudit for t in f.policy):
        problems.append("post-audit harmful verdicts exist; published run reports 0")
    if not any(t.is_harmful_preaudit for t in f.policy):
        problems.append(
            "no pre-audit harmful verdicts; the two label sets are indistinguishable, so "
            "there is nothing for the judge study to be validated against"
        )

    if problems:
        raise ValueError(
            "fixture does not reproduce the published run:\n  - " + "\n  - ".join(problems)
        )
