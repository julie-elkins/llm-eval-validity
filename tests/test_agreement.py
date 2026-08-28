"""Tests for the agreement statistics.

Every estimator is checked against a case whose value is derived by hand in the docstring, not
against this module's own output on the real data. Two of them are the published tables from
Feinstein and Cicchetti's 1990 paradox papers, which is the one comparison that matters here:
this study's reference standard has a category holding almost all the mass, so the paradox is
the operating regime rather than a footnote.
"""

import pytest

from validity import agreement as a

GRADES = ("correct", "wrong", "confused", "abstained")


def counts_to_pairs(counts):
    """Expand a {(reference, rater): n} table into the pair list the estimators take."""
    return [pair for pair, n in counts.items() for _ in range(n)]


# --- Cohen's kappa --------------------------------------------------------------------------


def test_kappa_matches_a_hand_computed_two_by_two():
    """a=20 b=5 / c=10 d=15, N=50.

    p_o = (20+15)/50 = 0.70.
    Reference rows: yes 25, no 25. Rater columns: yes 30, no 20.
    p_e = (25/50)(30/50) + (25/50)(20/50) = 0.30 + 0.20 = 0.50.
    kappa = (0.70 - 0.50) / (1 - 0.50) = 0.40.
    """
    m = a.matrix(
        counts_to_pairs({("yes", "yes"): 20, ("yes", "no"): 5, ("no", "yes"): 10, ("no", "no"): 15}),
        categories=("yes", "no"),
    )
    assert m.n == 50
    assert m.p_observed == pytest.approx(0.70)
    assert m.p_expected == pytest.approx(0.50)
    assert m.kappa == pytest.approx(0.40)


def test_kappa_is_one_for_perfect_agreement_and_zero_for_chance():
    m = a.matrix([("x", "x")] * 10 + [("y", "y")] * 10, categories=("x", "y"))
    assert m.kappa == pytest.approx(1.0)

    # Independent raters each using both labels half the time: p_o = p_e = 0.5.
    chance = a.matrix(
        counts_to_pairs({("x", "x"): 25, ("x", "y"): 25, ("y", "x"): 25, ("y", "y"): 25}),
        categories=("x", "y"),
    )
    assert chance.kappa == pytest.approx(0.0)


def test_kappa_is_defined_when_both_raters_used_one_category():
    """The degenerate table this study can actually produce.

    If a judge and the reference standard both label all 192 turns `correct`, p_e = 1 and kappa
    is 0/0. NaN would propagate through every sort and comparison downstream, so 1.0 is
    returned and the report is responsible for saying that agreement was perfect and
    uninformative.
    """
    m = a.matrix([("correct", "correct")] * 20, categories=("correct",))
    assert m.p_expected == pytest.approx(1.0)
    assert m.kappa == 1.0
    assert m.kappa_max == 1.0


# --- the paradox ----------------------------------------------------------------------------


def test_the_kappa_paradox_reproduces_on_feinsteins_two_tables():
    """Feinstein & Cicchetti (1990): identical raw agreement, kappa 0.70 against 0.32.

    Table A -- 40, 9 / 6, 45. p_o = 85/100 = 0.85.
      rows 49, 51; cols 46, 54.
      p_e = 0.49*0.46 + 0.51*0.54 = 0.2254 + 0.2754 = 0.5008.
      kappa = (0.85 - 0.5008) / 0.4992 = 0.3492 / 0.4992 = 0.6995.

    Table B -- 80, 5 / 10, 5. p_o = 85/100 = 0.85, the same.
      rows 85, 15; cols 90, 10.
      p_e = 0.85*0.90 + 0.15*0.10 = 0.765 + 0.015 = 0.780.
      kappa = (0.85 - 0.78) / 0.22 = 0.07 / 0.22 = 0.3182.

    Same agreement, same errors, half the kappa -- because in B one category holds 85% of the
    mass. That is this study's situation exactly, which is why the report never quotes kappa
    without kappa_max and PABAK beside it.
    """
    table_a = a.matrix(
        counts_to_pairs({("y", "y"): 40, ("y", "n"): 9, ("n", "y"): 6, ("n", "n"): 45}),
        categories=("y", "n"),
    )
    table_b = a.matrix(
        counts_to_pairs({("y", "y"): 80, ("y", "n"): 5, ("n", "y"): 10, ("n", "n"): 5}),
        categories=("y", "n"),
    )

    assert table_a.p_observed == pytest.approx(table_b.p_observed) == pytest.approx(0.85)
    assert table_a.kappa == pytest.approx(0.6995, abs=1e-4)
    assert table_b.kappa == pytest.approx(0.3182, abs=1e-4)

    # PABAK depends only on raw agreement, so it is identical for the two tables: 2(0.85) - 1.
    assert table_a.pabak == pytest.approx(0.70)
    assert table_b.pabak == pytest.approx(0.70)


