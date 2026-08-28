"""Tests for the judge, all of them offline.

Nothing here calls Bedrock. What is checked is the part that decides whether the judge's
agreement means anything -- what goes into the prompt, what is deliberately left out, and
whether an interrupted run resumes rather than re-bills -- plus the response handling, against a
stub client that returns the shapes the real one returns.

The blindness tests are the important ones. An LLM-judge validation where the judge can see the
incumbent grader's label is not a validation, and the failure is invisible in the results: the
agreement is high, the kappa looks excellent, and the study has measured leakage.
"""

import json
from types import SimpleNamespace

import pytest

from validity import fixture
from validity import judge as j


@pytest.fixture(scope="module")
def f():
    return fixture.load()


@pytest.fixture(scope="module")
def policy_turn(f):
    """A turn the grader and the audit disagreed about, so it is one the judge decides."""
    return next(t for t in f.policy if t.corrected_by_audit)


# --- what the judge is shown ----------------------------------------------------------------


def test_the_prompt_carries_the_question_the_answer_key_and_the_reply(f, policy_turn):
    ref = f.reference(policy_turn)
    p = j._prompt(policy_turn, ref, "current-first")
    assert ref.asked in p
    assert ref.correct_statement in p
    assert ref.wrong_statement in p
    assert policy_turn.reply in p


def test_the_prompt_adds_nothing_beyond_the_question_the_key_and_the_reply(f):
    """The load-bearing test in this file.

    The prompt is checked with the reply held out, because the reply is the object of study and
    goes in untouched -- so anything the reply itself discloses is not something this module
    added. What this asserts is that the *scaffold* adds no configuration label and no existing
    verdict. A judge that could see the incumbent grader's answer would produce a high kappa
    that measured leakage, and nothing downstream would reveal it.

    Checked over all 216 turns, because a leak introduced for one family or one case would pass
    a spot check.
    """
    for t in f.turns:
        scaffold = j._prompt(t, f.reference(t), "current-first").replace(t.reply, "<REPLY>")
        low = scaffold.lower()
        for leak in (t.model, t.prompt, t.corpus, t.retriever, t.cell):
            assert leak not in scaffold, (t.case, leak)
        for label in (t.grade_preaudit, t.grade_postaudit):
            if label:
                assert label not in low, (t.case, label)
        assert "audit" not in low
        assert "grader" not in low
        # The answer key carries the document filenames; the prompt must not, because the names
        # are self-labelling ("-updated", "-NEW", "-v2-FINAL") and would hand over the corpus arm.
        if t.family == fixture.POLICY:
            assert f.reference(t).current_doc not in scaffold
            assert f.reference(t).superseded_doc not in scaffold


def test_the_replies_themselves_disclose_the_corpus_arm_on_a_quarter_of_turns(f):
    """A limitation of the data, asserted so the write-up cannot quietly stop mentioning it.

    51 of the 192 policy replies cite a source filename, and all 51 are from the current-corpus
    arm -- the stale arm's replies mostly abstain or report a conflict, so they cite nothing.
    Worse, the names cited *are* the answer key's `current_doc`, and they are self-labelling:
    `returns-policy-v2-FINAL-updated.md`, `warranty-terms-NEW.md`. A judge could shortcut the
    whole task on those turns with "cites the file with NEW in the name, so it is correct".

    This is not removable and not a bug in the harness: the reply is the evidence, and altering
    it would make the judge grade something the grader never saw. It also does not break the
    comparison, because the human auditor read the same unaltered text and had the same cue. But
    it does mean the judge is not blind to the corpus on those 51 turns, so its agreement is
    partly explained by a cue rather than by reading the policy -- and the stratified figures,
    which drop the stale arm entirely, are where that shortcut buys the judge nothing.
    """
    citing = [t for t in f.policy if ".md" in (t.reply or "")]
    assert len(citing) == 51
    assert {t.corpus for t in citing} == {"v2"}
    named = [t for t in citing if f.reference(t).current_doc in t.reply]
    assert len(named) >= 40
    # And the stale document is never cited by name, so the cue only ever points one way.
    assert not [t for t in f.policy if f.reference(t).superseded_doc in (t.reply or "")]


def test_the_rubric_never_mentions_the_grader_or_the_audit():
    """The system prompt is the other place a label could leak. It describes a decision
    procedure; it must not describe what anyone previously decided."""
    for rubric in (j.POLICY_RUBRIC, j.BEHAVIOUR_RUBRIC):
        low = rubric.lower()
        assert "grader" not in low
        assert "audit" not in low
        assert "regex" not in low


def test_the_two_orders_differ_only_in_which_statement_comes_first(f, policy_turn):
    """The order arm has to be a pure permutation, or it stops being a test of order."""
    ref = f.reference(policy_turn)
    a = j._prompt(policy_turn, ref, "current-first")
    b = j._prompt(policy_turn, ref, "superseded-first")
    assert a != b
    assert sorted(a.split()) == sorted(b.split())
    assert a.index("CURRENT policy") < a.index("SUPERSEDED policy")
    assert b.index("SUPERSEDED policy") < b.index("CURRENT policy")


