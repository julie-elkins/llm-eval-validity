"""What the published run could and could not have detected.

The source project reports four axis contrasts and calls one of them "no measurable
difference". That phrase is a claim about two things at once -- the effect and the
instrument -- and only one of them was measured. This module separates them: every marginal
gets a Wilson interval, every contrast gets a Newcombe difference interval, and every null
result gets the smallest effect the design could have resolved.

Run it:  uv run python -m validity.precision
"""

from validity import fixture, intervals

# The four contrasts the source README tabulates, as (axis, high level, low level). Ordered
# high-minus-low so a positive point estimate always means "the first level did better",
# which is the direction the published table reads in.
CONTRASTS = (
    ("corpus", "v2", "v1", "data readiness"),
    ("retriever", "kb", "keyword", "tool configuration"),
    ("model", "opus", "haiku", "model selection"),
    ("prompt", "naive", "tuned", "prompt configuration"),
)

# Where the published table's per-cell design lands, for the sizing section.
TURNS_PER_CELL = 8

# A contrast whose interval clears zero by less than this is reported as fragile rather than
# as a finding. Not a significance threshold -- the point is that a bound this close to zero
# would move to the other side of it under a handful of relabelled turns, and this study's
# whole subject is that 26 turns were in fact relabelled.
FRAGILE_MARGIN_POINTS = 5.0

# The axis whose effect is large enough to swamp the others when marginalised over, and the
# level of it that is not on the floor. See `stratified()`.
DOMINANT_AXIS = "corpus"
DOMINANT_LEVEL = "v2"


def marginals(f: fixture.Fixture) -> list[tuple[str, str, intervals.Interval]]:
    rows = []
    for axis in fixture.AXES:
        for level in f.levels(axis):
            correct, n = fixture.accuracy(t for t in f.policy if getattr(t, axis) == level)
            rows.append((axis, level, intervals.wilson(correct, n)))
    return rows


def contrasts(f: fixture.Fixture) -> list[tuple[str, str, str, str, intervals.Difference]]:
    rows = []
    for axis, high, low, pillar in CONTRASTS:
        ch, nh = fixture.accuracy(t for t in f.policy if getattr(t, axis) == high)
        cl, nl = fixture.accuracy(t for t in f.policy if getattr(t, axis) == low)
        rows.append((axis, high, low, pillar, intervals.difference(ch, nh, cl, nl)))
    return rows


def stratified(f: fixture.Fixture) -> list[tuple[str, str, str, intervals.Difference]]:
    """The same contrasts, restricted to the corpus arm that is not on the floor.

    Every marginal in the table above pools 48 turns from `corpus=v1`, where accuracy is 5%.
    That arm is a floor: the retrieved documents contradict the correct answer, so no prompt
    and no model can do much with them. Pooling a floor with a non-floor halves the range any
    other axis has room to move in, which biases every other contrast toward zero -- so a
    null on the prompt axis, computed over all 192 turns, is partly an artefact of the corpus
    axis rather than a fact about prompts.

    Restricting to `v2` costs half the sample and therefore widens every interval. That is
    the honest trade and both versions are reported: the marginal answers "what did this
    configuration deliver", the stratified answers "does this knob do anything".
    """
    rows = []
    pool = [t for t in f.policy if getattr(t, DOMINANT_AXIS) == DOMINANT_LEVEL]
    for axis, high, low, _pillar in CONTRASTS:
        if axis == DOMINANT_AXIS:
            continue
        ch, nh = fixture.accuracy(t for t in pool if getattr(t, axis) == high)
        cl, nl = fixture.accuracy(t for t in pool if getattr(t, axis) == low)
        rows.append((axis, high, low, intervals.difference(ch, nh, cl, nl)))
    return rows