def test_pabak_reduces_to_byrts_formula_at_two_categories_and_generalises_above():
    m = a.matrix(
        counts_to_pairs({("y", "y"): 8, ("y", "n"): 1, ("n", "y"): 1, ("n", "n"): 10}),
        categories=("y", "n"),
    )
    assert m.pabak == pytest.approx(2 * m.p_observed - 1)

    # Four categories: (p_o - 1/4) / (3/4). Chance is 0.25, not 0.5, so the same raw agreement
    # earns a higher PABAK -- which is why the number is meaningless without its k.
    four = a.matrix([("correct", "correct")] * 18 + [("wrong", "abstained")] * 2, categories=GRADES)
    assert four.p_observed == pytest.approx(0.9)
    assert four.pabak == pytest.approx((0.9 - 0.25) / 0.75)


def test_kappa_max_is_the_ceiling_the_marginals_impose():
    """Table B above, rearranged as favourably as its marginals allow.

    rows 85, 15; cols 90, 10. Best case diagonal: min(85,90) + min(15,10) = 85 + 10 = 95.
      p_o_max = 0.95, p_e = 0.78 (unchanged -- the marginals are fixed).
      kappa_max = (0.95 - 0.78) / 0.22 = 0.17 / 0.22 = 0.7727.

    So the observed 0.3182 is 41% of what was attainable. Table A's ceiling is far higher, and
    that difference is the thing the raw coefficient hides.
    """
    table_b = a.matrix(
        counts_to_pairs({("y", "y"): 80, ("y", "n"): 5, ("n", "y"): 10, ("n", "n"): 5}),
        categories=("y", "n"),
    )
    assert table_b.p_observed_max == pytest.approx(0.95)
    assert table_b.kappa_max == pytest.approx(0.7727, abs=1e-4)
    assert table_b.kappa_attained == pytest.approx(0.3182 / 0.7727, abs=1e-3)
    assert table_b.kappa <= table_b.kappa_max


def test_kappa_never_exceeds_its_ceiling_on_any_table():
    """The invariant that would catch a marginal being read off the wrong axis."""
    tables = [
        {("y", "y"): 40, ("y", "n"): 9, ("n", "y"): 6, ("n", "n"): 45},
        {("y", "y"): 80, ("y", "n"): 5, ("n", "y"): 10, ("n", "n"): 5},
        {("y", "y"): 1, ("y", "n"): 20, ("n", "y"): 20, ("n", "n"): 1},
        {("y", "y"): 90, ("y", "n"): 1, ("n", "y"): 8, ("n", "n"): 1},
    ]
    for counts in tables:
        m = a.matrix(counts_to_pairs(counts), categories=("y", "n"))
        assert m.kappa <= m.kappa_max + 1e-12, counts


# --- weighted kappa ------------------------------------------------------------------------


