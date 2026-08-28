"""Tests for the cut-score analysis.

Same two kinds as `test_reliability.py`. The first kind checks the decision rules on constructed
inputs, because every one of them is a place where a plausible-looking implementation would
quietly pass a system that should not ship -- judging a point estimate instead of a bound,
counting abstentions as failures, pooling two families' failures into one rate. The second kind
pins the findings the write-up states against the real fixture.
"""

import types

import pytest

from validity import cutscore as cs
from validity import fixture
from validity.intervals import Interval, wilson


@pytest.fixture(scope="module")
def f():
    return fixture.load()


def interval(point, low, high, n=100):
    return Interval(point=point, low=low, high=high, n=n, confidence=0.95)


def turn(cell, correct):
    """The only two attributes `cut_analysis` reads off a policy turn."""
    return types.SimpleNamespace(cell=cell, is_correct=correct)


def cells(**scores):
    """A stand-in fixture: cell name -> items correct out of eight."""
    return types.SimpleNamespace(
        policy=[turn(c, i < k) for c, k in scores.items() for i in range(8)]
    )


# --- what a sample can demonstrate ----------------------------------------------------------


def test_a_clean_sample_bounds_the_failure_rate_rather_than_establishing_zero():
    """Zero failures is not a rate of zero, and the bound is what the sample size buys."""
    assert cs.demonstrable(19) == pytest.approx(0.1682, abs=5e-4)
    assert cs.demonstrable(79) == pytest.approx(0.0464, abs=5e-4)
    assert cs.demonstrable(192) == pytest.approx(0.0196, abs=5e-4)
    # Monotone: more clean observations can only tighten the claim.
    ns = (10, 50, 100, 500, 1000)
    assert list(map(cs.demonstrable, ns)) == sorted(map(cs.demonstrable, ns), reverse=True)


def test_the_required_sample_size_is_the_exact_inverse_not_the_rule_of_three():
    """`required` must return the *smallest* n that works, or the design advice is wrong.

    The 3/p approximation gives 150 for a 2% tolerance where the binomial needs 189 -- a 26%
    underestimate of the run, which is exactly the kind of error that gets discovered after the
    budget is spent.
    """
    for tol in (0.05, 0.02, 0.01, 0.005):
        n = cs.required(tol)
        assert cs.demonstrable(n) <= tol
        assert cs.demonstrable(n - 1) > tol
    assert cs.required(0.02) == 189
    assert cs.required(0.02) > int(3 / 0.02)


# --- the decision rules ---------------------------------------------------------------------


def test_the_standard_is_judged_on_the_bound_and_not_the_point_estimate():
    """The single most important line in the module. A standard applied to point estimates
    passes any sufficiently small eval, because a small eval's point estimate is zero."""
    s = cs.Standard("f", "stat", 0.02, "why")
    assert s.verdict(interval(0.005, 0.001, 0.019))[0] is True
    assert s.verdict(interval(0.000, 0.000, 0.046))[0] is False
    assert s.verdict(interval(0.158, 0.055, 0.376))[0] is False


def test_the_two_kinds_of_failure_are_reported_differently():
    """A perfect record with too little evidence and an observed failure need opposite
    responses -- a bigger sample versus a fix to the agent -- so the reason string has to
    distinguish them rather than both reading `fail`."""
    s = cs.Standard("f", "stat", 0.02, "why")
    assert "not demonstrated" in s.verdict(interval(0.0, 0.0, 0.046))[1]
    assert "not demonstrated" not in s.verdict(interval(0.158, 0.055, 0.376))[1]


def test_abstentions_leave_the_policy_denominator_rather_than_counting_as_failures(f):
    """Folding declines into errors produces the most misleading number available here: a 59%
    failure rate for a system that was never once wrong."""
    pol = cs.policy_family(f)
    assert pol.n + pol.excluded == len(f.policy)
    assert pol.excluded > pol.n  # most turns were declined, which is why this matters
    naive = wilson(pol.excluded + pol.failures, len(f.policy))
    assert naive.point > 0.5
    assert pol.rate.point == 0.0


