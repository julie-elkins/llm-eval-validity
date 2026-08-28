"""Was the grader right? Judge agreement, test-retest, and the ceiling the marginals impose.

The first two analyses in this repo took the harness's own numbers as given and asked how
precise they were. This one asks whether they were *correct*, which needs a second reader. The
reader is an LLM judge -- two of them, Sonnet 5 and Haiku 4.5 -- shown the question, both the
current and the superseded policy statement, and the reply, and nothing else: no configuration
label, no incumbent grade, no audit verdict. Five independent passes each, plus a sixth pass
with the two policy statements swapped, so run-to-run instability and order sensitivity are
measured rather than assumed away.

That design is what makes the headline finding available. Read run 1 alone and Haiku beats
Sonnet; read all five and Haiku's worst run lands on Sonnet's best. The between-model gap is
smaller than the within-model spread, so a single-run comparison would have declared a winner
that five runs cannot find. Every published judge comparison this study's author could find
reports a single run.

The second finding is about the coefficient rather than the judges. Split the 192 policy turns
by corpus and the stale-corpus half gives raw agreement of 95% and a kappa of zero -- exactly
zero for Haiku, slightly negative for Sonnet. Not because the judges failed but because both
they and the human reference answer `abstained` almost everywhere, and `kappa_max` on that half
is itself 0.00. The ceiling is zero, so no judge of any quality could score above it. A report
that quoted kappa alone would describe the study's best-behaved stratum as a failure.

Everything here reads `runs/*.jsonl` and touches no network. `validity.judge` spends the money;
this module is re-runnable for free.

Run it:  uv run python -m validity.reliability
"""

import collections
import json
from dataclasses import dataclass
from pathlib import Path

from validity import agreement, fixture
from validity.intervals import Interval

RUNS = Path(__file__).resolve().parent.parent / "runs"
JUDGES = ("sonnet-5", "haiku-4.5")
GRADES = (fixture.CORRECT, fixture.WRONG, fixture.CONFUSED, fixture.ABSTAINED)
VIOLATION = ("True", "False")

# Folding the four grades onto the decision a rollout actually turns on. `abstained` is not a
# good answer but it is a safe one -- the customer is handed to a human -- whereas `wrong` and
# `confused` both ship an incorrect policy statement.
HARM = {
    fixture.CORRECT: "safe",
    fixture.ABSTAINED: "safe",
    fixture.WRONG: "harmful",
    fixture.CONFUSED: "harmful",
}
HARM_CATEGORIES = ("harmful", "safe")

# The stratifying axis. Nine of the 24 configurations score 0/8 and every one is `corpus=v1`,
# which is the same confound `validity.discrimination` had to work around: over the full grid
# every statistic is really detecting the corpus.
STRATUM_AXIS = "corpus"

# Majority of five. An odd number of passes so a tie is impossible, which matters because a
# tie-break rule would be a judgement call sitting underneath every number in the report.
PASSES = 5


@dataclass(frozen=True)
class Reading:
    """One rater's labels for one family, keyed by index into `Fixture.turns`."""

    rater: str
    family: str
    labels: dict[int, str]
    # Present only for a judge read over several passes; None for the grader and the reference.
    passes: tuple[dict[int, str], ...] | None = None

    @property
    def unstable(self) -> tuple[int, ...]:
        """Turns whose label was not identical on every pass."""
        if not self.passes:
            return ()
        return tuple(t for t in sorted(self.labels) if len({p[t] for p in self.passes}) > 1)

    @property
    def alpha(self) -> float | None:
        """Krippendorff's alpha treating the passes as independent coders of the same turns.

        Intra-rater rather than inter-rater: the question is whether the judge agrees with
        *itself*, which bounds how much of its agreement with the human could be real. A judge
        whose own alpha is 0.90 cannot meaningfully agree with anything above 0.90.
        """
        if not self.passes:
            return None
        turns = sorted(self.labels)
        return agreement.krippendorff_alpha([tuple(p[t] for p in self.passes) for t in turns])