def test_weighted_kappa_with_flat_weights_is_cohens_kappa():
    """The self-consistency check. Unit cost on every off-diagonal cell is exactly Cohen's
    model, so any error in the weighting arithmetic shows up as a divergence here."""
    m = a.matrix(
        counts_to_pairs(
            {
                ("correct", "correct"): 60,
                ("correct", "abstained"): 8,
                ("wrong", "confused"): 4,
                ("abstained", "correct"): 5,
                ("abstained", "abstained"): 23,
            }
        ),
        categories=GRADES,
    )
    flat = {(x, y): 1.0 for x in GRADES for y in GRADES if x != y}
    assert m.weighted_kappa(flat) == pytest.approx(m.kappa)


def test_weighted_kappa_rewards_a_judge_whose_errors_stay_inside_the_harmful_pair():
    """Two judges with identical raw agreement and different error patterns.

    Both disagree on 8 of 100 turns. One confuses `wrong` with `confused` -- both harmful, so
    the deployment decision is unchanged. The other calls harmful replies `correct`, which is
    the error that ships. Unweighted kappa cannot tell them apart; HARM_WEIGHTS can, and this
    is the entire reason the weighted variant is in the report.
    """
    inside = a.matrix(
        counts_to_pairs(
            {("correct", "correct"): 80, ("abstained", "abstained"): 12, ("wrong", "confused"): 8}
        ),
        categories=GRADES,
    )
    across = a.matrix(
        counts_to_pairs(
            {("correct", "correct"): 80, ("abstained", "abstained"): 12, ("wrong", "correct"): 8}
        ),
        categories=GRADES,
    )
    assert inside.p_observed == pytest.approx(across.p_observed)
    assert inside.weighted_kappa() > across.weighted_kappa()


def test_an_unlisted_confusion_costs_full_weight():
    """Adding a category must not make disagreements involving it free."""
    m = a.matrix(
        counts_to_pairs({("correct", "correct"): 10, ("novel", "correct"): 5}),
        categories=("correct", "novel"),
    )
    assert m.weighted_kappa({}) == pytest.approx(m.kappa)


# --- collapsing ----------------------------------------------------------------------------


def test_collapsing_to_the_deployment_decision_preserves_the_units():
    """Four grades folded into harmful / not-harmful, which is what a rollout turns on."""
    m = a.matrix(
        counts_to_pairs(
            {
                ("correct", "correct"): 60,
                ("correct", "abstained"): 8,
                ("wrong", "confused"): 4,
                ("abstained", "correct"): 5,
                ("abstained", "abstained"): 23,
            }
        ),
        categories=GRADES,
    )
    harm = {"correct": "safe", "abstained": "safe", "wrong": "harmful", "confused": "harmful"}
    c = m.collapse(harm, ("harmful", "safe"))

    assert c.n == m.n
    # Every confusion that stayed inside a collapsed class becomes agreement: wrong/confused
    # (4, both harmful) and the two correct/abstained confusions (8 + 5, both safe). 83 -> 100.
    assert m.agreements == 83
    assert c.agreements == 100
    assert c.p_observed > m.p_observed
    # Which is the trap the report has to name: collapsing raises agreement by construction, so
    # a binary kappa is not evidence that the four-way judge worked.
    assert c.kappa > m.kappa


# --- Krippendorff's alpha ------------------------------------------------------------------


def test_alpha_matches_a_hand_computed_four_unit_case():
    """Two coders: A = [1,1,0,0], B = [1,0,0,0].

    Coincidence matrix (each of the 4 units contributes both ordered pairs):
      unit 1 (1,1) -> o[1][1] += 2
      unit 2 (1,0) -> o[1][0] += 1, o[0][1] += 1
      units 3,4 (0,0) -> o[0][0] += 4
    So o[0][0]=4, o[1][1]=2, o[0][1]=o[1][0]=1, total = 8 = 2 x 4 units.
    Marginals: n_0 = 4+1 = 5, n_1 = 1+2 = 3.
      D_o = (1 + 1) / 8 = 0.25
      D_e = (5*3 + 3*5) / (8 * 7) = 30 / 56 = 0.535714...
      alpha = 1 - 0.25/0.535714 = 1 - 0.466667 = 0.533333.

    Cohen's kappa on the same data is 0.50, and the gap is the point: alpha pools the two
    coders' marginals where kappa keeps them separate, so the two answer slightly different
    questions and neither is a substitute for the other.
    """
    codings = [("1", "1"), ("1", "0"), ("0", "0"), ("0", "0")]
    assert a.krippendorff_alpha(codings) == pytest.approx(0.5333333, abs=1e-6)
    assert a.matrix(codings, categories=("0", "1")).kappa == pytest.approx(0.50)


