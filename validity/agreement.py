"""Inter-rater agreement, for comparing a judge against a reference standard.

Every statistic here answers the same question -- how much do two readers of the same reply
agree, beyond what they would have agreed on by accident -- and they disagree with each other
enough that reporting only one would be a choice worth hiding. That is the point of the module.

Raw agreement is the number a reader wants and the number that misleads. On this data 90% of
the 192 policy turns carry the same label, so any two raters agree on nine in ten replies
before either of them has read anything. Cohen's kappa corrects for that, and then overcorrects:
when one category holds most of the mass, kappa is bounded well below 1 by the marginals alone,
and a genuinely good judge scores like a poor one. That is the kappa paradox, and it is not a
curiosity here -- it is the expected regime, because the reference standard has 0 harmful
verdicts out of 192.

So four numbers get reported together, and the report says which one to believe and why:

  raw agreement   what happened, uninterpretable on its own
  Cohen's kappa   chance-corrected against each rater's own marginals
  kappa_max       the highest kappa these marginals permit -- kappa/kappa_max is the share of
                  the attainable agreement actually reached, which is the fair reading when the
                  marginals are fixed by the world rather than by the rater
  PABAK           chance-corrected against a uniform prior instead, so prevalence cannot
                  suppress it -- optimistic where kappa is pessimistic, and reported as the
                  other bound rather than as the answer

Krippendorff's alpha is computed as well, for one specific reason: it handles missing codings
natively. A judge run over an API drops turns -- a filter, a timeout, a malformed verdict -- and
every kappa formulation requires dropping those units from both raters, which quietly changes
the denominator. Alpha does not.

No scipy and no sklearn. Each estimator is short, and each is tested against a worked example
whose value is arrived at by hand in the test's docstring, so a reader can check the
implementation rather than trusting that the right library function was called.
"""

import random
from collections import Counter
from dataclasses import dataclass

from validity.intervals import Interval, wilson

# Disagreement weights over the four policy grades, for `weighted_kappa`.
#
# The four grades are nominal to a regex and ordinal to a customer. Telling someone the
# superseded policy (`wrong`) and hedging between both policies (`confused`) are both harmful
# and are near-substitutes as errors; scoring a correct reply as an abstention is a mistake
# that costs nothing but a false alarm. Unweighted kappa treats all twelve off-diagonal
# confusions as identical, which understates a judge whose only disagreements are inside the
# harmful pair and overstates one that confuses `correct` with `wrong`.
#
# Weights are disagreement costs on 0-1, zero on the diagonal, and deliberately coarse: they
# encode an ordering the source project's own HARMFUL grouping already asserts, not a
# calibrated loss. The cut-score analysis is where a defensible cost ratio has to be argued.
HARM_WEIGHTS = {
    ("correct", "wrong"): 1.0,
    ("correct", "confused"): 1.0,
    ("correct", "abstained"): 0.5,
    ("wrong", "confused"): 0.25,
    ("wrong", "abstained"): 0.75,
    ("confused", "abstained"): 0.75,
}

# Landis & Koch's bands, kept because readers expect them and labelled because they are worse
# than they look: they were proposed as "arbitrary but useful divisions" for two raters on a
# balanced dichotomy, and this data is neither. The report prints the band and the caveat
# together rather than letting a number pick up an adjective on its own.
BANDS = (
    (0.81, "almost perfect"),
    (0.61, "substantial"),
    (0.41, "moderate"),
    (0.21, "fair"),
    (0.00, "slight"),
    (-1.01, "worse than chance"),
)

BOOTSTRAP_RESAMPLES = 5000
BOOTSTRAP_SEED = 20260828


def band(kappa: float) -> str:
    for floor, label in BANDS:
        if kappa >= floor:
            return label
    return BANDS[-1][1]