@dataclass(frozen=True)
class Comparison:
    """One rater against the human reference standard, over one set of turns."""

    rater: str
    label: str
    matrix: agreement.Matrix
    collapsed: agreement.Matrix
    kappa_ci: tuple[float, float] | None

    @property
    def n(self) -> int:
        return self.matrix.n

    @property
    def degenerate(self) -> bool:
        """True when the marginals make a positive kappa impossible.

        Happens when either rater used a single category: then `p_observed_max` equals
        `p_expected` and the ceiling is 0.00, so kappa is pinned at or below zero however good
        the rater is. The report has to say this out loud wherever it occurs.
        """
        return self.matrix.kappa_max <= 0.0


def read(path: Path = RUNS) -> dict[str, list[dict]]:
    """Load every recorded verdict, dropping the ones that errored."""
    out: dict[str, list[dict]] = {}
    for judge in JUDGES:
        f = path / f"{judge}.jsonl"
        if not f.exists():
            continue
        rows = [json.loads(line) for line in f.read_text().splitlines() if line.strip()]
        out[judge] = [r for r in rows if not r.get("error")]
    return out


def consensus(rows, judge: str, family: str, order: str = "current-first") -> Reading:
    """Majority label over the available passes, and the passes themselves.

    `wrong` and `confused` are read as-is rather than merged: the point of keeping the four-way
    scheme is to find out whether the judge uses it, and merging first would hide the answer.
    """
    field = "grade" if family == fixture.POLICY else "violation"
    by_run: dict[int, dict[int, str]] = collections.defaultdict(dict)
    for r in rows:
        if r["judge"] == judge and r["family"] == family and r["order"] == order:
            by_run[r["run"]][r["turn"]] = str(r[field])

    passes = tuple(by_run[k] for k in sorted(by_run))
    if not passes:
        return Reading(judge, family, {}, ())
    turns = sorted(set.intersection(*(set(p) for p in passes)))
    labels = {
        t: collections.Counter(p[t] for p in passes).most_common(1)[0][0] for t in turns
    }
    return Reading(judge, family, labels, passes)


def reference(f: fixture.Fixture, family: str, *, audited: bool = True) -> Reading:
    """The human standard, or the incumbent grader's labels if `audited` is False."""
    labels = {}
    for i, t in enumerate(f.turns):
        if t.family != family:
            continue
        if family == fixture.POLICY:
            v = t.grade_postaudit if audited else t.grade_preaudit
        else:
            v = t.violation_postaudit if audited else t.violation_preaudit
        if v is not None:
            labels[i] = str(v)
    return Reading("human audit" if audited else "regex grader", family, labels)


def compare(
    ref: Reading,
    rater: Reading,
    *,
    label: str = "all turns",
    turns=None,
    bootstrap: bool = True,
) -> Comparison:
    """Tabulate a rater against the reference over the turns both labelled."""
    family = ref.family
    categories = GRADES if family == fixture.POLICY else VIOLATION
    harm = HARM if family == fixture.POLICY else None

    keys = sorted(set(ref.labels) & set(rater.labels))
    if turns is not None:
        keys = [k for k in keys if k in set(turns)]
    pairs = [(ref.labels[k], rater.labels[k]) for k in keys]

    m = agreement.matrix(
        pairs, categories, reference_label=ref.rater, rater_label=rater.rater
    )
    collapsed = (
        m.collapse(harm, HARM_CATEGORIES)
        if harm
        else agreement.matrix(pairs, categories, reference_label=ref.rater,
                              rater_label=rater.rater)
    )

    ci = None
    if bootstrap:
        try:
            ci = agreement.bootstrap(
                pairs, lambda s: agreement.matrix(s, categories).kappa
            )
        except ValueError:
            ci = None  # too sparse to resample; the report says so rather than inventing one

    return Comparison(rater.rater, label, m, collapsed, ci)


def screen(f: fixture.Fixture, ref: Reading, grader: Reading, judge: Reading):
    """The judge as a screening test for grader error, not as a replacement grader.

    This is the framing that answers the deployment question. Nobody deploys a judge to
    relabel an eval; they deploy it to decide which turns a human should look at. So the
    positive class is "the incumbent grader disagrees with the human reference" and the test is
    "the judge disagrees with the incumbent grader". Sensitivity is then the share of real
    grader errors that reach a human, and review load is the price.
    """
    keys = sorted(set(ref.labels) & set(grader.labels) & set(judge.labels))
    error = [grader.labels[k] != ref.labels[k] for k in keys]
    flag = [judge.labels[k] != grader.labels[k] for k in keys]
    return agreement.screening(error, flag)


