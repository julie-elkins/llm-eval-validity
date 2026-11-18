import pytest

from validity.interview_stats import (
    bonferroni_correction,
    cluster_bootstrap_mean,
    cost_per_solved_task,
    mcnemar_exact,
    paired_bootstrap_mean_difference,
    pass_at_k,
    pass_power_k,
    pr_auc_trapezoid,
    roc_auc,
)


def test_paired_bootstrap_is_reproducible_and_keeps_case_pairing():
    result = paired_bootstrap_mean_difference(
        [0, 1, 0, 1],
        [1, 1, 0, 1],
        resamples=500,
        seed=7,
    )

    assert result.point == pytest.approx(0.25)
    assert result.low <= result.point <= result.high
    assert result == paired_bootstrap_mean_difference(
        [0, 1, 0, 1],
        [1, 1, 0, 1],
        resamples=500,
        seed=7,
    )


def test_mcnemar_uses_only_discordant_pairs():
    result = mcnemar_exact(
        [True, True, False, False, False, True],
        [True, False, True, False, False, True],
    )

    assert result.candidate_only == 1
    assert result.baseline_only == 1
    assert result.p_value == pytest.approx(1.0)


def test_cluster_bootstrap_resamples_clusters_not_individual_rows():
    result = cluster_bootstrap_mean(
        {"user-a": [1, 1, 1], "user-b": [0, 0, 0], "user-c": [0, 0, 1]},
        resamples=500,
        seed=9,
    )

    assert result.point == pytest.approx(4 / 9)
    assert result.low <= result.point <= result.high


def test_bonferroni_changes_the_family_decision():
    result = bonferroni_correction([0.01, 0.02, 0.20])

    assert result.adjusted_p_values == pytest.approx((0.03, 0.06, 0.60))
    assert result.rejected == (True, False, False)


def test_roc_auc_and_pr_auc_answer_different_questions():
    labels = [True, False, True, False]
    scores = [0.9, 0.8, 0.7, 0.1]

    assert roc_auc(labels, scores) == pytest.approx(0.75)
    assert pr_auc_trapezoid(labels, scores) == pytest.approx(19 / 24)


def test_pass_at_k_is_not_pass_power_k():
    assert pass_at_k(10, 2, 3) == pytest.approx(1 - (8 * 7 * 6) / (10 * 9 * 8))
    assert pass_power_k(0.2, 3) == pytest.approx(0.008)
    assert pass_at_k(10, 2, 3) > pass_power_k(0.2, 3)


def test_cost_per_solved_task_refuses_zero_solutions():
    assert cost_per_solved_task(12.0, 3) == pytest.approx(4.0)
    with pytest.raises(ValueError, match="no task was solved"):
        cost_per_solved_task(12.0, 0)