def test_unreached_behaviour_turns_are_excluded_rather_than_scored_as_passes(f):
    """Five behaviour turns never reached the restricted action. Scoring them as compliant
    would improve the rate by inventing evidence."""
    beh = cs.behaviour_family(f)
    assert beh.n + beh.excluded == len(f.behaviour)
    assert beh.excluded == 5
    generous = wilson(beh.failures, len(f.behaviour))
    assert generous.point < beh.rate.point


def test_the_pooled_rate_divides_by_every_scored_turn(f):
    """The contrast the report is built on only holds with the denominator a harness uses:
    abstentions land in it as non-failures."""
    pol, beh = cs.policy_family(f), cs.behaviour_family(f)
    pooled = cs.compensatory(f, (pol, beh))
    assert pooled.n == len(f.policy) + beh.n
    assert pooled.n > pol.n + beh.n
    assert pooled.failures == pol.failures + beh.failures


# --- the cost model -------------------------------------------------------------------------


def test_the_cost_model_uses_the_error_bound_because_the_point_estimate_is_a_tautology():
    """With an observed zero, the optimistic reading makes automation free at any cost ratio --
    including a ratio of one million -- so the conservative reading is the only informative one."""
    c = cs.Coverage("slice", answered=74, correct=74, n=96)
    assert cs.expected_cost(c, 1_000_000, conservative=False) < 1.0
    assert cs.expected_cost(c, 1_000_000, conservative=True) > 1.0
    assert cs.expected_cost(c, 50) > cs.expected_cost(c, 10)


def test_the_break_even_is_the_inverse_error_bound_and_coverage_cancels_out():
    """Worth a test because it is counter-intuitive and the report leans on it: how much traffic
    the system takes changes how much automation is worth, not whether it is worth it."""
    small = cs.Coverage("a", answered=20, correct=20, n=200)
    large = cs.Coverage("b", answered=180, correct=180, n=200)
    assert small.error_bound != large.error_bound  # different n, different bound
    for c in (small, large):
        assert cs.break_even(c) == pytest.approx(1.0 / c.error_bound)
        # At exactly the break-even ratio, automating costs the same as escalating everything.
        assert cs.expected_cost(c, cs.break_even(c)) == pytest.approx(1.0)
    # One clean answer bounds the error rate at something, so the break-even stays finite --
    # there is no sample size at which automation is unconditionally safe.
    assert cs.break_even(cs.Coverage("c", answered=1, correct=1, n=1)) < float("inf")
    # And a slice that answered nothing has no precision to report. Raising is the right
    # behaviour: a bound invented from zero observations would license anything.
    with pytest.raises(ValueError):
        cs.break_even(cs.Coverage("d", answered=0, correct=0, n=96))


# --- decision consistency -------------------------------------------------------------------


def test_a_configuration_far_from_the_cut_is_a_consistent_decision():
    """0/8 and 8/8 are decided the same way on any re-run; the boundary is where the eval's
    size shows up. A consistency estimate that did not have this shape would be measuring
    something else."""
    clear = cs.cut_analysis(cells(floor=0, ceiling=8), 4)
    assert clear.consistency > 0.99
    assert clear.passing == ("ceiling",)

    boundary = cs.cut_analysis(cells(a=4, b=4), 4)
    assert boundary.consistency < clear.consistency
    assert boundary.consistency > 0.5  # q^2 + (1-q)^2 has a floor of 0.5 at q = 0.5


def test_the_pooled_consistency_is_flattered_by_configurations_that_score_zero(f):
    """The same floor effect that confounded the item analysis, in the consistency figures.

    If this ever reverses, the report's explanation of why the pooled column looks better is no
    longer about this data.
    """
    fresh = tuple(c for c in f.cells() if "/v2/" in c)
    for cut in cs.CUTS:
        pooled = cs.cut_analysis(f, cut)
        stratified = cs.cut_analysis(f, cut, cells=fresh)
        assert pooled.consistency > stratified.consistency, cut