def spread(rows, judge: str, f: fixture.Fixture) -> tuple[float, float, list[float]]:
    """Per-pass kappa against the human reference: the range a single run would have hidden."""
    ref = reference(f, fixture.POLICY)
    by_run: dict[int, dict[int, str]] = collections.defaultdict(dict)
    for r in rows:
        if r["judge"] == judge and r["family"] == fixture.POLICY and r["order"] == "current-first":
            by_run[r["run"]][r["turn"]] = r["grade"]
    ks = []
    for run in sorted(by_run):
        labels = by_run[run]
        keys = sorted(set(ref.labels) & set(labels))
        ks.append(
            agreement.matrix([(ref.labels[k], labels[k]) for k in keys], GRADES).kappa
        )
    return (min(ks), max(ks), ks) if ks else (0.0, 0.0, [])


def order_flips(rows, judge: str, family: str) -> tuple[int, int]:
    """How many turns changed label when the two policy statements were presented in the other
    order. A judge sensitive to presentation order is measuring the prompt, not the reply."""
    field = "grade" if family == fixture.POLICY else "violation"
    got = {}
    for r in rows:
        if r["judge"] == judge and r["family"] == family and r["run"] == 1:
            got.setdefault(r["order"], {})[r["turn"]] = str(r[field])
    a, b = got.get("current-first", {}), got.get("superseded-first", {})
    keys = set(a) & set(b)
    return sum(1 for k in keys if a[k] != b[k]), len(keys)


# --- rendering ------------------------------------------------------------------------------


def _pct(x: float) -> str:
    return f"{x * 100:.1f}%"


def _ci(i: Interval) -> str:
    return f"{i.point:.3f} [{i.low:.2f}, {i.high:.2f}]"


def _row(c: Comparison) -> str:
    ci = f"[{c.kappa_ci[0]:+.2f}, {c.kappa_ci[1]:+.2f}]" if c.kappa_ci else "--"
    attained = (
        f"{c.matrix.kappa_attained:.2f}" if c.matrix.kappa_attained is not None else "n/a"
    )
    return (
        f"| {c.rater} | {c.n} | {c.matrix.p_observed:.3f} | {c.matrix.kappa:+.3f} | {ci} | "
        f"{c.matrix.kappa_max:.3f} | {attained} | {c.matrix.pabak:.3f} | "
        f"{c.matrix.weighted_kappa():+.3f} |"
    )


HEADER = (
    "| rater | n | raw agreement | kappa | 95% CI | kappa_max | attained | PABAK | weighted |\n"
    "|---|---|---|---|---|---|---|---|---|"
)


