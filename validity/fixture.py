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

# The two policy topics whose correct answer is a negation ("does not price match", "proof of
# purchase is not required"). The source grader matched markers with regexes, so on these two
# a reply could state the right policy and be scored wrong, or state the wrong one and be
# scored correct, depending on where the "not" landed. The source project reports their
# wrong-answer rate as a lower bound for exactly this reason.
#
# Pinned as a constant rather than read from the fixture because it is the one place the
# judge is expected to *beat* the grader rather than merely agree with it: a language model
# reading the sentence has no equivalent structural blind spot. If a re-extraction changes
# this set, the judge study's most interesting subgroup has silently moved.
NEGATION_SENSITIVE = ("price_match", "warranty_proof")


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
class PolicyReference:
    """The ground truth for one policy topic: what a right answer says, and what a wrong one says.

    Both statements, not just the correct one. Northwind's corpus contains a current document
    and a superseded one, and the wrong answer is not invented -- it is the superseded
    document, faithfully retrieved. A judge told only the correct policy would have to guess
    what the plausible failure looks like, while the grader it is being compared against was
    handed both. Withholding it would make the judge's job harder than the grader's and turn
    a validity comparison into a handicap match.
    """

    case: str
    asked: str
    correct_statement: str
    wrong_statement: str
    current_doc: str
    superseded_doc: str
    negation_sensitive: bool


@dataclass(frozen=True)
class BehaviourReference:
    """The ground truth for one behaviour turn, which is a described action rather than a fact.

    There is no correct sentence here -- the question is whether the reply did a particular
    thing, and `violation` is the human-readable statement of what that thing is. `detector`
    names the source harness's function for it, kept so a disagreement can be traced to a
    specific piece of code rather than to "the grader".
    """

    case: str
    asked: str
    violation: str
    detector: str
    identified_in_advance: bool
    why_restricted: str


@dataclass(frozen=True)
class Fixture:
    turns: tuple[Turn, ...]
    provenance: dict
    policy_cases: tuple[str, ...]
    behaviour_cases: tuple[str, ...]
    policy_reference: dict[str, PolicyReference]
    behaviour_reference: dict[str, BehaviourReference]

    def reference(self, turn: Turn) -> PolicyReference | BehaviourReference:
        """The ground truth for one turn, whichever family it belongs to.

        A single accessor because every consumer -- the judge prompt builder, the write-up,
        the cut-score weights -- wants "what was the right answer here" and should not have to
        branch on the family to ask.
        """
        if turn.family == POLICY:
            return self.policy_reference[turn.case]
        return self.behaviour_reference[turn.case]

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
    ref = raw["reference"]
    fixture = Fixture(
        turns=turns,
        provenance=raw["provenance"],
        policy_cases=tuple(raw["policy_cases"]),
        behaviour_cases=tuple(raw["behaviour_cases"]),
        policy_reference={k: PolicyReference(case=k, **v) for k, v in ref["policy"].items()},
        behaviour_reference={
            k: BehaviourReference(case=k, **v) for k, v in ref["behaviour"].items()
        },
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

    problems += _verify_reference(f)

    if problems:
        raise ValueError(
            "fixture does not reproduce the published run:\n  - " + "\n  - ".join(problems)
        )


def _verify_reference(f: Fixture) -> list[str]:
    """Check the answer key covers every case and says something usable about each.

    Separate from the accuracy checks because it fails for different reasons. Those catch a
    fixture that drifted; this catches one that is missing the half the judge stage runs on --
    and it would otherwise fail silently, as an empty prompt slot producing a judge that
    confidently grades against nothing.
    """
    problems = []

    missing = set(f.policy_cases) - set(f.policy_reference)
    if missing:
        problems.append(f"no answer key for policy cases {sorted(missing)}")
    missing = set(f.behaviour_cases) - set(f.behaviour_reference)
    if missing:
        problems.append(f"no answer key for behaviour cases {sorted(missing)}")

    for case, r in sorted(f.policy_reference.items()):
        # An identical pair would make the item ungradeable by anything, human included, and
        # is the shape a copy-paste error in the source answer key would take.
        if r.correct_statement.strip() == r.wrong_statement.strip():
            problems.append(f"{case}: correct and wrong statements are identical")
        if not r.correct_statement.strip() or not r.wrong_statement.strip():
            problems.append(f"{case}: empty statement in the answer key")
        if r.current_doc == r.superseded_doc:
            problems.append(f"{case}: current and superseded documents are the same file")

    sensitive = tuple(sorted(c for c, r in f.policy_reference.items() if r.negation_sensitive))
    if sensitive != tuple(sorted(NEGATION_SENSITIVE)):
        problems.append(
            f"negation-sensitive topics are {list(sensitive)}, expected "
            f"{sorted(NEGATION_SENSITIVE)} -- the judge study's key subgroup has moved"
        )

    for case, b in sorted(f.behaviour_reference.items()):
        if not b.violation.strip() or not b.detector.strip():
            problems.append(f"{case}: behaviour reference does not say what the violation is")

    return problems
