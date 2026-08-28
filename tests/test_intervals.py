"""Tests for the interval estimators.

Every expected value here is either a textbook figure for the Wilson interval or derived by
hand in the docstring. None of them was produced by running this module and pasting the
output, which is the failure mode that makes a statistics test worthless: it pins the
behaviour without ever checking the formula.
"""

import pytest

from validity import intervals


def test_wilson_matches_the_textbook_symmetric_case():
    """p=0.5, n=100, 95% is the worked example every reference carries: [40.4%, 59.6%].

    Symmetric only because the point estimate is exactly a half; asserting it first means a
    sign error in the spread term shows up before any asymmetric case is trusted.
    """
    i = intervals.wilson(50, 100)
    assert i.point == 0.5
    assert round(i.low, 4) == 0.4038
    assert round(i.high, 4) == 0.5962


def test_wilson_at_zero_successes_is_bounded_and_not_degenerate():
    """0/10 is [0, 27.8%], not [0, 0].

    This is the whole reason Wilson is used here rather than Wald. A category that observed
    no successes has not established that its rate is zero, and an interval that says it has
    would let an empty category clear a threshold in the cut-score analysis.
    """
    i = intervals.wilson(0, 10)
    assert i.low == 0.0
    assert round(i.high, 4) == 0.2775
    assert i.width > 0


def test_wilson_never_leaves_the_unit_interval_anywhere_it_is_used():
    """The property Wald violates at the sizes this study actually has.

    Swept over every denominator the source run produces (8 per cell, 64 per model, 96 per
    axis level, 192 overall) at every possible success count.
    """
    for n in (8, 64, 96, 192):
        for k in range(n + 1):
            i = intervals.wilson(k, n)
            assert 0.0 <= i.low <= i.point <= i.high <= 1.0, (k, n)


def test_half_width_reports_the_larger_arm_not_half_the_width():
    """A reader reconstructing the interval from "+/- x" must not get a narrower one.

    Wilson is asymmetric away from p=0.5, so half the width understates one side. 5/96 --
    the corpus-v1 cell -- is far enough from a half for the two to differ.
    """
    i = intervals.wilson(5, 96)
    assert i.point - i.low != pytest.approx(i.high - i.point)
    assert i.half_width == pytest.approx(100 * max(i.point - i.low, i.high - i.point))
    assert i.half_width >= 100 * i.width / 2


def test_difference_of_identical_proportions_is_centred_on_zero_and_includes_it():
    i = intervals.difference(48, 96, 48, 96)
    assert i.point == 0.0
    assert i.includes_zero


def test_difference_separates_the_corpus_contrast_from_zero():
    """5/96 against 74/96 is the source project's largest effect; it must clear zero easily.

    The control on the null result below: if the method could not detect this, it could not
    detect anything, and a null elsewhere would say nothing about the thing measured.
    """
    d = intervals.difference(74, 96, 5, 96)
    assert d.point == pytest.approx(0.71875)
    assert not d.includes_zero
    assert d.low > 0.55


def test_difference_does_not_separate_the_prompt_contrast_from_zero():
    """41/96 against 38/96 -- the axis the source README calls "no measurable difference".

    The interval is what turns that phrase into a claim about the instrument: it spans zero,
    and `resolvable` says how large an effect this design could have found.
    """
    d = intervals.difference(41, 96, 38, 96)
    assert d.includes_zero
    assert 10 < d.resolvable < 20


def test_sample_size_for_five_points_is_the_conventional_385():
    """z^2 * 0.25 / 0.05^2 = 384.16, rounded up. The number every survey text quotes."""
    assert intervals.n_for_half_width(5) == 385


def test_sample_size_grows_quadratically_as_the_target_tightens():
    """Halving the target half-width quadruples the requirement.

    Stated as a test because it is the point of the whole sizing argument: an eval set of 8
    per cell is not "a bit small" for a 5-point question, it is off by two orders of
    magnitude.
    """
    assert intervals.n_for_half_width(10) == 97
    assert intervals.n_for_half_width(5) == 385
    assert intervals.n_for_half_width(2.5) == 1537


def test_untested_confidence_level_is_refused():
    """Better a loud failure than a quantile nobody checked."""
    with pytest.raises(ValueError, match="untested confidence"):
        intervals.wilson(5, 96, confidence=0.975)


def test_impossible_counts_are_refused():
    with pytest.raises(ValueError):
        intervals.wilson(97, 96)
    with pytest.raises(ValueError):
        intervals.wilson(-1, 96)
    with pytest.raises(ValueError, match="no observations"):
        intervals.wilson(0, 0)
