"""Which of the eight test questions actually distinguish a good configuration from a bad one.

An eval set is not a list of questions, it is an instrument, and the questions in it are not
interchangeable. A question every configuration gets right and a question every configuration
gets wrong both cost an API call and neither moves the score, so neither tells you anything
about the system under test. Item analysis is how a certification programme finds those, and
it transfers to an eval suite exactly.

The unit of observation is the grid cell: 24 configurations, each of which answered all eight
policy questions, so each question has 24 scored attempts by examinees of varying ability.

The catch, and the main finding of this module, is that "varying ability" does not hold over
all 24. Nine cells score 0/8 and every one of them is `corpus=v1`. An item analysis run over
the full grid therefore compares a group that could not answer anything against a group that
could, and every item looks excellent because every item detects the corpus. That is one fact
discovered eight times, not eight working items. So the analysis is run twice -- once over the
full grid to show the confound, once within the stratum where the corpus is not the binding
constraint to say something about the questions themselves.

Run it:  uv run python -m validity.discrimination
"""

from dataclasses import dataclass

from validity import fixture

# Conventional interpretive bands for corrected item-total correlation in test development
# (Ebel; used in most item-analysis handbooks). Bands rather than a single accept/reject cut
# because at 12 or 24 observations per item the estimate is itself very imprecise.
BANDS = (
    (0.40, "strong", "keep"),
    (0.30, "adequate", "keep"),
    (0.20, "marginal", "revise"),
    (0.00, "weak", "revise or drop"),
    (-1.01, "negative", "broken -- investigate before dropping"),
)

# Fraction of cells in the upper and lower groups for the discrimination index. A third apiece
# is the standard choice, trading some of the extremes' contrast for enough cells per group to
# be worth computing.
GROUP_FRACTION = 1 / 3

# The axis that dominates the grid, and the level of it that is not on the floor. Same
# stratification as `validity.precision`, for the same reason, established there.
DOMINANT_AXIS = "corpus"
DOMINANT_LEVEL = "v2"

# A stratum with fewer cells than this is not worth an item analysis at all; below it the
# correlations are noise with a decimal point.
MIN_CELLS = 10


@dataclass(frozen=True)
class Item:
    case: str
    correct: int
    n: int
    r_corrected: float
    r_uncorrected: float
    d_index: float
    upper: float
    lower: float

    @property
    def difficulty(self) -> float:
        """Proportion correct. Called difficulty by convention even though it measures ease."""
        return self.correct / self.n

    @property
    def saturated(self) -> bool:
        """Every attempt scored the same way, so the item has no variance to correlate with."""
        return self.difficulty in (0.0, 1.0)

    @property
    def band(self) -> tuple[str, str]:
        # Saturation is checked before the correlation bands because a saturated item's r is 0
        # for an arithmetic reason, and reporting it as "weak -- revise or drop" would invite
        # rewriting a question that works fine and is merely too easy for this examinee pool.
        if self.saturated:
            at = "ceiling" if self.difficulty == 1.0 else "floor"
            return f"at {at}", "regression check only"
        for floor, label, action in BANDS:
            if self.r_corrected >= floor:
                return label, action
        return BANDS[-1][1], BANDS[-1][2]


@dataclass(frozen=True)
class Analysis:
    """One item analysis over one set of cells."""

    label: str
    cells: tuple[str, ...]
    items: tuple[Item, ...]
    totals: dict[str, int]
    upper_group: tuple[str, ...]
    lower_group: tuple[str, ...]
    mean_interitem_r: float
    min_interitem_r: float
    max_interitem_r: float
    alpha: float

    @property
    def dead_cells(self) -> tuple[str, ...]:
        """Cells that scored zero. They have no ability to correlate against."""
        return tuple(c for c in self.cells if self.totals[c] == 0)

    @property
    def perfect_cells(self) -> tuple[str, ...]:
        return tuple(c for c in self.cells if self.totals[c] == len(self.items))


