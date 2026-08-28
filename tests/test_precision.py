"""Tests for the precision re-analysis.

The estimators are tested in `test_intervals.py`. What is tested here is the analysis on top
of them: that the contrasts are oriented the way the source table reads, that the stratified
version restricts to the arm it claims to, and that the two conclusions this study actually
draws from the fixture -- one null, one fragile bound -- are the ones the code reports.
"""

import pytest

from validity import fixture, precision


@pytest.fixture(scope="module")
def f():
    return fixture.load()


def test_marginals_cover_every_level_of_every_axis(f):
    """Nine levels: three models, two each of prompt, corpus, retriever."""
    rows = precision.marginals(f)
    assert len(rows) == 9
    assert {a for a, _l, _i in rows} == set(fixture.AXES)
    # Every marginal is a 64 or 96 turn slice; anything else means a level was mis-split.
    assert {i.n for _a, _l, i in rows} == {64, 96}


def test_contrasts_are_oriented_so_positive_means_the_first_level_won(f):
    """The corpus contrast is the unambiguous one: v2 is better, so it must come out positive.

    A sign flip here would silently invert every conclusion in the report while leaving all
    the interval arithmetic correct, which is the kind of error no interval test catches.
    """
    d = {a: diff for a, _h, _l, _p, diff in precision.contrasts(f)}
    assert d["corpus"].point == pytest.approx(0.71875)
    assert d["corpus"].low > 0


def test_the_prompt_axis_is_the_one_null_and_it_is_underpowered(f):
    """The source README's "no measurable difference", restated as a claim about the design.

    Both halves are asserted: the interval spans zero, and the resolvable effect is large
    enough that the null carries little information. If a fixture change ever made this
    contrast separate from zero, the report's central worked example would be stale.
    """
    d = {a: diff for a, _h, _l, _p, diff in precision.contrasts(f)}
    assert d["prompt"].includes_zero
    assert d["prompt"].resolvable > 10
    assert [a for a, _h, _l, _p, diff in precision.contrasts(f) if diff.includes_zero] == [
        "prompt"
    ]


def test_the_retriever_finding_is_the_fragile_one(f):
    """Clears zero by under 2 points -- inside the scale of the 26-turn audit.

    Singled out because it is the finding this analysis qualifies rather than confirms or
    overturns, and the qualification is the useful output.
    """
    d = {a: diff for a, _h, _l, _p, diff in precision.contrasts(f)}
    margin = 100 * min(abs(d["retriever"].low), abs(d["retriever"].high))
    assert not d["retriever"].includes_zero
    assert margin < precision.FRAGILE_MARGIN_POINTS
    # And no other contrast is fragile, so the report's fragile section has exactly one entry.
    others = [
        a
        for a, _h, _l, _p, diff in precision.contrasts(f)
        if a != "retriever"
        and not diff.includes_zero
        and 100 * min(abs(diff.low), abs(diff.high)) < precision.FRAGILE_MARGIN_POINTS
    ]
    assert others == []


def test_stratified_drops_the_dominant_axis_and_halves_each_arm(f):
    """Restricting to corpus=v2 leaves 96 turns, 48 per arm on every remaining axis.

    Except model, which has three levels -- so the two-level contrast arms are 32 each. The
    check is that the arms are equal and add to no more than the stratum, which is what makes
    the difference interval legitimate.
    """
    rows = precision.stratified(f)
    assert {a for a, _h, _l, _d in rows} == {"model", "prompt", "retriever"}
    stratum = [t for t in f.policy if t.corpus == precision.DOMINANT_LEVEL]
    assert len(stratum) == 96
    for axis, _high, _low, d in rows:
        assert d.a.n == d.b.n, axis
        assert d.a.n + d.b.n <= len(stratum), axis


def test_stratifying_widens_every_interval(f):
    """The cost of the stratified view, asserted so the report cannot claim it for free.

    Half the sample must produce a wider interval on every axis. If one narrowed, the strata
    are not nested the way the argument assumes.
    """
    pooled = {a: d for a, _h, _l, _p, d in precision.contrasts(f)}
    for axis, _high, _low, d in precision.stratified(f):
        assert d.high - d.low > pooled[axis].high - pooled[axis].low, axis


def test_the_floor_arm_really_is_a_floor(f):
    """The premise of the whole stratified section.

    If corpus=v1 were merely worse rather than at the floor, pooling it would not compress
    the other axes and the stratified analysis would be unmotivated. 5/96 with a ceiling of
    under 12% is a floor.
    """
    correct, n = fixture.accuracy(t for t in f.policy if t.corpus == "v1")
    assert (correct, n) == (5, 96)
    from validity import intervals

    assert intervals.wilson(correct, n).high < 0.12


def test_report_runs_over_the_real_fixture(f, capsys):
    """A smoke test on the entry point: every f-string interpolates, every table populates.

    Cheap, and it is the only thing standing between a formatting error and a published
    document with a KeyError in it.
    """
    precision.report(f)
    out = capsys.readouterr().out
    assert "Precision of the published findings" in out
    assert "corpus=v2" in out
    assert "{" not in out  # an unformatted placeholder that escaped
    assert "None:" not in out  # the fragile section found its one entry