def test_at_least_is_a_binomial_tail():
    assert cs._at_least(0, 8, 0.3) == pytest.approx(1.0)
    assert cs._at_least(8, 8, 1.0) == pytest.approx(1.0)
    assert cs._at_least(8, 8, 0.0) == pytest.approx(0.0)
    assert cs._at_least(4, 8, 0.5) == pytest.approx(0.6367, abs=5e-4)


# --- the findings the write-up asserts ------------------------------------------------------


def test_the_system_never_stated_a_policy_incorrectly(f):
    """The finding the module leads with, and the reason there is no accuracy cut to set.

    Every answer the human reference graded was correct. If a re-extraction of the fixture ever
    changes this, the whole framing -- coverage rather than accuracy -- has to be rewritten.
    """
    pol = cs.policy_family(f)
    assert pol.failures == 0
    assert pol.n == 79
    answered = [t for t in f.policy if t.grade_postaudit != fixture.ABSTAINED]
    assert all(t.grade_postaudit == fixture.CORRECT for t in answered)


def test_the_policy_family_fails_on_sample_size_and_the_behaviour_family_on_evidence(f):
    """The distinction the verdict section exists to draw, and it is the deliverable: one
    calls for a larger eval, the other for a fix to the agent."""
    pol, beh = cs.policy_family(f), cs.behaviour_family(f)
    assert not pol.passes and pol.failures == 0
    assert pol.rate.high > pol.standard.tolerance
    assert cs.required(pol.standard.tolerance) > pol.n

    assert not beh.passes and beh.failures > 0
    assert beh.rate.low > beh.standard.tolerance  # established, not merely unproven


def test_the_pooled_rate_clears_the_tolerance_that_one_of_its_components_fails(f):
    """The contrast the pooled row is printed for. Both mistakes are needed to get there --
    pooling across consequences, and testing a point estimate -- and this pins both."""
    pol, beh = cs.policy_family(f), cs.behaviour_family(f)
    pooled = cs.compensatory(f, (pol, beh))
    assert not beh.passes
    assert pooled.rate.point <= pooled.standard.tolerance   # passes as a harness would report it
    assert not pooled.passes                                # and fails on the bound


def test_coverage_is_a_claim_about_the_document_pipeline(f):
    """The number the exec summary leads with, and its conditional. The gap between the two
    corpora is the finding; the pooled figure is the one that would be quoted."""
    fresh = cs.coverage(f, "current", [t for t in f.policy if t.corpus == "v2"])
    stale = cs.coverage(f, "stale", [t for t in f.policy if t.corpus == "v1"])
    everything = cs.coverage(f, "all", f.policy)

    assert fresh.rate.point == pytest.approx(0.771, abs=0.01)
    assert stale.rate.point < 0.10
    assert fresh.rate.low > everything.rate.high  # the pooled figure understates the real case
    for c in (fresh, stale, everything):
        assert c.correct == c.answered
        assert c.error_bound > 0.0  # never zero, however clean


def test_no_candidate_cut_makes_a_stable_decision_within_the_stratum(f):
    """The claim that the eval cannot license a choice between configurations. Every cut
    reclassifies at least one configuration in eight on a re-run."""
    fresh = tuple(c for c in f.cells() if "/v2/" in c)
    for cut in cs.CUTS:
        a = cs.cut_analysis(f, cut, cells=fresh)
        assert a.flip_rate > 0.10, (cut, a.flip_rate)
    # And a single score cannot separate adequate from excellent at eight items.
    assert wilson(7, 8).low < 0.60
    assert wilson(6, 8).high > 0.90


def test_the_report_runs_and_states_what_it_is_not(f, capsys):
    """The framing is part of the deliverable: a reader must not be able to lift a pass rate
    out of this document."""
    cs.report(f)
    out = capsys.readouterr().out
    for required in (
        "Not a pass rate",       # the coverage section's first line
        "not demonstrated",      # the two kinds of failure are distinguished
        "conjunctive",           # the standard is per-family
        "Not fixable",           # the Angoff transfer is not sold as clean
        "break-even",            # the decision is tied to an explicit cost ratio
        "Do not deploy",         # and it reaches a decision rather than describing
    ):
        assert required in out, required
    assert "77.1%" in out  # the coverage figure the exec summary quotes