def pearson(xs, ys) -> float:
    """Pearson correlation, implemented rather than imported.

    With one dichotomous variable this is the point-biserial correlation -- the same formula,
    a different name for the case where one side is 0/1. Returns 0.0 for a constant series,
    where the coefficient is undefined: an item every configuration passes has no covariance
    with anything, and reporting 0 (with the difficulty alongside, which will read 1.00 and
    give the game away) is more useful downstream than a NaN that poisons a sort.
    """
    xs, ys = list(xs), list(ys)
    if len(xs) != len(ys):
        raise ValueError("series of different lengths")
    n = len(xs)
    if n < 3:
        raise ValueError(f"correlation over {n} observations is not meaningful")
    mx, my = sum(xs) / n, sum(ys) / n
    dx = [x - mx for x in xs]
    dy = [y - my for y in ys]
    sx = sum(d * d for d in dx) ** 0.5
    sy = sum(d * d for d in dy) ** 0.5
    if sx == 0 or sy == 0:
        return 0.0
    return sum(a * b for a, b in zip(dx, dy)) / (sx * sy)


def variance(xs) -> float:
    """Population variance. Population, not sample: alpha is defined over the observed set."""
    xs = list(xs)
    m = sum(xs) / len(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)


def cronbach_alpha(columns) -> float:
    """Internal consistency of the suite, from a list of per-item score columns.

    Included because it is the number that makes the redundancy visible. Alpha rises both
    when items measure one thing consistently and when they are near-duplicates, and it cannot
    tell those apart -- so a very high alpha on an eval suite is not straightforwardly good
    news. It is quoted here next to the mean inter-item correlation, which is what actually
    distinguishes the two readings.
    """
    columns = [list(c) for c in columns]
    k = len(columns)
    if k < 2:
        raise ValueError("alpha needs at least two items")
    totals = [sum(col[i] for col in columns) for i in range(len(columns[0]))]
    total_var = variance(totals)
    if total_var == 0:
        return 0.0
    return (k / (k - 1)) * (1 - sum(variance(c) for c in columns) / total_var)


def score_matrix(f: fixture.Fixture) -> tuple[tuple[str, ...], dict[str, dict[str, int]]]:
    """Cells x cases, scored 1 for a post-audit correct answer and 0 otherwise.

    Note what this deliberately collapses: `wrong`, `confused` and `abstained` all score 0.
    For item analysis that is right -- the question is whether the configuration produced the
    correct answer -- but it means a question that reliably provokes a safe abstention looks
    identical here to one that provokes a confident falsehood. The two are very different
    operationally, which is why the cut-score analysis keeps them apart and this one does not
    pretend to.
    """
    cells = f.cells()
    matrix = {c: {} for c in cells}
    for t in f.policy:
        matrix[t.cell][t.case] = int(t.is_correct)
    return cells, matrix


def analyse(f: fixture.Fixture, cells=None, label: str = "all cells") -> Analysis:
    all_cells, matrix = score_matrix(f)
    cells = tuple(all_cells if cells is None else cells)
    if len(cells) < MIN_CELLS:
        raise ValueError(f"{len(cells)} cells is too few for item analysis (need {MIN_CELLS})")
    cases = f.policy_cases
    totals = {c: sum(matrix[c][case] for case in cases) for c in cells}

    group_size = max(1, round(len(cells) * GROUP_FRACTION))
    ranked = sorted(cells, key=lambda c: totals[c])
    lower_group, upper_group = tuple(ranked[:group_size]), tuple(ranked[-group_size:])

    items = []
    for case in cases:
        scores = [matrix[c][case] for c in cells]
        rest = [totals[c] - matrix[c][case] for c in cells]
        items.append(
            Item(
                case=case,
                correct=sum(scores),
                n=len(scores),
                r_corrected=pearson(scores, rest),
                r_uncorrected=pearson(scores, [totals[c] for c in cells]),
                d_index=(
                    sum(matrix[c][case] for c in upper_group) / len(upper_group)
                    - sum(matrix[c][case] for c in lower_group) / len(lower_group)
                ),
                upper=sum(matrix[c][case] for c in upper_group) / len(upper_group),
                lower=sum(matrix[c][case] for c in lower_group) / len(lower_group),
            )
        )

    pairs = [
        pearson([matrix[c][a] for c in cells], [matrix[c][b] for c in cells])
        for i, a in enumerate(cases)
        for b in cases[i + 1 :]
    ]
    return Analysis(
        label=label,
        cells=cells,
        items=tuple(sorted(items, key=lambda i: -i.r_corrected)),
        totals=totals,
        upper_group=upper_group,
        lower_group=lower_group,
        mean_interitem_r=sum(pairs) / len(pairs),
        min_interitem_r=min(pairs),
        max_interitem_r=max(pairs),
        alpha=cronbach_alpha([[matrix[c][case] for c in cells] for case in cases]),
    )


