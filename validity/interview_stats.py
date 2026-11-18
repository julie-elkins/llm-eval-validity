"""Small, dependency-free statistics used in the evaluation interview lab.

The functions here are intentionally narrow. They expose assumptions that are easy to hide
behind a statistics package: paired cases, clustered observations, multiple hypotheses, rare
positives, repeated attempts, and cost accounting.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from statistics import mean
from typing import Callable, Iterable, Mapping, Sequence


DEFAULT_RESAMPLES = 5000
DEFAULT_SEED = 20261118


@dataclass(frozen=True)
class BootstrapInterval:
    point: float
    low: float
    high: float
    confidence: float
    resamples: int


@dataclass(frozen=True)
class McNemarResult:
    candidate_only: int
    baseline_only: int
    statistic: float
    p_value: float


@dataclass(frozen=True)
class MultipleComparisonResult:
    raw_p_values: tuple[float, ...]
    adjusted_p_values: tuple[float, ...]
    rejected: tuple[bool, ...]
    alpha: float


def _validate_confidence(confidence: float) -> None:
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")


def _percentile(values: Sequence[float], probability: float) -> float:
    if not values:
        raise ValueError("cannot calculate a percentile from no values")
    index = min(len(values) - 1, max(0, int(probability * len(values))))
    return values[index]


def _bootstrap(
    observations: Sequence[object],
    statistic: Callable[[list[object]], float],
    *,
    confidence: float,
    resamples: int,
    seed: int,
) -> BootstrapInterval:
    if len(observations) < 2:
        raise ValueError("at least two observations are required")
    if resamples < 100:
        raise ValueError("resamples must be at least 100")
    _validate_confidence(confidence)

    point = statistic(list(observations))
    rng = random.Random(seed)
    values: list[float] = []
    for _ in range(resamples):
        sample = [observations[rng.randrange(len(observations))] for _ in observations]
        values.append(statistic(sample))
    values.sort()
    tail = (1 - confidence) / 2
    return BootstrapInterval(
        point=point,
        low=_percentile(values, tail),
        high=_percentile(values, 1 - tail),
        confidence=confidence,
        resamples=resamples,
    )


def paired_bootstrap_mean_difference(
    baseline: Sequence[float],
    candidate: Sequence[float],
    *,
    confidence: float = 0.95,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
) -> BootstrapInterval:
    """Bootstrap the candidate-minus-baseline mean on matched evaluation cases."""

    if len(baseline) != len(candidate):
        raise ValueError("baseline and candidate must have the same length")
    if not baseline:
        raise ValueError("no paired observations")
    pairs = list(zip(baseline, candidate))

    def difference(sample: list[tuple[float, float]]) -> float:
        return mean(candidate_score - baseline_score for baseline_score, candidate_score in sample)

    return _bootstrap(
        pairs,
        difference,
        confidence=confidence,
        resamples=resamples,
        seed=seed,
    )


def mcnemar_exact(
    baseline_pass: Sequence[bool],
    candidate_pass: Sequence[bool],
) -> McNemarResult:
    """Run the exact two-sided McNemar test on paired binary outcomes.

    McNemar's test is a paired test for binary outcomes. Only cases where exactly one system
    passes contribute to the test; concordant cases carry no information about the difference.
    """

    if len(baseline_pass) != len(candidate_pass):
        raise ValueError("baseline and candidate must have the same length")
    if not baseline_pass:
        raise ValueError("no paired observations")

    candidate_only = sum(
        not baseline and candidate
        for baseline, candidate in zip(baseline_pass, candidate_pass)
    )
    baseline_only = sum(
        baseline and not candidate
        for baseline, candidate in zip(baseline_pass, candidate_pass)
    )
    discordant = candidate_only + baseline_only
    if discordant == 0:
        return McNemarResult(candidate_only, baseline_only, 0.0, 1.0)

    smaller = min(candidate_only, baseline_only)
    lower_tail = sum(
        math.comb(discordant, successes) for successes in range(smaller + 1)
    ) / (2**discordant)
    p_value = min(1.0, 2 * lower_tail)
    statistic = (candidate_only - baseline_only) ** 2 / discordant
    return McNemarResult(candidate_only, baseline_only, statistic, p_value)


def cluster_bootstrap_mean(
    clusters: Mapping[str, Sequence[float]],
    *,
    confidence: float = 0.95,
    resamples: int = DEFAULT_RESAMPLES,
    seed: int = DEFAULT_SEED,
) -> BootstrapInterval:
    """Bootstrap a pooled mean while resampling independent clusters.

    A cluster can be a user, task family, conversation, or repository. Resampling individual
    turns would pretend correlated turns were independent and make the interval too narrow.
    """

    if len(clusters) < 2:
        raise ValueError("at least two clusters are required")
    if any(not values for values in clusters.values()):
        raise ValueError("clusters cannot be empty")
    names = tuple(clusters)

    def pooled_mean(selected: list[str]) -> float:
        values = [value for name in selected for value in clusters[name]]
        return mean(values)

    return _bootstrap(
        names,
        pooled_mean,
        confidence=confidence,
        resamples=resamples,
        seed=seed,
    )


def bonferroni_correction(
    p_values: Iterable[float],
    *,
    alpha: float = 0.05,
) -> MultipleComparisonResult:
    """Apply Bonferroni correction to a family of hypotheses."""

    values = tuple(p_values)
    if not values:
        raise ValueError("no p-values")
    if not 0 < alpha < 1:
        raise ValueError("alpha must be between 0 and 1")
    if any(not 0 <= value <= 1 for value in values):
        raise ValueError("p-values must be between 0 and 1")
    adjusted = tuple(min(1.0, value * len(values)) for value in values)
    threshold = alpha / len(values)
    return MultipleComparisonResult(
        raw_p_values=values,
        adjusted_p_values=adjusted,
        rejected=tuple(value <= threshold for value in values),
        alpha=alpha,
    )


def roc_auc(labels: Sequence[bool], scores: Sequence[float]) -> float:
    """Calculate ROC-AUC, the probability a positive ranks above a negative."""

    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    positives = [score for label, score in zip(labels, scores) if label]
    negatives = [score for label, score in zip(labels, scores) if not label]
    if not positives or not negatives:
        raise ValueError("ROC-AUC needs both positive and negative labels")
    wins = sum(1 for positive in positives for negative in negatives if positive > negative)
    ties = sum(1 for positive in positives for negative in negatives if positive == negative)
    return (wins + 0.5 * ties) / (len(positives) * len(negatives))


def pr_auc_trapezoid(labels: Sequence[bool], scores: Sequence[float]) -> float:
    """Calculate trapezoidal precision-recall area for a ranked list."""

    if len(labels) != len(scores):
        raise ValueError("labels and scores must have the same length")
    if not labels:
        raise ValueError("no observations")
    positives = sum(labels)
    if positives == 0:
        raise ValueError("PR-AUC needs at least one positive label")

    ranked = sorted(zip(scores, labels), key=lambda pair: pair[0], reverse=True)
    points = [(0.0, 1.0)]
    true_positives = 0
    false_positives = 0
    for _, label in ranked:
        if label:
            true_positives += 1
        else:
            false_positives += 1
        recall = true_positives / positives
        precision = true_positives / (true_positives + false_positives)
        points.append((recall, precision))

    return sum(
        (recall_b - recall_a) * (precision_a + precision_b) / 2
        for (recall_a, precision_a), (recall_b, precision_b) in zip(points, points[1:])
    )


def pass_at_k(n: int, solved: int, k: int) -> float:
    """Estimate the chance that at least one of k samples solves a task."""

    if not 0 <= solved <= n or n <= 0 or not 0 < k <= n:
        raise ValueError("require n > 0, 0 <= solved <= n, and 0 < k <= n")
    if n - solved < k:
        return 1.0
    return 1 - math.comb(n - solved, k) / math.comb(n, k)


def pass_power_k(pass_probability: float, k: int) -> float:
    """Calculate the chance that all k independent attempts pass."""

    if not 0 <= pass_probability <= 1 or k <= 0:
        raise ValueError("require 0 <= pass_probability <= 1 and k > 0")
    return pass_probability**k


def cost_per_solved_task(total_cost_usd: float, solved_tasks: int) -> float:
    """Calculate spend per solved task, refusing a zero-success denominator."""

    if total_cost_usd < 0:
        raise ValueError("cost cannot be negative")
    if solved_tasks <= 0:
        raise ValueError("cost per solved task is undefined when no task was solved")
    return total_cost_usd / solved_tasks
