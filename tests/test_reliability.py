"""Tests for the judge-validation report.

Two kinds of test here. The first kind checks the aggregation logic on synthetic transcripts,
because a majority-vote bug or a mis-joined turn index would move every number in the report in
a plausible-looking direction. The second kind pins the findings the write-up makes claims
about, against the real 2,494 verdicts -- so if a re-run of the judge changes a conclusion, a
test fails rather than a paragraph quietly becoming false.
"""

import json

import pytest

from validity import agreement, fixture
from validity import reliability as rel


@pytest.fixture(scope="module")
def f():
    return fixture.load()


@pytest.fixture(scope="module")
def rows():
    got = rel.read()
    if not got:
        pytest.skip("no judge transcripts recorded; run `make judge`")
    return got


def transcript(tmp_path, records):
    """Write a synthetic transcript and read it back through the real loader."""
    path = tmp_path / "sonnet-5.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in records))
    return rel.read(tmp_path)


def verdict(turn, grade, run=1, order="current-first", error=None):
    return {
        "judge": "sonnet-5", "family": fixture.POLICY, "turn": turn, "grade": grade,
        "run": run, "order": order, "error": error,
    }


# --- aggregation ----------------------------------------------------------------------------


def test_consensus_takes_the_majority_of_the_passes(tmp_path):
    """Turn 0 is called `correct` twice and `abstained` once, so consensus is `correct`."""
    got = transcript(tmp_path, [
        verdict(0, "correct", run=1), verdict(0, "abstained", run=2), verdict(0, "correct", run=3),
    ])
    r = rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY)
    assert r.labels == {0: "correct"}
    assert len(r.passes) == 3
    assert r.unstable == (0,)


def test_consensus_ignores_the_swapped_order_arm_unless_asked_for_it(tmp_path):
    """The order arm shares turn indices with the main arm. Pooling them would silently average
    the sensitivity test into the headline figure and hide the effect it exists to measure."""
    got = transcript(tmp_path, [
        verdict(0, "correct", order="current-first"),
        verdict(0, "abstained", order="superseded-first"),
    ])
    main = rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY)
    swapped = rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY, order="superseded-first")
    assert main.labels == {0: "correct"}
    assert swapped.labels == {0: "abstained"}
    assert len(main.passes) == 1


def test_errored_verdicts_are_dropped_rather_than_tabulated(tmp_path):
    """An errored verdict has no grade. Counting it would put a None into a confusion matrix."""
    got = transcript(tmp_path, [
        verdict(0, "correct"), verdict(1, None, error="ThrottlingException"),
    ])
    assert len(got["sonnet-5"]) == 1
    assert rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY).labels == {0: "correct"}


def test_consensus_only_keeps_turns_every_pass_answered(tmp_path):
    """A turn that failed on pass 2 must not get a majority computed from the other two.

    Otherwise the per-pass columns and the consensus column describe different turn sets, and a
    judge whose failures cluster on hard turns would look better in consensus than in any run.
    """
    got = transcript(tmp_path, [
        verdict(0, "correct", run=1), verdict(0, "correct", run=2),
        verdict(1, "wrong", run=1),
    ])
    r = rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY)
    assert set(r.labels) == {0}


def test_the_passes_are_scored_as_intra_rater_agreement(tmp_path):
    """Three identical passes is alpha 1.0; a flip on one of two turns is below it."""
    same = transcript(tmp_path, [verdict(t, "correct", run=r)
                                 for t in (0, 1) for r in (1, 2, 3)])
    assert rel.consensus(same["sonnet-5"], "sonnet-5", fixture.POLICY).alpha == pytest.approx(1.0)

    flips = transcript(tmp_path, [
        verdict(0, "correct", run=1), verdict(0, "abstained", run=2),
        verdict(1, "abstained", run=1), verdict(1, "abstained", run=2),
    ])
    assert rel.consensus(flips["sonnet-5"], "sonnet-5", fixture.POLICY).alpha < 1.0


def test_a_reading_without_passes_reports_no_alpha(f):
    """The human reference was read once. An alpha for it would be a fabrication."""
    assert rel.reference(f, fixture.POLICY).alpha is None
    assert rel.reference(f, fixture.POLICY).unstable == ()


def test_the_reference_reading_excludes_the_turns_with_no_human_label(f):
    """Five behaviour turns never reached the tool, so the audit recorded nothing for them."""
    assert len(rel.reference(f, fixture.BEHAVIOUR).labels) == 19
    assert len(rel.reference(f, fixture.POLICY).labels) == 192