def test_alpha_is_one_for_perfect_agreement_and_defined_when_all_labels_match():
    assert a.krippendorff_alpha([("x", "x"), ("y", "y"), ("x", "x")]) == pytest.approx(1.0)
    # No variance at all: D_e is 0, alpha is undefined, and 1.0 is the only honest answer.
    assert a.krippendorff_alpha([("x", "x")] * 5) == 1.0


def test_alpha_uses_the_pairs_that_exist_rather_than_dropping_the_unit():
    """The property the module is here for.

    Three units where one rater's verdict is missing. Alpha ignores the unpairable unit and
    keeps the other two intact -- it does not drop the whole unit from both raters, and it does
    not score the gap as agreement.
    """
    complete = [("x", "x"), ("y", "y")]
    with_gap = [("x", "x"), ("y", "y"), ("x", None)]
    assert a.krippendorff_alpha(with_gap) == pytest.approx(a.krippendorff_alpha(complete))

    with pytest.raises(ValueError, match="two or more raters"):
        a.krippendorff_alpha([("x", None), (None, "y")])


def test_alpha_normalises_units_coded_by_more_than_two_raters():
    """The 1/(m-1) weighting, checked on a case where dropping it changes the answer.

    Units A = (x,x,x), B = (y,y), C = (x,y). Each ordered pair within a unit is weighted
    1/(m-1), so a unit coded m times contributes m to the coincidence total -- not m(m-1).

      A: m=3, six ordered pairs at 1/2   -> o[x][x] += 3
      B: m=2                             -> o[y][y] += 2
      C: m=2                             -> o[x][y] += 1, o[y][x] += 1
      total = 7 = 3 + 2 + 2, marginals n_x = 4, n_y = 3.
      D_o = 2/7 = 0.285714
      D_e = (4*3 + 3*4) / (7*6) = 24/42 = 0.571429
      alpha = 1 - 0.5 = 0.500000

    Weighting every ordered pair at 1 instead gives o[x][x] = 6, total 10, and alpha = 0.5714 --
    the run of three agreements would count twice as much as it should. Which is the whole
    reason to check: both values look entirely reasonable in a report.
    """
    assert a.krippendorff_alpha([("x", "x", "x"), ("y", "y"), ("x", "y")]) == pytest.approx(0.5)

    # Perfect agreement stays 1.0 regardless of how many raters saw each unit.
    assert a.krippendorff_alpha([("x",) * 5, ("y",) * 2]) == pytest.approx(1.0)


def test_alpha_is_zero_when_disagreement_is_exactly_chance():
    """Units (x,x,x) and (y,x): D_o = 2/5 and D_e = 8/20 are both 0.4, so alpha is 0.

    Not an edge case to be smoothed -- a judge that scores 0 here has contributed nothing over
    guessing from the observed label frequencies, and it should read as exactly that.
    """
    assert a.krippendorff_alpha([("x", "x", "x"), ("y", "x")]) == pytest.approx(0.0)


# --- the screening framing -----------------------------------------------------------------


