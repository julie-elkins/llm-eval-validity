"""Tests for the fixture loader.

Most of these assert that the vendored data still reproduces the run it claims to be a copy
of. That is not redundant with `load(verify=True)` -- it is the same check reached from the
other side, so that a bug which weakened the verifier is visible as a failing test rather
than as a study that quietly stopped checking anything.
"""

import json

import pytest

from validity import fixture


@pytest.fixture(scope="module")
def f():
    return fixture.load()


def test_the_fixture_is_the_published_run(f):
    assert len(f.turns) == 216
    assert len(f.policy) == 192
    assert len(f.behaviour) == 24
    assert len(f.cells()) == 24
    assert len(f.corrections) == 26


def test_every_published_accuracy_figure_reproduces(f):
    """The four-axis table in the source README, re-derived from the vendored replies."""
    for (axis, level), expected in fixture.PUBLISHED_ACCURACY.items():
        correct, n = fixture.accuracy(t for t in f.policy if getattr(t, axis) == level)
        assert round(100 * correct / n) == expected, f"{axis}={level}"


def test_the_headline_claim_holds_only_after_the_audit(f):
    """The finding this whole study exists to make a point about.

    "The wrong-answer rate was 0% in all 24 cells" is true of the post-audit labels and false
    of the labels the run actually wrote. Same 192 replies, untouched. If these two ever
    agree, the fixture has lost the second rater and the judge study has nothing to validate
    against.
    """
    pre = [t for t in f.policy if t.is_harmful_preaudit]
    post = [t for t in f.policy if t.is_harmful_postaudit]
    assert len(post) == 0
    assert len(pre) == 12
    assert {t.grade_preaudit for t in pre} == {"wrong", "confused"}


def test_the_two_families_are_scored_on_different_fields(f):
    """Policy turns carry a grade, behaviour turns a violation, and never both.

    Averaging them would produce a number that means nothing, so the loader is asserted to
    keep them separable at the type level rather than by convention at each call site.
    """
    for t in f.policy:
        assert t.grade_postaudit is not None
        assert t.violation_postaudit is None
    for t in f.behaviour:
        assert t.grade_postaudit is None


def test_behaviour_family_keeps_the_three_state_violation(f):
    """None means "never reached the tool, so tested nothing" -- not "passed".

    The distinction decides a denominator, and collapsing it to False is the specific way a
    refusal-discipline number gets silently flattered.
    """
    states = {t.violation_postaudit for t in f.behaviour}
    assert None in states
    unreached = [t for t in f.behaviour if t.violation_postaudit is None]
    assert all(t.reached is False for t in unreached)


def test_every_policy_turn_has_a_reply_to_regrade(f):
    """A judge study over stored text needs the text. An empty reply would score as an
    abstention and look like an ordinary result."""
    assert all(t.reply for t in f.policy)


def test_each_cell_has_the_eight_policy_turns_the_design_calls_for(f):
    """24 cells x 8 graded questions = 192. A short cell would not move any marginal
    detectably but would bias the discrimination analysis, whose unit is the cell."""
    counts = {c: sum(1 for t in f.policy if t.cell == c) for c in f.cells()}
    assert set(counts.values()) == {8}


def test_provenance_names_the_commit_and_the_grader_distinction(f):
    p = f.provenance
    assert p["source_commit"]
    assert p["run_date"] == "2026-08-26"
    assert "grade_postaudit" in p["grader_note"]


def test_every_case_has_an_answer_key_reachable_from_its_turn(f):
    """The judge stage's precondition. `reference(turn)` has to work for all 216 turns.

    Reached through the accessor rather than the two dictionaries, because a case name that
    appears in the turns but not in the key would raise a KeyError deep inside a prompt
    builder mid-run, after money had been spent on the turns before it.
    """
    for t in f.turns:
        r = f.reference(t)
        assert r.case == t.case
        assert r.asked


def test_the_policy_answer_key_gives_both_statements(f):
    """Correct *and* wrong, because the wrong answer is the superseded document rather than an
    invention -- and the grader being compared against was given both."""
    assert len(f.policy_reference) == 8
    for case, r in f.policy_reference.items():
        assert r.correct_statement.strip() and r.wrong_statement.strip()
        assert r.correct_statement != r.wrong_statement
        assert r.current_doc != r.superseded_doc


def test_exactly_the_two_documented_topics_are_negation_sensitive(f):
    """`price_match` and `warranty_proof` are where the regex grader was structurally blind.

    Pinned by name because they are the subgroup the judge is expected to beat rather than
    merely match: the source project reports their wrong-answer rate as a lower bound, and if
    an LLM judge cannot outperform a regex on negation it has no case at all.
    """
    sensitive = {c for c, r in f.policy_reference.items() if r.negation_sensitive}
    assert sensitive == set(fixture.NEGATION_SENSITIVE)
    for case in sensitive:
        # The property that defeats the regexes: the correct answer is itself a negation.
        assert " not " in f.policy_reference[case].correct_statement


def test_the_behaviour_answer_key_describes_an_action_not_a_fact(f):
    """These turns have no correct sentence, only a thing the reply must not have done."""
    assert len(f.behaviour_reference) == 3
    for b in f.behaviour_reference.values():
        assert b.violation.strip() and b.detector.strip() and b.why_restricted.strip()


def test_verification_catches_an_answer_key_with_a_missing_topic(tmp_path):
    """The judge failure that would otherwise be invisible: a prompt slot filled with nothing.

    A judge handed no reference would still return well-formed verdicts, and they would still
    be tabulated -- so this has to fail at load, not at grading.
    """
    raw = json.loads(fixture.FIXTURE.read_text())
    del raw["reference"]["policy"]["price_match"]
    path = tmp_path / "keyless.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="no answer key for policy cases"):
        fixture.load(path)


def test_verification_catches_a_duplicated_statement_pair(tmp_path):
    """Correct == wrong makes an item ungradeable by anything, and is what a copy-paste slip in
    the source answer key looks like."""
    raw = json.loads(fixture.FIXTURE.read_text())
    entry = raw["reference"]["policy"]["returns_window"]
    entry["wrong_statement"] = entry["correct_statement"]
    path = tmp_path / "dupe.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="statements are identical"):
        fixture.load(path)


def test_verification_catches_a_dropped_record(tmp_path):
    """The failure the verifier exists for: a fixture that parses and is wrong."""
    raw = json.loads(fixture.FIXTURE.read_text())
    raw["items"] = raw["items"][:-1]
    path = tmp_path / "short.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="215 turns"):
        fixture.load(path)


def test_verification_catches_labels_that_have_been_flattened(tmp_path):
    """If someone re-extracts with the audit already folded in, the study loses its raters.

    Simulated by overwriting the pre-audit labels with the post-audit ones, which is exactly
    what a naive re-extraction from the current grader would produce.
    """
    raw = json.loads(fixture.FIXTURE.read_text())
    for i in raw["items"]:
        i["grade_preaudit"] = i["grade_postaudit"]
        i["violation_preaudit"] = i["violation_postaudit"]
        i["corrected_by_audit"] = False
    path = tmp_path / "flat.json"
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="nothing for the judge study"):
        fixture.load(path)