def test_a_comparison_is_only_over_turns_both_raters_labelled(tmp_path, f):
    got = transcript(tmp_path, [verdict(0, "correct"), verdict(1, "abstained")])
    r = rel.consensus(got["sonnet-5"], "sonnet-5", fixture.POLICY)
    c = rel.compare(rel.reference(f, fixture.POLICY), r, bootstrap=False)
    assert c.n == 2


def test_the_degenerate_flag_fires_exactly_when_the_ceiling_is_zero():
    """The property the report's central caveat is keyed on.

    A rater that used one category cannot score a positive kappa, so the report must be able to
    detect that case rather than printing a 0.00 as though it were a measurement.
    """
    one_category = agreement.matrix(
        [("abstained", "abstained")] * 90 + [("correct", "abstained")] * 6,
        rel.GRADES,
    )
    assert one_category.kappa_max == pytest.approx(0.0)
    assert rel.Comparison("j", "l", one_category, one_category, None).degenerate

    varied = agreement.matrix(
        [("abstained", "abstained")] * 80 + [("correct", "correct")] * 16,
        rel.GRADES,
    )
    assert not rel.Comparison("j", "l", varied, varied, None).degenerate


# --- the findings the write-up asserts ------------------------------------------------------


def test_both_judges_agree_with_the_human_more_closely_than_the_incumbent_grader(f, rows):
    """The study's reason for existing. If this reverses, the write-up's thesis is gone."""
    ref = rel.reference(f, fixture.POLICY)
    grader = rel.compare(ref, rel.reference(f, fixture.POLICY, audited=False), bootstrap=False)
    for j in rows:
        judge = rel.compare(ref, rel.consensus(rows[j], j, fixture.POLICY), bootstrap=False)
        assert judge.matrix.kappa > grader.matrix.kappa, j
        assert judge.matrix.p_observed > grader.matrix.p_observed, j


def test_the_two_judges_cannot_be_separated_once_every_pass_is_counted(f, rows):
    """The headline methodological finding, pinned.

    Haiku wins on pass 1 by 0.03 of kappa. Its own pass-to-pass range is wider than that, and
    the two judges' ranges overlap -- so the between-model difference this study can see is
    smaller than the within-model noise, and no ranking is supportable. A single-pass study
    would have reported the ranking without ever being able to see this.
    """
    ranges = {j: rel.spread(rows[j], j, f)[:2] for j in rows}
    assert len(ranges) == 2
    (lo_a, hi_a), (lo_b, hi_b) = ranges.values()
    assert lo_a <= hi_b and lo_b <= hi_a, ranges

    # And the within-judge spread is at least as large as the gap between the point estimates.
    widest = max(hi - lo for lo, hi in ranges.values())
    gap = abs(sum(ranges[j][0] + ranges[j][1] for j in list(ranges)[:1])
              - sum(ranges[j][0] + ranges[j][1] for j in list(ranges)[1:])) / 2
    assert widest >= gap * 0.9, (widest, gap)


def test_the_stale_corpus_stratum_has_a_kappa_ceiling_of_about_zero(f, rows):
    """The result the module's docstring leads with.

    Raw agreement above 0.90 and a kappa at or below 0.00, because the reference standard is
    nearly single-category there. If this ever stops holding, the long explanation of the kappa
    paradox in the report is no longer about this data and has to be rewritten or removed.
    """
    ref = rel.reference(f, fixture.POLICY)
    stale = [i for i, t in enumerate(f.turns)
             if t.family == fixture.POLICY and t.corpus == "v1"]
    for j in rows:
        c = rel.compare(ref, rel.consensus(rows[j], j, fixture.POLICY), turns=stale,
                        bootstrap=False)
        assert c.n == 96
        assert c.matrix.p_observed > 0.90, (j, c.matrix.p_observed)
        assert c.matrix.kappa <= 0.01, (j, c.matrix.kappa)
        assert c.matrix.kappa_max < 0.35, (j, c.matrix.kappa_max)


def test_the_same_judges_score_a_usable_kappa_in_the_stratum_that_varies(f, rows):
    """The other half of the paradox: same judges, same rubric, informative coefficient.

    Without this the low figures above would read as a property of the judges rather than of
    the marginals, which is the misreading the whole section is written to prevent.
    """
    ref = rel.reference(f, fixture.POLICY)
    fresh = [i for i, t in enumerate(f.turns)
             if t.family == fixture.POLICY and t.corpus == "v2"]
    for j in rows:
        c = rel.compare(ref, rel.consensus(rows[j], j, fixture.POLICY), turns=fresh,
                        bootstrap=False)
        assert c.matrix.kappa > 0.80, (j, c.matrix.kappa)
        assert not c.degenerate