@dataclass(frozen=True)
class Matrix:
    """A cross-tabulation of two raters over the same units.

    `rows` is the reference standard and `cols` the rater under test, and the asymmetry is
    load-bearing: sensitivity, specificity and the bias index all read one direction, and a
    transposed matrix returns plausible-looking wrong answers. So the two are named at
    construction rather than passed positionally at each call site.
    """

    categories: tuple[str, ...]
    counts: dict[tuple[str, str], int]
    reference_label: str = "reference"
    rater_label: str = "rater"

    @property
    def n(self) -> int:
        return sum(self.counts.values())

    def get(self, row: str, col: str) -> int:
        return self.counts.get((row, col), 0)

    def row_total(self, c: str) -> int:
        return sum(self.get(c, k) for k in self.categories)

    def col_total(self, c: str) -> int:
        return sum(self.get(k, c) for k in self.categories)

    @property
    def agreements(self) -> int:
        return sum(self.get(c, c) for c in self.categories)

    @property
    def p_observed(self) -> float:
        return self.agreements / self.n

    @property
    def p_expected(self) -> float:
        """Chance agreement under Cohen's model: each rater's own marginal distribution.

        This is the assumption people forget they are making. It treats the two raters as
        independently drawing from the frequencies they happened to use, which is why a rater
        who almost always says `correct` gets very little credit for saying `correct` when the
        reference also does.
        """
        return sum(
            (self.row_total(c) / self.n) * (self.col_total(c) / self.n) for c in self.categories
        )

    @property
    def kappa(self) -> float:
        pe = self.p_expected
        if pe == 1.0:
            # Both raters used exactly one category, and the same one. Agreement is perfect
            # and chance agreement is also perfect, so kappa is 0/0. Reported as 1.0 with the
            # reason stated in the report, because the alternative -- NaN -- propagates.
            return 1.0
        return (self.p_observed - pe) / (1 - pe)

    @property
    def p_observed_max(self) -> float:
        """The highest raw agreement these two marginal distributions allow.

        Fixing both raters' category frequencies and rearranging the table as favourably as
        possible puts min(row_c, col_c) on each diagonal cell. If the rater used `abstained`
        30 times and the reference used it 12, at least 18 of those can never be matched.
        """
        return sum(min(self.row_total(c), self.col_total(c)) for c in self.categories) / self.n

    @property
    def kappa_max(self) -> float:
        """Kappa at that maximum. The ceiling the marginals impose before the rater is judged.

        Worth reporting because it is often the whole story. A kappa of 0.55 against a ceiling
        of 0.60 is a rater making almost no correctable mistakes; the same 0.55 against a
        ceiling of 0.98 is a rater making a lot of them, and the unadorned coefficient does not
        distinguish the two cases.
        """
        pe = self.p_expected
        if pe == 1.0:
            return 1.0
        return (self.p_observed_max - pe) / (1 - pe)

    @property
    def kappa_attained(self) -> float | None:
        """kappa / kappa_max: the share of the attainable agreement actually reached."""
        km = self.kappa_max
        return None if km <= 0 else self.kappa / km

    @property
    def pabak(self) -> float:
        """Prevalence-and-bias-adjusted kappa: chance-corrected against a uniform prior.

        Generalised to k categories as (p_o - 1/k) / (1 - 1/k), which reduces to Byrt's
        2*p_o - 1 at k=2. It answers a different question from kappa -- "how much better than
        guessing uniformly" rather than "than guessing from the observed frequencies" -- and on
        skewed data it is the optimistic bound. Reported as a pair with kappa, never alone;
        quoting PABAK by itself on this data would be picking the flattering statistic.
        """
        k = len(self.categories)
        if k < 2:
            raise ValueError("PABAK needs at least two categories")
        return (self.p_observed - 1 / k) / (1 - 1 / k)

    def weighted_kappa(self, weights: dict[tuple[str, str], float] = HARM_WEIGHTS) -> float:
        """Kappa with unequal disagreement costs. See HARM_WEIGHTS for why.

        Weights are read symmetrically: a cost given for (a, b) applies to (b, a) too, since a
        confusion between two grades costs the same regardless of which rater made it. An
        unlisted off-diagonal pair costs the full 1.0, so adding a category cannot silently
        make disagreements free.
        """

        def w(a: str, b: str) -> float:
            if a == b:
                return 0.0
            return weights.get((a, b), weights.get((b, a), 1.0))

        observed = sum(
            w(a, b) * self.get(a, b) / self.n for a in self.categories for b in self.categories
        )
        expected = sum(
            w(a, b) * (self.row_total(a) / self.n) * (self.col_total(b) / self.n)
            for a in self.categories
            for b in self.categories
        )
        if expected == 0:
            return 1.0
        return 1 - observed / expected

    def collapse(self, mapping: dict[str, str], categories: tuple[str, ...]) -> "Matrix":
        """Fold the categories into coarser ones -- four grades into harmful/not, say.

        The binary collapse is the one that matches the deployment decision: nobody ships on
        "the judge distinguishes `wrong` from `confused`", they ship on "the judge catches
        replies that would mislead a customer". Kappa on the collapsed table is a different
        statistic from kappa on the full one and usually a larger number, so both are reported
        and the collapse is stated.
        """
        counts: Counter = Counter()
        for (a, b), v in self.counts.items():
            counts[(mapping[a], mapping[b])] += v
        return Matrix(
            categories=categories,
            counts=dict(counts),
            reference_label=self.reference_label,
            rater_label=self.rater_label,
        )

    def table(self) -> str:
        """The confusion matrix as text, reference down the side and rater across the top."""
        width = max(len(c) for c in self.categories) + 2
        head = "".join(f"{c:>{width}}" for c in self.categories)
        lines = [f"{'':{width}}{head}{'total':>{width}}   <- {self.rater_label}"]
        for a in self.categories:
            row = "".join(f"{self.get(a, b):>{width}}" for b in self.categories)
            lines.append(f"{a:{width}}{row}{self.row_total(a):>{width}}")
        totals = "".join(f"{self.col_total(b):>{width}}" for b in self.categories)
        lines.append(f"{'total':{width}}{totals}{self.n:>{width}}")
        lines.append(f"^-- {self.reference_label}")
        return "\n".join(lines)


