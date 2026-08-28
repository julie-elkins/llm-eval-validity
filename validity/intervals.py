"""Interval estimates for proportions, because a pass rate without one is not a result.

Every number this study inherits is a proportion over 64, 96 or 192 observations, and
several of the source project's published comparisons are differences between two of them.
The normal approximation is wrong at exactly the sizes that matter here -- it produces
intervals that run below 0% for the 5/96 cell -- so the Wilson score interval is used
throughout, and the one place a difference is tested uses the Newcombe hybrid built from
two Wilson intervals for the same reason.

No scipy: the only quantile needed is the standard normal's, and hard-coding the three
conventional values is more honest than a dependency that hides which one was used.
"""

from dataclasses import dataclass

# Two-sided normal quantiles. Enumerated rather than computed so that a caller cannot
# silently request a confidence level this module has never been tested at.
Z = {0.90: 1.6448536269514722, 0.95: 1.959963984540054, 0.99: 2.5758293035489004}


@dataclass(frozen=True)
class Interval:
    """A point estimate with bounds, all on the 0-1 scale."""

    point: float
    low: float
    high: float
    n: int
    confidence: float

    @property
    def width(self) -> float:
        return self.high - self.low

    @property
    def half_width(self) -> float:
        """The plus-or-minus a reader expects, in percentage points.

        Wilson intervals are asymmetric about the point estimate, so this is the larger of
        the two arms rather than half the width -- a reader who takes "+/- 14 points" and
        reconstructs the interval should not end up with a narrower one than was computed.
        """
        return 100 * max(self.point - self.low, self.high - self.point)

    def pct(self) -> str:
        return f"{100 * self.point:.1f}% [{100 * self.low:.1f}, {100 * self.high:.1f}]"


def wilson(successes: int, n: int, confidence: float = 0.95) -> Interval:
    """Wilson score interval for a binomial proportion.

    Chosen over the Wald interval because every interesting cell here is small or extreme.
    On the 5/96 corpus-v1 cell Wald gives [0.6%, 9.8%]; on a 0/8 cell it gives the
    degenerate [0, 0], which would let a category with no evidence at all pass a threshold
    test. Wilson stays inside [0, 1] and never collapses to a point.
    """
    if n <= 0:
        raise ValueError("no observations")
    if not 0 <= successes <= n:
        raise ValueError(f"{successes} successes out of {n}")
    if confidence not in Z:
        raise ValueError(f"untested confidence level {confidence}; have {sorted(Z)}")

    z = Z[confidence]
    p = successes / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    spread = z * ((p * (1 - p) / n + z**2 / (4 * n**2)) ** 0.5) / denom

    # Wilson's bounds always straddle the point estimate, but at 0 and n successes the two
    # terms above are algebraically equal and differ only in the last bits -- at k=0, n=96
    # the lower bound arrives as 3.5e-18 rather than 0. Clamping against `p` as well as
    # against [0, 1] enforces the invariant the caller relies on, instead of leaving a
    # sub-attometre violation for a comparison two modules away to trip over.
    return Interval(
        point=p,
        low=min(p, max(0.0, centre - spread)),
        high=max(p, min(1.0, centre + spread)),
        n=n,
        confidence=confidence,
    )


@dataclass(frozen=True)
class Difference:
    """A difference of two proportions, with the interval that decides whether it is real."""

    point: float
    low: float
    high: float
    a: Interval
    b: Interval
    confidence: float

    @property
    def includes_zero(self) -> bool:
        return self.low <= 0 <= self.high

    @property
    def resolvable(self) -> float:
        """The smallest difference this design could have distinguished from zero, in points.

        Reported alongside every null result. "No measurable difference" is a claim about
        the instrument as much as about the thing measured, and this is the number that says
        which.
        """
        return 100 * max(abs(self.low - self.point), abs(self.high - self.point))

    def pct(self) -> str:
        return f"{100 * self.point:+.1f} points [{100 * self.low:+.1f}, {100 * self.high:+.1f}]"


def difference(
    successes_a: int, n_a: int, successes_b: int, n_b: int, confidence: float = 0.95
) -> Difference:
    """Newcombe's hybrid-score interval for p_a - p_b.

    Built from the two Wilson intervals rather than from a pooled normal approximation, so
    it inherits Wilson's behaviour at the extremes: the corpus contrast here is 5/96 against
    74/96, where a Wald difference interval is unreliable in both tails at once.
    """
    a = wilson(successes_a, n_a, confidence)
    b = wilson(successes_b, n_b, confidence)
    point = a.point - b.point
    # The bounds pair each proportion's worst case against the other's, which is what makes
    # this conservative rather than merely convenient.
    low = point - ((a.point - a.low) ** 2 + (b.high - b.point) ** 2) ** 0.5
    high = point + ((a.high - a.point) ** 2 + (b.point - b.low) ** 2) ** 0.5
    return Difference(
        point=point,
        low=max(-1.0, low),
        high=min(1.0, high),
        a=a,
        b=b,
        confidence=confidence,
    )


def n_for_half_width(target_points: float, p: float = 0.5, confidence: float = 0.95) -> int:
    """How many observations a category needs to be measured to +/- `target_points`.

    The question every customer asks about an eval set and almost no published harness
    answers. Defaults to p=0.5 because that is the worst case: a proportion near a half has
    the widest interval, so sizing against it is the promise that holds wherever the true
    rate lands. Uses the normal approximation deliberately -- it is the conservative
    direction for sample size, and a reader planning a run wants a round number, not a
    root-finding routine.
    """
    if not 0 < target_points < 100:
        raise ValueError("target half-width must be in (0, 100) percentage points")
    z = Z[confidence]
    target = target_points / 100
    return int(-(-(z**2 * p * (1 - p) / target**2) // 1))