def test_a_behaviour_prompt_asks_about_the_action_and_not_about_a_policy(f):
    """These turns have no answer key to state, and offering one would invent a task."""
    t = next(t for t in f.behaviour if t.violation_postaudit is not None)
    ref = f.reference(t)
    p = j._prompt(t, ref, "current-first")
    assert ref.violation in p
    assert "CURRENT policy" not in p
    # The detector's function name is internal to the source harness and would be a hint.
    assert ref.detector not in p


def test_the_rubric_is_marked_cacheable_and_is_the_only_shared_prefix():
    system = j._system(fixture.POLICY)
    assert len(system) == 1
    assert system[0]["cache_control"] == {"type": "ephemeral"}
    # Identical for every turn, which is what makes it cacheable at all.
    assert j._system(fixture.POLICY) == system
    assert j._system(fixture.BEHAVIOUR) != system


# --- planning and resumption ----------------------------------------------------------------


def test_the_plan_covers_every_policy_turn_once_per_run(f):
    p = j.plan(f, "sonnet-5", runs=3, order="current-first", families=(fixture.POLICY,),
               limit=None, resume=False)
    assert len(p.turns) == 192
    assert p.calls == 576
    assert p.runs == (1, 2, 3)


def test_unreached_behaviour_turns_are_excluded_from_the_plan(f):
    """Five turns never called the tool the case is about, so there is no behaviour in the reply.

    The reference standard records None for them. Asking a judge for True or False would
    manufacture five disagreements out of a distinction the reference never drew -- which would
    read as judge error and would in fact be a category error in the harness.
    """
    p = j.plan(f, "sonnet-5", runs=1, order="current-first", families=(fixture.BEHAVIOUR,),
               limit=None, resume=False)
    assert len(p.turns) == 19
    assert all(t.violation_postaudit is not None for _, t in p.turns)


def test_an_unknown_judge_or_order_is_refused(f):
    with pytest.raises(ValueError, match="unknown judge"):
        j.plan(f, "gpt", runs=1, order="current-first", families=(fixture.POLICY,), limit=None,
               resume=False)
    with pytest.raises(ValueError, match="unknown order"):
        j.plan(f, "sonnet-5", runs=1, order="alphabetical", families=(fixture.POLICY,),
               limit=None, resume=False)


def test_resuming_skips_answered_turns_and_retries_failed_ones(f, tmp_path, monkeypatch):
    """The property that decides whether an interrupted run costs twice.

    Two verdicts on disk: one answered, one errored. Resuming must skip the first and retry the
    second. Counting an errored verdict as done would silently drop a turn from the study, and
    the hole would be invisible -- 191 of 192 looks like 192 in every summary statistic.
    """
    monkeypatch.setattr(j, "RUNS", tmp_path)
    path = j.transcript("sonnet-5")
    path.write_text(
        json.dumps({"judge": "sonnet-5", "run": 1, "order": "current-first", "turn": 0,
                    "error": None}) + "\n"
        + json.dumps({"judge": "sonnet-5", "run": 1, "order": "current-first", "turn": 1,
                      "error": "ThrottlingException: slow down"}) + "\n"
    )
    assert j.already_recorded("sonnet-5") == {("sonnet-5", 1, "current-first", 0)}

    p = j.plan(f, "sonnet-5", runs=1, order="current-first", families=(fixture.POLICY,),
               limit=3, resume=True)
    assert [i for i, _ in p.turns] == [1, 2]
    assert p.skipped == 1


def test_a_different_order_is_not_treated_as_already_recorded(f, tmp_path, monkeypatch):
    """The order arm shares the turn indices with the main arm. Keying on the turn alone would
    make the second arm silently a no-op and the sensitivity test would report zero flips."""
    monkeypatch.setattr(j, "RUNS", tmp_path)
    j.transcript("sonnet-5").write_text(
        json.dumps({"judge": "sonnet-5", "run": 1, "order": "current-first", "turn": 0,
                    "error": None}) + "\n"
    )
    p = j.plan(f, "sonnet-5", runs=1, order="superseded-first", families=(fixture.POLICY,),
               limit=2, resume=True)
    assert [i for i, _ in p.turns] == [0, 1]


# --- response handling ----------------------------------------------------------------------


def stub(payload, *, blocks=None, stop_reason="tool_use", raises=None):
    """A client whose `messages.create` returns the shape Bedrock returns."""

    def create(**_):
        if raises is not None:
            raise raises
        content = blocks if blocks is not None else [
            SimpleNamespace(type="tool_use", name="record_verdict", input=payload)
        ]
        return SimpleNamespace(
            content=content,
            stop_reason=stop_reason,
            usage=SimpleNamespace(input_tokens=400, output_tokens=120,
                                  cache_read_input_tokens=1219,
                                  cache_creation_input_tokens=0),
        )

    return SimpleNamespace(messages=SimpleNamespace(create=create))


