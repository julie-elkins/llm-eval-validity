"""Analysis helpers for a human-grounded judge calibration study.

This module turns the study questions into explicit outputs without inventing human labels.
Callers must provide aligned synthetic or approved labels. A missing second human is reported
as an open ceiling, not converted into a judge-quality claim.
"""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Sequence

from validity.agreement import Matrix, matrix
from validity.interview_stats import paired_bootstrap_mean_difference


@dataclass(frozen=True)
class AgreementReport:
    raw_agreement: float
    kappa: float
    n: int


@dataclass(frozen=True)
class RepeatabilityReport:
    pairwise_agreements: tuple[float, ...]
    minimum: float
    maximum: float


@dataclass(frozen=True)
class BiasProbe:
    position_difference: float
    verbosity_difference: float
    position_interval: tuple[float, float]
    verbosity_interval: tuple[float, float]


@dataclass(frozen=True)
class CalibrationDecision:
    decision: str
    reasons: tuple[str, ...]


def agreement_report(reference: Sequence[str], rater: Sequence[str]) -> AgreementReport:
    """Compare one rater with a reference using the repository's agreement definitions."""

    if len(reference) != len(rater):
        raise ValueError("reference and rater must have the same length")
    table = matrix(list(zip(reference, rater)))
    return AgreementReport(table.p_observed, table.kappa, table.n)


def human_human_ceiling(
    human_a: Sequence[str],
    human_b: Sequence[str],
) -> AgreementReport | None:
    """Return the human-human ceiling, or None when the independent pair is absent."""

    if len(human_a) != len(human_b):
        raise ValueError("human raters must have the same length")
    if not human_a:
        return None
    return agreement_report(human_a, human_b)


def judge_repeatability(runs: Sequence[Sequence[str]]) -> RepeatabilityReport | None:
    """Summarize agreement across repeated judge runs on the same cases."""

    if len(runs) < 2:
        return None
    if len({len(run) for run in runs}) != 1:
        raise ValueError("judge runs must have the same number of cases")
    agreements = []
    for index, first in enumerate(runs):
        for second in runs[index + 1 :]:
            agreements.append(agreement_report(first, second).raw_agreement)
    return RepeatabilityReport(tuple(agreements), min(agreements), max(agreements))


def bias_probe(
    position_first_scores: Sequence[float],
    position_second_scores: Sequence[float],
    concise_scores: Sequence[float],
    verbose_scores: Sequence[float],
) -> BiasProbe:
    """Measure paired position and verbosity differences with bootstrap intervals."""

    position = paired_bootstrap_mean_difference(
        position_first_scores,
        position_second_scores,
        resamples=1000,
        seed=20261118,
    )
    verbosity = paired_bootstrap_mean_difference(
        concise_scores,
        verbose_scores,
        resamples=1000,
        seed=20261119,
    )
    return BiasProbe(
        position_difference=position.point,
        verbosity_difference=verbosity.point,
        position_interval=(position.low, position.high),
        verbosity_interval=(verbosity.low, verbosity.high),
    )


def calibration_decision(
    *,
    human_ceiling: AgreementReport | None,
    judge_human: AgreementReport | None,
    repeatability: RepeatabilityReport | None,
    abstention_rate: float,
    minimum_agreement: float = 0.80,
    maximum_abstention_rate: float = 0.20,
) -> CalibrationDecision:
    """Decide whether a judge is suitable for screening or release.

    Screening means routing cases to human review; release means using the judge as a release
    gate. The release decision is intentionally stricter and requires human-human evidence.
    """

    reasons: list[str] = []
    if human_ceiling is None:
        reasons.append("human-human agreement ceiling is not measured")
    if judge_human is None:
        reasons.append("judge-human agreement is not measured")
    elif judge_human.raw_agreement < minimum_agreement:
        reasons.append("judge-human agreement is below the declared threshold")
    if repeatability is None:
        reasons.append("judge repeatability is not measured")
    elif repeatability.minimum < minimum_agreement:
        reasons.append("judge repeatability is below the declared threshold")
    if not 0 <= abstention_rate <= 1:
        raise ValueError("abstention_rate must be between 0 and 1")
    if abstention_rate > maximum_abstention_rate:
        reasons.append("judge abstention exceeds the declared threshold")

    if not reasons:
        return CalibrationDecision("screening_and_release_candidate", ())
    if judge_human is not None and judge_human.raw_agreement >= minimum_agreement:
        return CalibrationDecision("screening_only", tuple(reasons))
    return CalibrationDecision("not_ready", tuple(reasons))