def test_screening_reports_sensitivity_specificity_and_the_review_load():
    """A judge that flags 20 of 26 real grader errors and 15 clean turns, out of 216.

    sensitivity = 20/26 = 0.769; specificity = 175/190 = 0.921;
    precision = 20/35 = 0.571; review load = 35/216 = 0.162.

    Precision is the number that decides whether anyone uses this: at 12% prevalence, a judge
    with 92% specificity still sends more clean turns than dirty ones on some settings, and a
    reviewer experiences that as noise regardless of how good the sensitivity is.
    """
    s = a.Screening(true_positive=20, false_positive=15, false_negative=6, true_negative=175)
    assert s.n == 216
    assert s.positives == 26
    assert s.prevalence == pytest.approx(26 / 216)
    assert s.sensitivity.point == pytest.approx(20 / 26)
    assert s.specificity.point == pytest.approx(175 / 190)
    assert s.precision.point == pytest.approx(20 / 35)
    assert s.review_load == pytest.approx(35 / 216)
    # Wilson, so the interval on 26 observations is wide and does not run outside [0, 1].
    assert 0.0 < s.sensitivity.low < s.sensitivity.point < s.sensitivity.high < 1.0


def test_screening_precision_is_none_when_nothing_was_flagged():
    """A judge that agrees with the grader everywhere. Not an error, and not a precision of 0."""
    s = a.Screening(true_positive=0, false_positive=0, false_negative=26, true_negative=190)
    assert s.precision is None
    assert s.sensitivity.point == 0.0
    assert s.specificity.point == 1.0


def test_screening_builds_from_aligned_boolean_sequences():
    s = a.screening([True, True, False, False], [True, False, True, False])
    assert (s.true_positive, s.false_negative, s.false_positive, s.true_negative) == (1, 1, 1, 1)
    with pytest.raises(ValueError, match="different lengths"):
        a.screening([True], [True, False])


# --- the bootstrap -------------------------------------------------------------------------


def test_bootstrap_brackets_the_point_estimate_and_is_reproducible():
    pairs = counts_to_pairs(
        {("y", "y"): 80, ("y", "n"): 5, ("n", "y"): 10, ("n", "n"): 5}
    )

    def kappa(sample):
        return a.matrix(sample, categories=("y", "n")).kappa

    low, high = a.bootstrap(pairs, kappa, resamples=1000)
    point = kappa(pairs)
    assert low < point < high
    assert a.bootstrap(pairs, kappa, resamples=1000) == (low, high)


def test_bootstrap_refuses_a_table_too_sparse_to_resample():
    """20 identical pairs: nearly every resample is single-category and undefined.

    Returning a degenerate interval here would put a spurious [1.0, 1.0] into the report, which
    reads as certainty rather than as no information at all.
    """
    pairs = [("correct", "correct")] * 20

    def kappa(sample):
        m = a.matrix(sample, categories=("correct", "wrong"))
        if m.p_expected == 1.0:
            raise ValueError("degenerate")
        return m.kappa

    with pytest.raises(ValueError, match="too sparse"):
        a.bootstrap(pairs, kappa, resamples=200)


# --- the tabulator -------------------------------------------------------------------------


def test_declared_categories_keep_an_unused_grade_visible():
    """A four-way scheme the judge only ever uses three ways is a finding.

    Inferring categories from the data would silently make it a three-way scheme, and the
    confusion matrix in the report would lose the row that shows the judge never once said
    `confused`.
    """
    m = a.matrix([("correct", "correct")] * 5, categories=GRADES)
    assert m.categories == GRADES
    assert m.row_total("confused") == 0
    assert "confused" in m.table()


def test_a_label_outside_the_declared_categories_is_an_error():
    """A judge returning an off-schema verdict must not be quietly tabulated as a new grade."""
    with pytest.raises(ValueError, match="outside the declared categories"):
        a.matrix([("correct", "CORRECT")], categories=GRADES)


def test_the_table_names_which_axis_is_the_reference():
    """Sensitivity reads one direction. A transposed table returns wrong answers that look
    right, so the rendered matrix says out loud which rater is which."""
    m = a.matrix(
        [("correct", "correct"), ("wrong", "correct")],
        categories=GRADES,
        reference_label="human audit",
        rater_label="sonnet-5 judge",
    )
    out = m.table()
    assert "human audit" in out
    assert "sonnet-5 judge" in out
