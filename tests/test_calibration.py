import pytest

from validity.calibration import (
    agreement_report,
    bias_probe,
    calibration_decision,
    human_human_ceiling,
    judge_repeatability,
)


def test_human_human_ceiling_is_explicitly_available():
    report = human_human_ceiling(
        ["pass", "pass", "fail", "pass"],
        ["pass", "pass", "fail", "fail"],
    )

    assert report is not None
    assert report.raw_agreement == pytest.approx(0.75)
    assert report.n == 4


def test_missing_human_pair_does_not_become_a_fake_ceiling():
    assert human_human_ceiling([], []) is None


def test_repeatability_reports_the_observed_range():
    report = judge_repeatability(
        [
            ["pass", "pass", "fail"],
            ["pass", "fail", "fail"],
            ["pass", "pass", "fail"],
        ]
    )

    assert report is not None
    assert report.minimum == pytest.approx(2 / 3)
    assert report.maximum == pytest.approx(1.0)


def test_bias_probe_keeps_position_and_verbosity_as_paired_questions():
    report = bias_probe(
        [0.8, 0.7, 0.9],
        [0.7, 0.7, 0.8],
        [0.8, 0.7, 0.9],
        [0.7, 0.6, 0.8],
    )

    assert report.position_difference == pytest.approx(-0.2 / 3)
    assert report.verbosity_difference == pytest.approx(-0.1)


def test_calibration_decision_separates_screening_from_release():
    human_ceiling = agreement_report(
        ["pass", "pass", "fail", "fail"],
        ["pass", "pass", "fail", "pass"],
    )
    judge_human = agreement_report(
        ["pass", "pass", "fail", "fail"],
        ["pass", "pass", "fail", "fail"],
    )
    repeatability = judge_repeatability(
        [["pass", "pass", "fail"], ["pass", "fail", "fail"]]
    )

    decision = calibration_decision(
        human_ceiling=human_ceiling,
        judge_human=judge_human,
        repeatability=repeatability,
        abstention_rate=0.10,
    )

    assert decision.decision == "screening_only"
    assert "judge repeatability is below the declared threshold" in decision.reasons