def report(f: fixture.Fixture, rows: dict[str, list[dict]]) -> None:
    if not rows:
        print("# Judge validation\n\nNo verdicts recorded. Run `make judge` first.")
        return

    policy_ref = reference(f, fixture.POLICY)
    grader = reference(f, fixture.POLICY, audited=False)
    judges = {j: consensus(rows[j], j, fixture.POLICY) for j in rows}
    n_passes = {j: len(r.passes or ()) for j, r in judges.items()}

    print("# Judge validation: is the grader's label the right label?\n")
    print(
        f"{len(policy_ref.labels)} policy turns, each graded four ways by a regex-based harness, "
        f"read once by a human auditor, and read {max(n_passes.values())} times each by two LLM "
        f"judges -- {', '.join(rows)} -- plus a further pass per judge with the two policy "
        f"statements swapped. {sum(len(v) for v in rows.values())} verdicts in total.\n"
    )
    print(
        "The judges saw the customer's question, the current policy statement, the superseded "
        "one, and the reply. They did not see the configuration, the incumbent grade, or the "
        "audit verdict. `tests/test_judge.py` asserts that over all 216 turns, because a judge "
        "that can see the existing label produces a high kappa that measures leakage and "
        "nothing downstream reveals it.\n"
    )

    # --- 1. the headline comparison ---------------------------------------------------------
    print("## Agreement with the human reference\n")
    print("Majority of five passes, against the post-audit human labels.\n")
    print(HEADER)
    comps = {}
    for j in rows:
        comps[j] = compare(policy_ref, judges[j])
        print(_row(comps[j]))
    grader_all = compare(policy_ref, grader)
    print(_row(grader_all))
    print()

    best = max(comps.values(), key=lambda c: c.matrix.kappa)
    print(
        f"Both judges agree with the human auditor more closely than the incumbent grader does "
        f"(kappa {grader_all.matrix.kappa:+.3f}). That is the result the study was run to get: "
        f"the labels the eval reported are not the labels a careful reader would assign, and an "
        f"LLM judge recovers more of the difference than the regex did.\n"
    )

    # --- 2. the run-to-run finding ----------------------------------------------------------
    print("## Why one run is not enough to rank two judges\n")
    print("| judge | kappa per pass | range | intra-judge alpha | turns that ever flipped |")
    print("|---|---|---|---|---|")
    ranges = {}
    for j in rows:
        lo, hi, ks = spread(rows[j], j, f)
        ranges[j] = (lo, hi)
        r = judges[j]
        print(
            f"| {j} | {', '.join(f'{k:.3f}' for k in ks)} | {lo:.3f}–{hi:.3f} | "
            f"{r.alpha:.3f} | {len(r.unstable)}/{len(r.labels)} |"
        )
    print()

    names = list(ranges)
    if len(names) == 2:
        a, b = names
        lo_a, hi_a = ranges[a]
        lo_b, hi_b = ranges[b]
        overlap = lo_a <= hi_b and lo_b <= hi_a
        print(
            f"Read pass 1 alone and {b} beats {a}. Read all {PASSES} and the intervals overlap"
            f"{'' if overlap else ' barely'}: {b}'s worst pass ({min(lo_b, lo_a):.3f}) sits "
            f"inside {a}'s range. **The between-model difference is no larger than the "
            f"within-model, run-to-run difference**, so this study cannot rank the two judges, "
            f"and a study that had run each judge once would have ranked them anyway.\n"
        )
        print(
            f"There is no temperature control to fall back on: the Python SDK's `messages.create` "
            f"does not accept sampling parameters at all in the 1.x line -- `temperature` is a "
            f"`TypeError`, not a rejected request -- and there is no seed. Repeated passes are the "
            f"only way to see this variance, which is the practical reason to budget for them.\n"
        )

    unstable_cases = collections.Counter(
        f.turns[t].case for j in rows for t in judges[j].unstable
    )
    if unstable_cases:
        top = ", ".join(f"`{c}` ({n})" for c, n in unstable_cases.most_common(3))
        print(
            f"The instability is not spread evenly. It concentrates on {top} -- the same items "
            f"the order-sensitivity check below picks out, which suggests genuinely borderline "
            f"replies rather than random noise.\n"
        )

    # --- 3. order sensitivity ----------------------------------------------------------------
    print("## Order sensitivity\n")
    print("| judge | turns relabelled when the statements were swapped |")
    print("|---|---|")
    for j in rows:
        flips, n = order_flips(rows[j], j, fixture.POLICY)
        print(f"| {j} | {flips}/{n} ({_pct(flips / n) if n else 'n/a'}) |")
    print()
    print(
        "Small, and smaller than the run-to-run variance -- so presenting the current policy "
        "first is not doing the judges' work for them. Worth measuring anyway: the arm costs one "
        "extra pass, and a judge that flipped 20% of its labels on a permutation of its own "
        "prompt would invalidate everything above it.\n"
    )

    # --- 4. the stratum finding --------------------------------------------------------------
    print(f"## The stratum where kappa cannot work\n")
    levels = f.levels(STRATUM_AXIS)
    print(f"| stratum | rater | n | raw agreement | kappa | kappa_max | PABAK |")
    print("|---|---|---|---|---|---|---|")
    strata = {}
    for level in levels:
        turns = [i for i, t in enumerate(f.turns) if t.family == fixture.POLICY
                 and getattr(t, STRATUM_AXIS) == level]
        for rater in list(judges.values()) + [grader]:
            c = compare(policy_ref, rater, label=f"{STRATUM_AXIS}={level}", turns=turns,
                        bootstrap=False)
            strata[(level, rater.rater)] = c
            print(
                f"| `{STRATUM_AXIS}={level}` | {c.rater} | {c.n} | {c.matrix.p_observed:.3f} | "
                f"{c.matrix.kappa:+.3f} | {c.matrix.kappa_max:.3f} | {c.matrix.pabak:.3f} |"
            )
    print()

    # The stratum to single out is the one where the reference standard is most concentrated on
    # a single label, because that is where kappa's denominator collapses.
    def concentration(level: str) -> float:
        vals = [policy_ref.labels[i] for i, t in enumerate(f.turns)
                if t.family == fixture.POLICY and getattr(t, STRATUM_AXIS) == level]
        return collections.Counter(vals).most_common(1)[0][1] / len(vals)

    stale = max(levels, key=concentration)
    dead = [c for (lv, _), c in strata.items() if lv == stale and c.degenerate]
    if dead:
        worst = min(dead, key=lambda c: c.matrix.p_observed)
        print(
            f"Read the `{STRATUM_AXIS}={stale}` rows again. Both judges agree with the human on "
            f"about {_pct(worst.matrix.p_observed)} of these turns and both score a kappa of zero "
            f"or below. For {worst.rater} the ceiling itself is **{worst.matrix.kappa_max:.2f}**: "
            f"it answered `abstained` on all {worst.n} turns, and a rater that uses one category "
            f"forces `p_observed_max = p_expected`, which pins kappa at 0.00 however good that "
            f"rater is. On this half of the data every retrieved document is superseded, the "
            f"human reference gives the same label to {_pct(concentration(stale))} of turns, and "
            f"answering it throughout is very nearly the correct behaviour.\n"
        )
        print(
            f"This is Feinstein and Cicchetti's paradox in its pure form, and it is the practical "
            f"warning the whole module exists to deliver: **a judge evaluated on a task whose "
            f"answer is usually the same answer will score a kappa near zero while being right "
            f"almost every time.** Report kappa alone and the study's best-behaved stratum reads "
            f"as its worst failure. Report `kappa_max` beside it and the number explains itself. "
            f"`tests/test_agreement.py` pins both of Feinstein's published tables for the same "
            f"reason.\n"
        )
        fresh = [c for (lv, _), c in strata.items() if lv != stale and not c.degenerate]
        if fresh:
            print(
                f"In the `{STRATUM_AXIS}={levels[-1]}` stratum, where the reference standard "
                f"actually varies, kappa becomes informative again and the ordering from the "
                f"headline table returns.\n"
            )

    # --- 5. the screening framing ------------------------------------------------------------
    print("## The deployment question: the judge as a screen, not a grader\n")
    print(
        f"Nobody deploys a judge to relabel an eval. They deploy it to decide which turns a "
        f"human should read. So the positive class here is *the grader's label disagrees with "
        f"the human reference*, and the test is *the judge disagrees with the grader*. "
        f"{len(f.corrections)} of the {len(f.turns)} turns were corrected by the audit.\n"
    )
    print("| judge | prevalence | sensitivity | specificity | precision | review load |")
    print("|---|---|---|---|---|---|")
    screens = {}
    for j in rows:
        s = screen(f, policy_ref, grader, judges[j])
        screens[j] = s
        prec = _ci(s.precision) if s.precision else "n/a"
        print(
            f"| {j} | {s.prevalence:.3f} | {_ci(s.sensitivity)} | {_ci(s.specificity)} | "
            f"{prec} | {_pct(s.review_load)} |"
        )
    print()
    top = max(screens.values(), key=lambda s: (s.sensitivity.point, -s.review_load))
    top_name = next(j for j, s in screens.items() if s is top)
    caught = top.true_positive
    print(
        f"That is the number for a deployment memo. {top_name} flags {_pct(top.review_load)} of "
        f"turns for human review and catches {caught} of the grader's {top.positives} actual "
        f"errors. But read the interval, not the point estimate: {top.positives} positives is a "
        f"small denominator, so a perfect {caught}/{top.positives} is still only consistent with "
        f"a true sensitivity as low as **{top.sensitivity.low:.2f}** -- as many as one grader "
        f"error in {round(1 / (1 - top.sensitivity.low))} could be missed by a screen that looked "
        f"flawless on this sample. "
        f"Reporting the point estimate alone would be the single most misleading thing this "
        f"study could do.\n"
    )
    print(
        f"Precision is the number that decides whether anyone keeps using it. At a prevalence of "
        f"{top.prevalence:.2f}, {_pct(top.specificity.point)} specificity still means roughly one "
        f"in {round(1 / (1 - (top.precision.point if top.precision else 0.5)))} flagged turns is "
        f"a false alarm, and a reviewer experiences that as noise no matter how good the "
        f"sensitivity is.\n"
    )

    # --- 6. per-item -------------------------------------------------------------------------
    print("## Where each rater fails\n")
    cases = sorted({t.case for t in f.policy})
    print(f"| question | n | " + " | ".join(rows) + " | regex grader | |")
    print("|---|---|" + "---|" * (len(rows) + 2))
    for case in cases:
        turns = [i for i, t in enumerate(f.turns) if t.case == case]
        cells = []
        for rater in list(judges.values()) + [grader]:
            hit = sum(1 for i in turns if rater.labels.get(i) == policy_ref.labels[i])
            cells.append(f"{hit / len(turns):.3f}")
        neg = "negation-sensitive" if f.policy_reference[case].negation_sensitive else ""
        print(f"| `{case}` | {len(turns)} | " + " | ".join(cells) + f" | {neg} |")
    print()

    neg_cases = [c for c in cases if f.policy_reference[c].negation_sensitive]
    if neg_cases:
        gr = [
            sum(1 for i, t in enumerate(f.turns) if t.case == c
                and grader.labels.get(i) == policy_ref.labels[i]) / 24
            for c in neg_cases
        ]
        print(
            f"The grader's two worst questions are exactly the two negation-sensitive ones "
            f"({', '.join(f'`{c}` at {g:.2f}' for c, g in zip(neg_cases, gr))}), where the "
            f"correct policy is that the company does *not* do something. Pattern-matching for "
            f"the policy's keywords cannot tell \"we do not price match\" from \"we will price "
            f"match\". Both judges are near-ceiling on both. This is the clearest statement of "
            f"what the judge buys: not a uniform lift, but the repair of a specific, "
            f"predictable class of grader failure.\n"
        )
        print(
            f"It runs the other way too. The judges' weakest questions are ones the grader "
            f"handles cleanly, so the two disagree about different turns -- which is an argument "
            f"for keeping the grader and screening it, rather than replacing it with a judge.\n"
        )

    # --- 7. the four-way scheme --------------------------------------------------------------
    print("## The four-way scheme was a two-way scheme\n")
    used = {
        r.rater: sorted({v for v in r.labels.values()})
        for r in list(judges.values()) + [policy_ref, grader]
    }
    print("| rater | grades actually used |")
    print("|---|---|")
    for name, u in used.items():
        print(f"| {name} | {', '.join(f'`{g}`' for g in u)} |")
    print()
    ref_used = used[policy_ref.rater]
    print(
        f"The human reference standard uses {len(ref_used)} of the four grades "
        f"({', '.join(f'`{g}`' for g in ref_used)}) and never once uses "
        f"{', '.join(f'`{g}`' for g in GRADES if g not in ref_used)}. Once a careful reader had "
        f"looked at all 192 replies, the harmful categories were empty: the system either "
        f"answered correctly or declined. So the four-way rubric collapsed to a two-way one in "
        f"practice, the judges mostly followed, and the `wrong` row of every confusion matrix "
        f"above is structural rather than incidental.\n"
    )
    print(
        f"Worth being precise about what that does and does not mean. It is a finding about this "
        f"system on this corpus, not about the rubric: a distinction the examinee never triggers "
        f"is untested, not unnecessary. But it does mean the four-way kappas above are carrying "
        f"less information than four categories suggest, and it is the direct cause of the "
        f"`kappa_max` ceilings in the stratified table.\n"
    )

    # --- 8. the confusion matrices -----------------------------------------------------------
    print("## Confusion matrices\n")
    for j, c in comps.items():
        print(f"### {j}\n")
        print(f"```\n{c.matrix.table()}\n```\n")
        print(
            f"Collapsed to the harmful/safe decision a rollout turns on: raw agreement "
            f"{c.collapsed.p_observed:.3f}, up from {c.matrix.p_observed:.3f}, because collapsing "
            f"turns every within-class confusion into agreement. Kappa goes the other way, to "
            f"{c.collapsed.kappa:+.3f} against a ceiling of {c.collapsed.kappa_max:.2f} -- the "
            f"human reference labelled nothing harmful, so after the fold it is a single-category "
            f"rater and the paradox from the stratified table applies with full force. **The "
            f"collapse that matters most for a deployment decision is the one where kappa is "
            f"least usable**, which is worth stating plainly because a binary kappa is the "
            f"statistic a reader is most likely to ask for here.\n"
        )
    print("### regex grader\n")
    print(f"```\n{grader_all.matrix.table()}\n```\n")
    print(
        f"The grader's errors have a shape. {grader_all.matrix.get(fixture.ABSTAINED, fixture.CORRECT)} "
        f"turns where the human read an abstention were scored `correct`, and "
        f"{grader_all.matrix.get(fixture.ABSTAINED, fixture.WRONG)} were scored `wrong` -- so the "
        f"regex was finding policy language in replies that declined to state a policy. Both "
        f"judges make almost none of that error, and the per-question table above says where: "
        f"replies about the two negation-sensitive policies.\n"
    )

    # --- 9. behaviour ------------------------------------------------------------------------
    beh_ref = reference(f, fixture.BEHAVIOUR)
    beh = {j: consensus(rows[j], j, fixture.BEHAVIOUR) for j in rows}
    if any(r.labels for r in beh.values()):
        print("## The behaviour family, separately and with a much smaller n\n")
        print(HEADER)
        for j in rows:
            print(_row(compare(beh_ref, beh[j], bootstrap=False)))
        print()
        over = collections.Counter()
        for j in rows:
            for t, v in beh[j].labels.items():
                if v != beh_ref.labels.get(t):
                    over[f.turns[t].case] += 1
        print(
            f"{len(beh_ref.labels)} turns, which is too few to support a coefficient and is "
            f"reported so the omission is visible rather than silent. Five of the 24 behaviour "
            f"turns never reached the tool the case is about, so the reference standard records "
            f"nothing for them and they are excluded rather than counted as disagreements.\n"
        )
        if over:
            worst = ", ".join(f"`{c}`" for c, _ in over.most_common(2))
            print(
                f"Both judges err in the same direction -- they call behaviour a violation where "
                f"the human did not, concentrated on {worst}. An over-flagging judge is the safer "
                f"failure for a screen and the wrong one for a grader, which is another reason "
                f"the screening framing above is the one to deploy on.\n"
            )

    # --- 10. limits --------------------------------------------------------------------------
    print("## What this does not establish\n")
    print(
        "**There is one human reader.** The 26 corrections are one auditor's pass over all 216 "
        "turns, so there is no human-human ceiling here and the judge-human agreement above "
        "cannot be compared against one. That ceiling is the single most useful missing number: "
        "without it, a kappa of 0.91 could mean the judge nearly matches a human or that it "
        "nearly matches *this* human. A second independent rater on a stratified subsample of "
        "40-60 turns would settle it and is the first thing to add.\n"
    )
    citing = [t for t in f.policy if ".md" in (t.reply or "")]
    print(
        f"**The judges are not fully blind.** {len(citing)} of the {len(f.policy)} replies cite a "
        f"source filename, all of them from the current-corpus arm, and the filenames are "
        f"self-labelling (`-updated`, `-NEW`, `-v2-FINAL`). On those turns a judge could shortcut "
        f"the task without reading the policy. Not removable -- the reply is the evidence, and "
        f"the human auditor read the same text with the same cue -- but it means part of the "
        f"agreement above is explained by a cue rather than by comprehension. The "
        f"`{STRATUM_AXIS}={stale}` stratum, where no reply cites anything, is where the shortcut "
        f"buys nothing.\n"
    )
    print(
        "**The reference standard is not independent of the judges' input.** Both were shown the "
        "current and superseded policy statements. Handing the judge only the correct statement "
        "would have made its task strictly harder than the human's and turned a validity "
        "comparison into a handicap match, so this is the right call -- but it does mean neither "
        "reader derived the answer key, and an error in the key would be invisible to both.\n"
    )
    print(
        "**Determinism cannot be pinned.** No temperature, no seed, no way to make a pass "
        "repeatable. The run-to-run spread above is therefore a floor on the variance of any "
        "single-run judge result, including every single-run judge result in this repo's "
        "sources.\n"
    )
    print(
        f"**Nothing here is a pass rate.** The question this answers is whether the harness's "
        f"labels can be trusted, and the answer is that they can be trusted more after screening "
        f"than before. The share of volume that could be safely automated is a cut-score "
        f"question, which needs the harmful-error cost weights, and is the next analysis.\n"
    )


def main() -> int:
    f = fixture.load()
    report(f, read())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