def _table(a: Analysis) -> None:
    print("| question | correct | difficulty | r (corrected) | D | upper | lower | verdict |")
    print("|---|---|---|---|---|---|---|---|")
    for i in a.items:
        label, action = i.band
        print(f"| `{i.case}` | {i.correct}/{i.n} | {i.difficulty:.2f} | {i.r_corrected:+.2f} | "
              f"{i.d_index:+.2f} | {i.upper:.2f} | {i.lower:.2f} | {label} -- {action} |")


def report(f: fixture.Fixture) -> None:
    full = analyse(f, label="all 24 configurations")
    stratum = analyse(
        f,
        cells=[c for c in f.cells() if f"/{DOMINANT_LEVEL}/" in c],
        label=f"{DOMINANT_AXIS}={DOMINANT_LEVEL} only",
    )

    print("# Item analysis: which questions carry the eval\n")
    print(f"{len(full.items)} policy questions, each attempted by every configuration. "
          f"Post-audit labels.\n")

    print("## First, the analysis that looks like good news\n")
    print(f"Over all {len(full.cells)} configurations, upper and lower groups being the top and "
          f"bottom {len(full.upper_group)} by total score:\n")
    _table(full)
    print(f"\nEvery item strong, every lower-group pass rate exactly {full.items[0].lower:.2f}. "
          f"That last column is the tell.\n")

    print("## Why it is not good news\n")
    dead = full.dead_cells
    on_floor = [c for c in dead if f"/{DOMINANT_LEVEL}/" not in c]
    dead_in_lower = [c for c in full.lower_group if full.totals[c] == 0]
    every = "all" if len(on_floor) == len(dead) else f"{len(on_floor)} of"
    print(f"{len(dead)} of the {len(full.cells)} configurations scored 0/{len(full.items)}, and "
          f"{every} {len(dead)} of them are `{DOMINANT_AXIS}=v1`. "
          f"{len(dead_in_lower)} of the {len(full.lower_group)} cells in the lower group are "
          f"among them"
          f"{', so the lower group is nothing but configurations that answered nothing at all'
             if len(dead_in_lower) == len(full.lower_group) else ''}. "
          f"`lower` is therefore 0.00 for every question by construction, and `D` collapses to "
          f"the upper group's pass rate -- a difficulty statistic wearing a discrimination "
          f"statistic's name.\n")
    print(f"What every item is detecting is the corpus. Mean inter-item correlation over the "
          f"full grid is **{full.mean_interitem_r:+.2f}** (range {full.min_interitem_r:+.2f} to "
          f"{full.max_interitem_r:+.2f}) and Cronbach's alpha is **{full.alpha:.2f}** -- values "
          f"that in test development would be read as eight near-duplicate items rather than "
          f"eight good ones. The suite is behaving as a single item asked eight times: *did "
          f"this configuration retrieve the current policy document*.\n")

    print(f"## The analysis that says something about the questions\n")
    print(f"Restricted to the {len(stratum.cells)} `{DOMINANT_AXIS}={DOMINANT_LEVEL}` "
          f"configurations, where the corpus is not the binding constraint and the total scores "
          f"actually spread:\n")
    _table(stratum)
    print(f"\nMean inter-item correlation falls to **{stratum.mean_interitem_r:+.2f}** (range "
          f"{stratum.min_interitem_r:+.2f} to {stratum.max_interitem_r:+.2f}), alpha to "
          f"**{stratum.alpha:.2f}**. Both are what a suite of eight questions that measure "
          f"related-but-distinct things should look like -- so the redundancy in the first "
          f"table was the corpus axis, not a property of the questions.\n")

    keep = [i for i in stratum.items if i.band[1] == "keep"]
    print(f"**{len(keep)} of {len(stratum.items)} questions still discriminate at r >= 0.30 "
          f"once the floor is removed.** Those are the ones ranking configurations on anything "
          f"other than which corpus they were pointed at.\n")

    for i in stratum.items:
        if i.r_corrected < 0:
            print(f"**`{i.case}` correlates negatively (r = {i.r_corrected:+.2f}, difficulty "
                  f"{i.difficulty:.2f}).** Configurations that do well overall do *worse* here. "
                  f"In test development that signals a mis-keyed item or one measuring "
                  f"something outside the construct, not a hard item. It should be read before "
                  f"it is dropped, because the reason is the finding.\n")
        elif i.saturated:
            # A saturated item has zero variance, so r is 0 for an arithmetic reason rather
            # than an empirical one. Diagnosing it as "close to noise" would invite the wrong
            # fix -- rewriting a question that is working exactly as written, just too easily.
            side = "Every" if i.difficulty == 1.0 else "No"
            print(f"**`{i.case}` is at the {'ceiling' if i.difficulty else 'floor'} within this "
                  f"stratum ({i.correct}/{i.n}).** {side} configuration passed it, so it has no "
                  f"variance and its r of {i.r_corrected:+.2f} is arithmetic, not evidence of a "
                  f"defect. It still "
                  f"separates v1 from v2 -- it is a corpus detector, and a fine one. What it "
                  f"cannot do is rank two configurations that both have the current corpus, "
                  f"which is the decision this eval is for. Keep it as a regression check, "
                  f"stop counting it toward configuration comparisons, and add a harder "
                  f"question on the same topic if that topic needs to stay in the ranking.\n")
        elif i.r_corrected < 0.20:
            print(f"**`{i.case}` is close to noise (r = {i.r_corrected:+.2f}, D = "
                  f"{i.d_index:+.2f}, difficulty {i.difficulty:.2f}).** It costs a call in "
                  f"every configuration and barely changes the ranking. Either it has a defect "
                  f"or the construct it taps is not the one the other seven tap.\n")

    print("## What this table can and cannot support\n")
    print(f"The stratified correlations rest on {len(stratum.cells)} observations each. "
          f"Sampling error on a correlation at n={len(stratum.cells)} is roughly +/-0.5 near "
          f"r = 0, which is wider than most of the gaps in the table. So it separates 'clearly "
          f"working' from 'clearly not' and the ordering within those groups should not be "
          f"read at all. Retiring a question on this evidence alone would be overreach; "
          f"flagging it for review is what the number supports.\n")

    print("Two design lessons that do generalise, and are the reusable part:\n")
    print(f"1. **Run item analysis inside strata, not over the whole grid.** A factorial eval "
          f"with one dominant axis will report every item as excellent, because every item "
          f"detects the dominant axis. The full-grid table above is exactly the artefact, and "
          f"it is the table an eval harness produces by default.")
    print(f"2. **Check the lower group before trusting a discrimination index.** A lower group "
          f"scoring 0.00 on every item means the index is measuring the floor. Here that was "
          f"{len(dead)} of {len(full.cells)} configurations; the statistic gave no warning, the "
          f"raw column did.")

    print(f"\n## Difficulty spread\n")
    easiest = max(stratum.items, key=lambda i: i.difficulty)
    hardest = min(stratum.items, key=lambda i: i.difficulty)
    print(f"Within the stratum, difficulty runs {hardest.difficulty:.2f} (`{hardest.case}`) to "
          f"{easiest.difficulty:.2f} (`{easiest.case}`).")
    if stratum.perfect_cells:
        print(f"{len(stratum.cells)} configurations, of which {len(stratum.perfect_cells)} "
              f"scored full marks -- so the suite is approaching its ceiling for the better "
              f"configurations and would need harder questions to keep separating them.")


def main() -> int:
    report(fixture.load())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