def test_the_screen_catches_the_graders_errors_at_a_reviewable_load(f, rows):
    """The deployment claim: high sensitivity for well under a quarter of turns reviewed."""
    ref = rel.reference(f, fixture.POLICY)
    grader = rel.reference(f, fixture.POLICY, audited=False)
    for j in rows:
        s = rel.screen(f, ref, grader, rel.consensus(rows[j], j, fixture.POLICY))
        assert s.sensitivity.point >= 0.95, (j, s.sensitivity.point)
        assert s.review_load < 0.25, (j, s.review_load)
        # The lower bound is the number the report leads with, and it is nowhere near the point
        # estimate -- 23 positives cannot support a confident claim of near-perfect recall.
        assert s.sensitivity.low < 0.90, (j, s.sensitivity.low)


def test_the_grader_fails_on_the_negation_sensitive_questions_and_the_judges_do_not(f, rows):
    """The mechanism behind the headline number, and the part that generalises.

    A regex cannot distinguish "we do not price match" from "we will price match", so the two
    negation-sensitive items are where the incumbent collapses. If a judge were merely better
    everywhere by a constant, the value story would be much weaker and much less transferable.
    """
    ref = rel.reference(f, fixture.POLICY)
    grader = rel.reference(f, fixture.POLICY, audited=False)
    negation = [c for c in {t.case for t in f.policy}
                if f.policy_reference[c].negation_sensitive]
    assert set(negation) == set(fixture.NEGATION_SENSITIVE)

    def hit_rate(reading, case):
        turns = [i for i, t in enumerate(f.turns) if t.case == case]
        return sum(1 for i in turns if reading.labels.get(i) == ref.labels[i]) / len(turns)

    others = [c for c in {t.case for t in f.policy} if c not in negation]
    for case in negation:
        assert hit_rate(grader, case) < 0.60, case
        assert hit_rate(grader, case) < min(hit_rate(grader, o) for o in others)
        for j in rows:
            judged = rel.consensus(rows[j], j, fixture.POLICY)
            assert hit_rate(judged, case) > 0.90, (j, case)


def test_the_human_reference_never_uses_the_harmful_grades(f):
    """Which is why the harmful/safe collapse produces a kappa of zero, and why the report says
    so instead of quoting the binary coefficient as an improvement."""
    ref = rel.reference(f, fixture.POLICY)
    used = set(ref.labels.values())
    assert used == {fixture.CORRECT, fixture.ABSTAINED}
    assert not used & set(fixture.HARMFUL)

    collapsed = rel.compare(
        ref, rel.reference(f, fixture.POLICY, audited=False), bootstrap=False
    ).collapsed
    assert collapsed.row_total("harmful") == 0
    assert collapsed.kappa_max == pytest.approx(0.0)


def test_order_sensitivity_is_smaller_than_run_to_run_instability(f, rows):
    """Both are measured so they can be compared; the comparison is the point.

    If swapping the two policy statements moved more labels than re-running the same prompt did,
    the judges would be reading the prompt's layout rather than the reply, and every agreement
    figure above would be suspect.
    """
    for j in rows:
        flips, n = rel.order_flips(rows[j], j, fixture.POLICY)
        unstable = len(rel.consensus(rows[j], j, fixture.POLICY).unstable)
        assert flips / n < 0.05, (j, flips, n)
        assert flips <= unstable + 2, (j, flips, unstable)


def test_the_report_runs_over_the_real_transcripts_and_names_its_limits(f, rows, capsys):
    """A smoke test with teeth: the caveats are part of the deliverable, not decoration."""
    rel.report(f, rows)
    out = capsys.readouterr().out
    for judge in rows:
        assert judge in out
    for required in (
        "kappa_max",          # never quote kappa without its ceiling
        "one human reader",   # no human-human ceiling was estimated
        "not fully blind",    # the filename cue
        "Nothing here is a pass rate",  # the exec summary's framing
    ):
        assert required in out, required


def test_the_report_says_so_rather_than_failing_when_nothing_has_been_judged(f, capsys):
    rel.report(f, {})
    assert "No verdicts recorded" in capsys.readouterr().out