def matrix(
    pairs,
    categories: tuple[str, ...] | None = None,
    *,
    reference_label: str = "reference",
    rater_label: str = "rater",
) -> Matrix:
    """Cross-tabulate (reference, rater) pairs.

    `categories` is worth passing explicitly. Inferred from the data, a category the rater
    never used and the reference never used simply vanishes -- and a four-way grade that turns
    out to be a three-way one in practice is a finding, not a detail to be normalised away by
    the tabulator.
    """
    pairs = [(a, b) for a, b in pairs]
    if not pairs:
        raise ValueError("no pairs to tabulate")
    if categories is None:
        categories = tuple(sorted({c for pair in pairs for c in pair}))
    unknown = {c for pair in pairs for c in pair} - set(categories)
    if unknown:
        raise ValueError(f"labels outside the declared categories: {sorted(unknown)}")
    return Matrix(
        categories=tuple(categories),
        counts=dict(Counter(pairs)),
        reference_label=reference_label,
        rater_label=rater_label,
    )


def krippendorff_alpha(codings, categories: tuple[str, ...] | None = None) -> float:
    """Nominal Krippendorff's alpha over units coded by two or more raters.

    `codings` is one iterable per unit, containing that unit's labels with `None` for a rater
    who did not code it. Units with fewer than two codings contribute nothing -- there is no
    pair to agree or disagree -- and are dropped rather than treated as agreement.

    Missing-data tolerance is the reason this is here rather than a third kappa. A judge run
    over an API loses turns for reasons unconnected to the reply: a rate limit, a timeout, a
    verdict that failed schema validation. Every kappa formulation handles that by dropping the
    unit from both raters, which changes the denominator silently and, if failures correlate
    with reply length or content, changes the estimate too. Alpha uses whatever pairs exist.

    Implemented via the coincidence matrix: each unit with m codings contributes 1/(m-1) to
    every ordered pair of its values, so a unit coded twice contributes exactly one pair in
    each direction and a unit coded five times does not count five times as much.
    """
    coincidence: Counter = Counter()
    for unit in codings:
        values = [v for v in unit if v is not None]
        m = len(values)
        if m < 2:
            continue
        for i, a in enumerate(values):
            for j, b in enumerate(values):
                if i != j:
                    coincidence[(a, b)] += 1 / (m - 1)

    if not coincidence:
        raise ValueError("no unit was coded by two or more raters")

    observed_categories = tuple(sorted({c for pair in coincidence for c in pair}))
    if categories is not None:
        unknown = set(observed_categories) - set(categories)
        if unknown:
            raise ValueError(f"labels outside the declared categories: {sorted(unknown)}")
        observed_categories = tuple(categories)

    total = sum(coincidence.values())
    marginal = {
        c: sum(coincidence.get((c, k), 0.0) for k in observed_categories)
        for c in observed_categories
    }

    disagreement = sum(v for (a, b), v in coincidence.items() if a != b)
    d_observed = disagreement / total

    if total <= 1:
        raise ValueError("too few pairable codings for an expected-disagreement estimate")
    d_expected = (
        sum(
            marginal[a] * marginal[b]
            for a in observed_categories
            for b in observed_categories
            if a != b
        )
        / (total * (total - 1))
    )

    if d_expected == 0:
        # Every coding is the same label. There is no disagreement to explain and no variance
        # to explain it with; alpha is undefined and 1.0 is the only non-misleading answer.
        return 1.0
    return 1 - d_observed / d_expected