def report(f: fixture.Fixture) -> None:
    print("# Precision of the published findings\n")
    print(f"Source: {f.provenance['source_repo']}")
    print(f"Commit: {f.provenance['source_commit'][:8]}   Run: {f.provenance['run_date']}")
    print(f"{len(f.policy)} graded policy turns across {len(f.cells())} cells, "
          f"{TURNS_PER_CELL} per cell. Post-audit labels.\n")

    print("## Accuracy by axis level, with 95% Wilson intervals\n")
    print("| axis | level | correct | n | accuracy | 95% CI | +/- |")
    print("|---|---|---|---|---|---|---|")
    for axis, level, i in marginals(f):
        print(f"| {axis} | {level} | {round(i.point * i.n)} | {i.n} | "
              f"{100 * i.point:.1f}% | [{100 * i.low:.1f}, {100 * i.high:.1f}] | "
              f"{i.half_width:.1f} pts |")

    print("\n## The four published contrasts\n")
    print("| axis | contrast | published | difference, 95% CI | separates from zero? |")
    print("|---|---|---|---|---|")
    for axis, high, low, _pillar, d in contrasts(f):
        published = f"{100 * d.b.point:.0f}% -> {100 * d.a.point:.0f}%"
        verdict = "no" if d.includes_zero else "**yes**"
        print(f"| {axis} | {low} -> {high} | {published} | {d.pct()} | {verdict} |")

    print("\n## What the nulls are actually saying\n")
    for axis, high, low, pillar, d in contrasts(f):
        if not d.includes_zero:
            continue
        print(f"**{axis} ({pillar}): {d.pct()}.** The interval spans zero, so this run does "
              f"not establish a difference between `{low}` and `{high}`. It also could not "
              f"have established one smaller than about {d.resolvable:.0f} points -- so "
              f"\"no measurable difference\" is, at this sample size, largely a statement "
              f"about the design. An effect of 10 points would have been missed.\n")

    print("## Which findings would not survive a relabelling\n")
    fragile = [
        (axis, low, high, d)
        for axis, high, low, _p, d in contrasts(f)
        if not d.includes_zero and 100 * min(abs(d.low), abs(d.high)) < FRAGILE_MARGIN_POINTS
    ]
    if not fragile:
        print("None: every contrast that clears zero clears it by more than "
              f"{FRAGILE_MARGIN_POINTS:.0f} points.\n")
    for axis, low, high, d in fragile:
        print(f"**{axis} ({low} -> {high}): {d.pct()}.** Clears zero by "
              f"{100 * min(abs(d.low), abs(d.high)):.1f} points. Reported as a finding in the "
              f"source project, and it is one -- but the bound is close enough that a "
              f"different-but-defensible grading of a few turns would move it across zero. "
              f"The human audit relabelled 26 of these 216 turns; that is the scale of "
              f"judgement this bound sits inside. Directionally supported, not established.\n")

    print(f"## The same contrasts within `{DOMINANT_AXIS}={DOMINANT_LEVEL}` only\n")
    print(f"The marginals above pool the `{DOMINANT_AXIS}=v1` arm, which sits at "
          f"{100 * intervals.wilson(*fixture.accuracy(t for t in f.policy if t.corpus == 'v1')).point:.0f}% "
          f"and is a floor: nothing any other knob does can show through it. Restricting to "
          f"the arm where the corpus is not the binding constraint halves n and widens every "
          f"interval, and is the version that answers whether a knob does anything at all.\n")
    print("| axis | contrast | all 192 turns | within v2 only (n=48/arm) |")
    print("|---|---|---|---|")
    pooled = {axis: d for axis, _h, _l, _p, d in contrasts(f)}
    for axis, high, low, d in stratified(f):
        print(f"| {axis} | {low} -> {high} | {pooled[axis].pct()} | {d.pct()} |")
    print()
    for axis, high, low, d in stratified(f):
        if pooled[axis].includes_zero and not d.includes_zero:
            print(f"**{axis} changes verdict.** Null over all 192 turns, non-null within v2 "
                  f"({d.pct()}). The pooled null was the floor talking, not the knob.\n")
        elif not pooled[axis].includes_zero and abs(d.point) > abs(pooled[axis].point):
            grew = 100 * (abs(d.point) - abs(pooled[axis].point))
            note = ""
            if 100 * min(abs(pooled[axis].low), abs(pooled[axis].high)) < FRAGILE_MARGIN_POINTS:
                note = (" This also resolves the fragile pooled bound above: within v2 the "
                        "contrast clears zero comfortably.")
            print(f"**{axis} is larger than the pooled figure suggests**, by {grew:.0f} points "
                  f"({pooled[axis].pct()} pooled, {d.pct()} within v2). The floor arm was "
                  f"diluting it, so the published marginal understates what this knob buys "
                  f"once the corpus is not the binding constraint.{note}\n")
        elif pooled[axis].includes_zero and d.includes_zero:
            print(f"**{axis} is null either way** ({d.pct()} within v2), so the pooled null "
                  f"is not a floor artefact -- though at n=48 per arm this version could only "
                  f"have detected an effect above about {d.resolvable:.0f} points.\n")

    print("## How large would the eval set have to be?\n")
    print("At p=0.5, the worst case for interval width:\n")
    print("| target precision | turns needed per category | vs. this design |")
    print("|---|---|---|")
    for target in (20, 10, 5, 2.5):
        need = intervals.n_for_half_width(target)
        print(f"| +/- {target} pts | {need} | {need / TURNS_PER_CELL:.0f}x the "
              f"{TURNS_PER_CELL} per cell |")
    print(f"\nThe per-cell n of {TURNS_PER_CELL} supports a half-width of roughly "
          f"{intervals.wilson(4, TURNS_PER_CELL).half_width:.0f} points. Per-cell claims in "
          f"the source tables should be read as directional only; the axis marginals, at 64 "
          f"and 96, are where the run can carry an argument.")


def main() -> int:
    report(fixture.load())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
