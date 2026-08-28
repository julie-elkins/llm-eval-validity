"""Tests for the item analysis.

The correlation and alpha implementations are checked against constructed cases whose answers
are known by hand or from the literature, not against this module's own output. The analysis on
top of them is checked for the one thing that would invalidate the write-up: that the full-grid
table really is confounded by the corpus axis and the stratified one really is not.
"""

import pytest

from validity import discrimination as d
from validity import fixture


@pytest.fixture(scope="module")
def f():
    return fixture.load()


@pytest.fixture(scope="module")
def full(f):
    return d.analyse(f, label="all")


@pytest.fixture(scope="module")
def stratum(f):
    return d.analyse(f, cells=[c for c in f.cells() if "/v2/" in c], label="v2")


# --- the estimators -------------------------------------------------------------------------


def test_pearson_is_one_for_a_perfect_linear_relation():
    assert d.pearson([0, 1, 2, 3], [0, 2, 4, 6]) == pytest.approx(1.0)
    assert d.pearson([0, 1, 2, 3], [6, 4, 2, 0]) == pytest.approx(-1.0)


def test_pearson_matches_a_hand_computed_dichotomous_case():
    """Point-biserial by hand: x = [0,0,1,1], y = [1,2,3,4].

    Deviations: dx = [-.5,-.5,.5,.5], dy = [-1.5,-.5,.5,1.5].
    Numerator .75+.25+.25+.75 = 2.0; sx = 1.0, sy = sqrt(5) = 2.2360679...
    r = 2 / 2.2360679 = 0.8944271...
    """
    assert d.pearson([0, 0, 1, 1], [1, 2, 3, 4]) == pytest.approx(0.8944271909999159)


def test_pearson_returns_zero_rather_than_nan_for_a_constant_series():
    """A saturated item has no variance. NaN would propagate into every sort downstream."""
    assert d.pearson([1, 1, 1, 1], [1, 2, 3, 4]) == 0.0
    assert d.pearson([1, 2, 3, 4], [0, 0, 0, 0]) == 0.0


def test_pearson_refuses_a_sample_too_small_to_mean_anything():
    with pytest.raises(ValueError, match="not meaningful"):
        d.pearson([0, 1], [1, 0])
    with pytest.raises(ValueError, match="different lengths"):
        d.pearson([0, 1, 2], [1, 0])


def test_alpha_is_one_for_identical_items_and_zero_for_uncorrelated_ones():
    """The two anchors that fix the scale.

    Four identical columns are perfectly redundant, which is alpha = 1 -- and is the reading
    the report leans on when it calls a high alpha a redundancy warning rather than good news.
    """
    col = [0, 0, 1, 1, 1, 0, 1, 0]
    assert d.cronbach_alpha([col] * 4) == pytest.approx(1.0)
    # Orthogonal columns: total variance equals the sum of item variances, so alpha is 0.
    assert d.cronbach_alpha([[1, 1, 0, 0], [1, 0, 1, 0]]) == pytest.approx(0.0)


def test_alpha_needs_at_least_two_items():
    with pytest.raises(ValueError, match="at least two"):
        d.cronbach_alpha([[0, 1, 0, 1]])


# --- the analysis ---------------------------------------------------------------------------


def test_the_score_matrix_is_complete(f):
    """24 cells x 8 cases with no gaps. A missing entry would raise a KeyError in `analyse`,
    but silently only for the one item it belonged to, so it is asserted directly."""
    cells, matrix = d.score_matrix(f)
    assert len(cells) == 24
    assert all(len(matrix[c]) == 8 for c in cells)
    assert {v for c in cells for v in matrix[c].values()} == {0, 1}


def test_the_full_grid_analysis_is_confounded_by_the_corpus_axis(full):
    """The finding the report is built on, asserted so it cannot silently stop being true.

    Every cell in the lower group scored zero, and every zero-scoring cell is corpus=v1. That
    is what makes `D` over the full grid a difficulty statistic rather than a discrimination
    one, and it is why the report leads with the confound instead of the table.
    """
    assert len(full.dead_cells) == 9
    assert all("/v1/" in c for c in full.dead_cells)
    assert all(full.totals[c] == 0 for c in full.lower_group)
    assert all(i.lower == 0.0 for i in full.items)


def test_the_full_grid_looks_uniformly_excellent_which_is_the_artefact(full):
    """Every item strong and alpha near-perfect: the pattern a naive run would report as
    success. Pinned because the report's rhetorical structure depends on it."""
    assert all(i.r_corrected > 0.4 for i in full.items)
    assert full.alpha > 0.9
    assert full.mean_interitem_r > 0.5


def test_stratifying_dissolves_the_apparent_redundancy(full, stratum):
    """Mean inter-item correlation and alpha both fall substantially inside the stratum.

    This is the evidence that the first table's redundancy was the corpus axis and not a
    property of the eight questions -- the single claim that most of the write-up rests on.
    """
    assert len(stratum.cells) == 12
    assert stratum.mean_interitem_r < full.mean_interitem_r / 2
    assert stratum.alpha < full.alpha
    assert not stratum.dead_cells


def test_two_items_are_at_ceiling_inside_the_stratum(stratum):
    """`returns_window` and `return_shipping` are 12/12, so they cannot rank v2 configurations.

    The concrete, actionable output of the whole module. Asserted by name because the
    recommendation in the report names them.
    """
    saturated = {i.case for i in stratum.items if i.saturated}
    assert saturated == {"returns_window", "return_shipping"}
    for i in stratum.items:
        if i.saturated:
            assert i.difficulty == 1.0
            assert i.r_corrected == 0.0


def test_a_saturated_item_is_not_labelled_weak(stratum):
    """Its r is zero for an arithmetic reason, and "revise or drop" is the wrong instruction."""
    for i in stratum.items:
        if i.saturated:
            assert i.band == ("at ceiling", "regression check only")
        else:
            assert i.band[0] != "at ceiling"


def test_corrected_correlation_is_never_above_uncorrected(full, stratum):
    """Including an item in its own criterion can only inflate the coefficient.

    A violation would mean the rest-score is being built wrong, which would not otherwise be
    visible -- both columns would still look like plausible correlations.
    """
    for a in (full, stratum):
        for i in a.items:
            assert i.r_corrected <= i.r_uncorrected + 1e-12, (a.label, i.case)


def test_analysis_refuses_a_stratum_too_thin_to_support_it(f):
    """Guards against the obvious next step -- stratifying by corpus *and* retriever, which
    would leave six cells and produce a table of noise with two decimal places."""
    with pytest.raises(ValueError, match="too few"):
        d.analyse(f, cells=[c for c in f.cells() if "/v2/" in c and "/kb" in c])


def test_report_runs_over_the_real_fixture(f, capsys):
    d.report(f)
    out = capsys.readouterr().out
    assert "at ceiling" in out
    assert "corpus=v2" in out
    assert "{" not in out