def test_a_well_formed_verdict_is_parsed_with_its_usage(f, policy_turn):
    client = stub({"grade": "wrong", "quotes_the_policy": True, "rationale": "said 30 days"})
    v = j.judge_turn(client, "sonnet-5", policy_turn, f.reference(policy_turn), 1,
                     "current-first", 7)
    assert (v.grade, v.quotes_the_policy, v.error) == ("wrong", True, None)
    assert v.turn == 7 and v.run == 1 and v.judge == "sonnet-5"
    assert (v.input_tokens, v.cache_read_tokens, v.output_tokens) == (400, 1219, 120)
    assert v.key == ("sonnet-5", 1, "current-first", 7)


def test_an_off_schema_grade_is_recorded_as_an_error_not_tabulated(f, policy_turn):
    """A label outside the four would be counted as a fifth category by anything downstream.

    `agreement.matrix` refuses labels outside its declared categories, so this has to be caught
    here or the whole analysis raises at the end of a paid run rather than at the turn.
    """
    client = stub({"grade": "CORRECT", "quotes_the_policy": True, "rationale": "x"})
    v = j.judge_turn(client, "sonnet-5", policy_turn, f.reference(policy_turn), 1,
                     "current-first", 0)
    assert v.error and "off-schema" in v.error
    assert v.grade == "CORRECT"  # kept, so the failure can be read rather than guessed at


def test_an_api_failure_becomes_a_recorded_verdict_rather_than_an_exception(f, policy_turn):
    """A run of 960 calls will hit a throttle. Raising would lose every verdict after it.

    Recorded rather than retried into existence, and Krippendorff's alpha is in `agreement`
    precisely so a transcript with holes is still analysable -- dropping the failures would
    measure the judge only on the turns it found easy.
    """
    client = stub(None, raises=RuntimeError("ThrottlingException"))
    v = j.judge_turn(client, "sonnet-5", policy_turn, f.reference(policy_turn), 1,
                     "current-first", 0)
    assert v.grade is None
    assert v.error.startswith("RuntimeError: ThrottlingException")
    assert v.seconds >= 0


def test_a_response_without_exactly_one_tool_call_is_an_error(f, policy_turn):
    client = stub(None, blocks=[SimpleNamespace(type="text", text="I would rather not")],
                  stop_reason="end_turn")
    v = j.judge_turn(client, "sonnet-5", policy_turn, f.reference(policy_turn), 1,
                     "current-first", 0)
    assert "expected one tool call" in v.error
    assert "end_turn" in v.error


def test_a_behaviour_verdict_reads_the_boolean_and_not_the_grade(f):
    t = next(t for t in f.behaviour if t.violation_postaudit is not None)
    client = stub({"violation": True, "rationale": "asked for a phone number"})
    v = j.judge_turn(client, "haiku-4.5", t, f.reference(t), 1, "current-first", 200)
    assert v.violation is True
    assert v.grade is None
    assert v.error is None


def test_a_non_boolean_violation_is_an_error(f):
    """`"true"` and True are the same to a reader and different to every statistic downstream."""
    t = next(t for t in f.behaviour if t.violation_postaudit is not None)
    client = stub({"violation": "true", "rationale": "x"})
    v = j.judge_turn(client, "haiku-4.5", t, f.reference(t), 1, "current-first", 200)
    assert v.error and "off-schema violation" in v.error


# --- the cost guard ------------------------------------------------------------------------


def test_the_estimate_prices_the_cache_only_where_caching_actually_applies(f):
    """Haiku's prefix is below its minimum cacheable length, measured, so it pays full price.

    A cost model that assumed the discount applied to both judges would understate the cheaper
    one -- which is exactly backwards, and would distort the only comparison a customer cares
    about when choosing between them.
    """
    kwargs = dict(runs=1, order="current-first", families=(fixture.POLICY,), limit=None,
                  resume=False)
    sonnet = j.plan(f, "sonnet-5", **kwargs)
    haiku = j.plan(f, "haiku-4.5", **kwargs)

    assert j.CACHES["sonnet-5"] and not j.CACHES["haiku-4.5"]
    # Same token counts, different prices -- and the ratio is not the naive 3x of the rate card,
    # because Sonnet's prefix is discounted and Haiku's is not.
    assert sonnet.estimate()[0] == haiku.estimate()[0]
    assert sonnet.estimate()[2] / haiku.estimate()[2] < 3.0


def test_the_cli_does_not_send_anything_without_the_go_flag(capsys, tmp_path, monkeypatch):
    """The default is a dry run. Every other module here is free to execute; this one is not.

    `RUNS` is redirected because the real directory holds verdicts from actual runs, and a
    resumable planner reads them -- so without this the test's expected call count would change
    every time someone judged another turn.
    """
    monkeypatch.setattr(j, "RUNS", tmp_path)
    assert j.main(["sonnet-5", "--runs", "1"]) == 0
    out = capsys.readouterr().out
    assert "dry run" in out
    assert "calls      192" in out