@dataclass(frozen=True)
class Screening:
    """The judge read as a screening test for grader errors, not as a rater.

    This is the framing that carries the deployment decision. Nobody deploys a judge to produce
    a kappa; they deploy it to decide which replies a human still has to read. So the question
    is a diagnostic one -- of the turns the grader got wrong, how many does the judge flag, and
    how much clean work does it flag along with them.

    The positive class is "the original grader's label disagrees with the reference standard",
    which held for 26 of 216 turns. At 12% prevalence, positive predictive value is bounded low
    even for an excellent test, and it is the number a reviewer's time is actually spent on --
    so it is reported next to sensitivity rather than left to be inferred from it.
    """

    true_positive: int
    false_positive: int
    false_negative: int
    true_negative: int
    confidence: float = 0.95

    @property
    def n(self) -> int:
        return self.true_positive + self.false_positive + self.false_negative + self.true_negative

    @property
    def positives(self) -> int:
        return self.true_positive + self.false_negative

    @property
    def negatives(self) -> int:
        return self.false_positive + self.true_negative

    @property
    def prevalence(self) -> float:
        return self.positives / self.n

    @property
    def sensitivity(self) -> Interval:
        """Of the real grader errors, the share the judge flagged. Wilson, because 26 is small."""
        return wilson(self.true_positive, self.positives, self.confidence)

    @property
    def specificity(self) -> Interval:
        return wilson(self.true_negative, self.negatives, self.confidence)

    @property
    def precision(self) -> Interval | None:
        """Positive predictive value: of the flagged turns, the share worth re-reading.

        None when the judge flagged nothing at all -- a perfectly possible outcome for a judge
        that agrees with the grader everywhere, and one that must not be reported as a
        precision of 0 or 1.
        """
        flagged = self.true_positive + self.false_positive
        return None if flagged == 0 else wilson(self.true_positive, flagged, self.confidence)

    @property
    def review_load(self) -> float:
        """Share of all turns the judge sends to a human. The cost side of the trade-off."""
        return (self.true_positive + self.false_positive) / self.n


def screening(reference_error, judge_flag, confidence: float = 0.95) -> Screening:
    """Build a Screening from two aligned boolean sequences."""
    reference_error = list(reference_error)
    judge_flag = list(judge_flag)
    if len(reference_error) != len(judge_flag):
        raise ValueError("sequences have different lengths")
    if not reference_error:
        raise ValueError("no observations")
    counts = Counter(zip(map(bool, reference_error), map(bool, judge_flag)))
    return Screening(
        true_positive=counts[(True, True)],
        false_positive=counts[(False, True)],
        false_negative=counts[(True, False)],
        true_negative=counts[(False, False)],
        confidence=confidence,
    )


def bootstrap(pairs, statistic, *, confidence: float = 0.95, resamples: int = BOOTSTRAP_RESAMPLES,
              seed: int = BOOTSTRAP_SEED) -> tuple[float, float]:
    """Percentile bootstrap interval for a statistic of a list of paired labels.

    A bootstrap rather than kappa's asymptotic variance, for two reasons. The closed-form
    variance is derived under a normal approximation that is poor when a category is nearly
    empty, which describes every table here -- the reference standard has zero `wrong` and zero
    `confused` verdicts. And the same routine then covers kappa_max, weighted kappa and alpha,
    none of which have a convenient variance at all, so the intervals in the report are all
    computed the same way instead of one per estimator.

    The seed is fixed and stated so the published interval is reproducible. Resampling units,
    not cells: a turn is the thing that was sampled.
    """
    pairs = list(pairs)
    if len(pairs) < 2:
        raise ValueError("not enough units to resample")
    rng = random.Random(seed)
    n = len(pairs)
    values = []
    for _ in range(resamples):
        sample = [pairs[rng.randrange(n)] for _ in range(n)]
        try:
            values.append(statistic(sample))
        except (ValueError, ZeroDivisionError):
            # A resample can land on a single category and make the statistic undefined. Those
            # draws are dropped rather than substituted, and the count is checked below --
            # silently replacing them with 1.0 would inflate the upper bound exactly where the
            # data is thinnest.
            continue
    if len(values) < resamples // 2:
        raise ValueError(
            f"only {len(values)} of {resamples} resamples produced a value; the table is too "
            "sparse for a bootstrap interval"
        )
    values.sort()
    lo = (1 - confidence) / 2
    return (
        values[int(lo * len(values))],
        values[min(len(values) - 1, int((1 - lo) * len(values)))],
    )
