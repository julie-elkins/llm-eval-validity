"""Run the offline Eval Statistics Interview Lab."""

from __future__ import annotations

import json

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


def main() -> None:
    paired = paired_bootstrap_mean_difference(
        [0, 1, 0, 1, 1, 0],
        [1, 1, 0, 1, 1, 1],
        resamples=1000,
    )
    mcnemar = mcnemar_exact(
        [False, True, False, True, True, False],
        [True, True, False, False, True, True],
    )
    cluster = cluster_bootstrap_mean(
        {"task-family-a": [1, 1, 0], "task-family-b": [1, 0], "task-family-c": [0, 0, 0]},
        resamples=1000,
    )
    correction = bonferroni_correction([0.01, 0.04, 0.20])
    labels = [True, False, False, False, True, False]
    scores = [0.95, 0.80, 0.65, 0.55, 0.50, 0.10]

    report = {
        "paired_bootstrap_difference": paired.__dict__,
        "mcnemar": mcnemar.__dict__,
        "cluster_bootstrap_mean": cluster.__dict__,
        "bonferroni": correction.__dict__,
        "roc_auc": roc_auc(labels, scores),
        "pr_auc_trapezoid": pr_auc_trapezoid(labels, scores),
        "pass_at_3": pass_at_k(10, 2, 3),
        "pass_power_3": pass_power_k(0.2, 3),
        "cost_per_solved_task_usd": cost_per_solved_task(18.0, 3),
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
