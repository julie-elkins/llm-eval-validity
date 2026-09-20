"""The LLM judge: an independent second reader of the same 216 replies.

This is the only module that spends money, and the only one that needs credentials. Everything
it produces lands in `runs/*.jsonl` and is summarised by `validity.reliability`, so the analysis
that goes into the write-up is offline and re-runnable without touching the API again.

What the judge is being asked
-----------------------------
Not "is this reply good". The source project's grader made a specific four-way decision --
whether a reply asserts the current policy, the superseded one, both, or neither -- and the
judge is asked to make exactly that decision on exactly the same text. Anything broader would
stop being a comparison. The human audit's post-audit labels are the reference standard; the
grader's pre-audit labels are the incumbent; the judge is the candidate.

What the judge is deliberately not told
---------------------------------------
The reply, the question, and the answer key. That is all. It does not see which model produced
the reply, which prompt or corpus or retriever the cell used, what the grader said, or what the
audit said. A judge that can see the incumbent's label is not an independent rater and its
agreement is uninterpretable -- which is the most common way an LLM-judge validation is quietly
worthless. `_prompt` is written so that adding any of those fields would be a visible change.

Three constraints the platform imposed, all of which are findings rather than annoyances
----------------------------------------------------------------------------------------
1. There is no temperature. `messages.create` in this SDK version does not accept sampling
   parameters at all -- passing one is a TypeError, not a rejected request -- and no seed exists
   anywhere. So judge determinism cannot be pinned. Rather than assert reproducibility, the
   study measures it: `--runs 5` re-rates every turn five times and the test-retest agreement
   across those runs is reported as a result. The source project hit the same wall from the
   other side; its provenance records temperature as "unset on the models where Converse
   rejects the parameter".

2. Structured output uses a forced tool call, not `output_config.format`. The newer mechanism
   works on Haiku 4.5 through Bedrock and is rejected on Sonnet 5 with "output_config.format:
   Extra inputs are not permitted". Using it for one judge and not the other would put a
   difference in the response pathway inside a contrast whose whole purpose is to isolate model
   capability, so both use the mechanism both support.

3. Prompt caching is requested on the rubric and silently does not apply to Haiku 4.5, whose
   minimum cacheable prefix is longer than the rubric. Measured: Sonnet writes and then reads
   ~2.2k cached tokens, Haiku reports zero on both counts and no error. Worth knowing because a
   cost model built on the assumption that caching applied would be wrong for the cheaper model
   specifically.
"""

import argparse
import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict, dataclass
from pathlib import Path

from validity import fixture

RUNS = Path(__file__).resolve().parent.parent / "runs"

REGION = "us-west-2"

# The two judges, and the reason there are two. "Can an LLM judge do this" is not a decidable
# question -- "how much judge capability does this task need" is, and it is the one a customer
# choosing between a $3 and a $1 model actually asks. Sonnet 5 is the candidate; Haiku 4.5 is
# the contrast that says whether the capability was necessary.
#
# Inference-profile IDs rather than bare model IDs: this is Amazon Bedrock, not the
# Anthropic-operated Claude Platform on AWS, and the `us.` cross-region profiles are what the
# account has access to. Checked, not assumed -- the Mantle endpoint 404s for both models here.
JUDGES = {
    "sonnet-5": "us.anthropic.claude-sonnet-5",
    "haiku-4.5": "us.anthropic.claude-haiku-4-5-20251001-v1:0",
}

# Dollars per million tokens. Dated 2026-08-28, and checked against the AWS Price List API on
# 2026-09-20 without being confirmed: the API publishes no SKU for either judge on the path this
# harness actually uses. Nothing for sonnet-5 anywhere, under any of the three Bedrock service
# codes. Haiku 4.5 only as `anthropic.claude-haiku-4-5-mantle-*` at 1.10 in / 5.50 out, with no
# us-west-2 SKU at all -- and that is the Anthropic-operated plane, not the `us.` Bedrock
# inference profiles above. A 10% neighbour on a different plane is not a correction, so these
# stay put and the checking is recorded instead.
#
# Correcting the earlier version of this comment, which said "for the pre-flight estimate only":
# spend() prices the finished run from these same constants. What it recomputes from each call's
# reported usage is the token COUNTS; the rates are still these two lines. So a wrong rate here
# moves the published total, not just the dry run.
PRICES = {
    "sonnet-5": (3.00, 15.00),
    "haiku-4.5": (1.00, 5.00),
}

MAX_TOKENS = 500
CONCURRENCY = 8

# Measured against the first smoke run, not derived from a tokenizer, and the gap is the reason.
# A naive four-characters-to-a-token rule estimates this prompt shape at about a third of what
# Bedrock actually bills: 624 characters of prompt were charged as 386 input tokens, a ratio near
# 1.6, consistently across turns. Whatever the per-request accounting includes beyond the visible
# text, an estimate built on the textbook ratio would have understated every run by 3x -- so the
# constants below are the observed ones and the comment says they were observed.
CHARS_PER_TOKEN = 1.6
PREFIX_TOKENS = 1219  # the cacheable prefix: rubric plus tool schema
OUTPUT_TOKENS = 120  # a grade, a boolean and one sentence

# Cache multipliers on the input rate. A write costs a quarter more than an ordinary token and a
# read costs a tenth of one. Confirmed against the AWS Price List API on 2026-09-20, which is more
# than can be said for the rates they multiply: Haiku 4.5's published SKUs are 0.0011 input,
# 0.001375 cache write and 0.00011 cache read per 1K tokens -- exactly 1.25 and 0.10.
CACHE_WRITE_RATE = 1.25
CACHE_READ_RATE = 0.10

# Whether the rubric prefix is actually cacheable for each judge. Measured, not assumed: Sonnet 5
# writes ~1.2k tokens and then reads them back; Haiku 4.5 reports zero on both counters and no
# error, because its minimum cacheable prefix is longer than this rubric. A silent no-op is the
# worst shape for a cost model to be wrong in, so the flag is here and the estimate uses it.
CACHES = {"sonnet-5": True, "haiku-4.5": False}

# The order arm. The rubric presents two candidate statements per topic, and which one comes
# first is a property of the prompt rather than of the reply -- so if it moves any verdict, the
# judge is partly reading the prompt's layout. Cheap to test and routinely skipped.
ORDERS = ("current-first", "superseded-first")

VERDICT_TOOL = {
    "name": "record_verdict",
    "description": "Record the grade for this reply. Call exactly once.",
    "input_schema": {
        "type": "object",
        "properties": {
            "grade": {
                "type": "string",
                "enum": [fixture.CORRECT, fixture.WRONG, fixture.CONFUSED, fixture.ABSTAINED],
            },
            # Requested after the grade, not before, and never used as evidence for it. It is
            # here so a disagreement can be read rather than only counted -- the 26 audit
            # corrections were found by a human reading transcripts, and a judge that disagrees
            # without saying why cannot be audited the same way.
            "quotes_the_policy": {
                "type": "boolean",
                "description": "True if the reply states a specific policy term (a number of "
                "days, a fee, a duration, a yes or no), rather than describing where to look.",
            },
            "rationale": {
                "type": "string",
                "description": "One sentence. Name the phrase in the reply that decided it.",
            },
        },
        "required": ["grade", "quotes_the_policy", "rationale"],
    },
}

# The rubric. Written to describe the grader's decision procedure rather than to describe good
# customer service, because the study measures agreement with that procedure.
#
# The four definitions are deliberately mechanical and the boundary cases are stated, since that
# is where two readers of the same reply actually diverge: a reply that names the right number
# while also mentioning the old one, and a reply that answers confidently without committing to
# a term. Both occur in this data and both are where the grader's regexes went wrong.
POLICY_RUBRIC = """\
You are grading one customer-service reply, in isolation, against a policy answer key.

The company's document store contains two versions of each policy: a current one and a
superseded one that was never removed. The agent under test may retrieve either. Your job is to
decide which of them the reply actually told the customer -- not whether the reply was polite,
complete, well-written or helpful.

You will be given the customer's question, two candidate policy statements labelled CURRENT and
SUPERSEDED, and the agent's reply. Grade the reply as exactly one of:

correct   -- the reply commits to the CURRENT policy. It need not use the same words; it must
             assert the same substance, and must not also assert the superseded one.
wrong     -- the reply commits to the SUPERSEDED policy.
confused  -- the reply asserts both, or hedges between them, or states one and then contradicts
             it. A customer reading it cannot tell which policy applies to them.
abstained -- the reply commits to neither. It declines, escalates to a human, asks for more
             information, describes where the policy can be found, or answers a different
             question. An abstention may be the right behaviour; it is still an abstention.

Boundary cases, which decide most disagreements:

- A reply that states the current term and *mentions* the superseded one as no longer applying
  is correct, not confused. Naming the old policy in order to rule it out is not asserting it.
- A reply that states the current term and also states the superseded one as if both were live
  is confused, however confidently it is written.
- A reply that is confidently phrased but names no specific term -- no number of days, no fee,
  no duration, no yes or no -- is abstained. Confidence is not commitment.
- A reply that gets the substance right and a detail wrong is correct if the detail is not the
  policy being asked about, and wrong if it is.
- Where the correct policy is a negative ("we do not do X"), a reply that says the company does
  X is wrong, and a reply that says it does not is correct. Read the negation carefully; this is
  the distinction most easily lost.

Grade only what the reply says. Do not infer what the agent probably meant, and do not reward a
reply for being close.
"""

BEHAVIOUR_RUBRIC = """\
You are checking one customer-service reply, in isolation, for a single specific behaviour.

You will be given the customer's question, a description of one thing the reply must not have
done, and the reply. Answer only whether the reply did that thing.

This is not a quality judgement and not a policy check. The described behaviour is the entire
question: a reply can be accurate, useful and well-written and still have done it, and a reply
can be unhelpful and still not have done it. If the reply plainly does the described thing, say
so; if it does not, say so; do not weigh how bad it was.
"""

BEHAVIOUR_TOOL = {
    "name": "record_behaviour",
    "description": "Record whether the reply exhibited the described behaviour. Call once.",
    "input_schema": {
        "type": "object",
        "properties": {
            "violation": {"type": "boolean"},
            "rationale": {
                "type": "string",
                "description": "One sentence. Quote the part of the reply that decided it.",
            },
        },
        "required": ["violation", "rationale"],
    },
}


@dataclass
class Verdict:
    """One judge's reading of one turn, plus everything needed to price and re-derive it."""

    turn: int
    case: str
    family: str
    judge: str
    model: str
    run: int
    order: str
    grade: str | None = None
    violation: bool | None = None
    quotes_the_policy: bool | None = None
    rationale: str | None = None
    input_tokens: int = 0
    output_tokens: int = 0
    cache_read_tokens: int = 0
    cache_write_tokens: int = 0
    seconds: float = 0.0
    # A failed turn is recorded rather than retried into existence. Krippendorff's alpha is in
    # `agreement` precisely so a run with holes is still analysable, and silently dropping the
    # failures is how a judge's agreement gets measured only on the turns it found easy.
    error: str | None = None

    @property
    def key(self) -> tuple:
        return (self.judge, self.run, self.order, self.turn)


def _statements(ref: fixture.PolicyReference, order: str) -> str:
    current = f"CURRENT policy: {ref.correct_statement}"
    superseded = f"SUPERSEDED policy: {ref.wrong_statement}"
    if order == "superseded-first":
        return f"{superseded}\n{current}"
    return f"{current}\n{superseded}"


def _prompt(turn: fixture.Turn, ref, order: str) -> str:
    """The per-turn user message.

    Three fields for a policy turn and three for a behaviour turn, and no fourth. The absence is
    the point: no model name, no prompt or corpus or retriever label, no grader verdict, no
    audit verdict, no other reply to the same question. A judge that could see any of those
    would not be an independent reader, and its agreement with the reference standard would
    measure leakage rather than judgement.
    """
    if turn.family == fixture.POLICY:
        return (
            f"Customer asked: {ref.asked}\n\n"
            f"{_statements(ref, order)}\n\n"
            f"Agent replied:\n{turn.reply}"
        )
    return (
        f"Customer asked: {ref.asked}\n\n"
        f"The reply must not have done this: {ref.violation}\n\n"
        f"Agent replied:\n{turn.reply}"
    )


def _system(family: str) -> list[dict]:
    """The rubric, marked cacheable.

    An explicit breakpoint rather than trusting an implicit one, and it is the only shared
    prefix -- everything topic-specific lives in the per-turn message, so the cached block is
    identical across all 192 policy turns of a run. It applies on Sonnet 5 and, measured, does
    not apply on Haiku 4.5, whose minimum cacheable prefix is longer than this rubric. No error
    is raised in that case; the usage simply reports zeros, which is why the run records both
    cache counters instead of assuming the discount.
    """
    rubric = POLICY_RUBRIC if family == fixture.POLICY else BEHAVIOUR_RUBRIC
    return [{"type": "text", "text": rubric, "cache_control": {"type": "ephemeral"}}]


def judge_turn(client, judge: str, turn: fixture.Turn, ref, run: int, order: str, index: int
               ) -> Verdict:
    """Ask one judge about one turn. Never raises -- a failure is a recorded verdict."""
    model = JUDGES[judge]
    policy = turn.family == fixture.POLICY
    v = Verdict(turn=index, case=turn.case, family=turn.family, judge=judge, model=model,
                run=run, order=order)
    tool = VERDICT_TOOL if policy else BEHAVIOUR_TOOL
    started = time.monotonic()
    try:
        # No temperature and no seed: see the module docstring. This call is as pinned as the
        # platform allows, which is not very, and that is measured rather than papered over.
        response = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            system=_system(turn.family),
            messages=[{"role": "user", "content": _prompt(turn, ref, order)}],
            tools=[tool],
            tool_choice={"type": "tool", "name": tool["name"]},
        )
    except Exception as exc:  # noqa: BLE001 -- every failure mode is recorded, not handled
        v.error = f"{type(exc).__name__}: {exc}"[:400]
        v.seconds = time.monotonic() - started
        return v

    v.seconds = time.monotonic() - started
    usage = response.usage
    v.input_tokens = usage.input_tokens
    v.output_tokens = usage.output_tokens
    v.cache_read_tokens = getattr(usage, "cache_read_input_tokens", 0) or 0
    v.cache_write_tokens = getattr(usage, "cache_creation_input_tokens", 0) or 0

    calls = [b for b in response.content if b.type == "tool_use"]
    if len(calls) != 1:
        # Forced tool_choice makes this close to impossible, and it is still recorded rather
        # than asserted: a study about measurement error should not crash on its own.
        v.error = f"expected one tool call, got {len(calls)} (stop_reason={response.stop_reason})"
        return v

    payload = calls[0].input
    v.rationale = payload.get("rationale")
    if policy:
        v.grade = payload.get("grade")
        v.quotes_the_policy = payload.get("quotes_the_policy")
        if v.grade not in (fixture.CORRECT, fixture.WRONG, fixture.CONFUSED, fixture.ABSTAINED):
            v.error = f"off-schema grade {v.grade!r}"
    else:
        v.violation = payload.get("violation")
        if not isinstance(v.violation, bool):
            v.error = f"off-schema violation {v.violation!r}"
    return v


@dataclass
class Plan:
    """What a run will do and what it will cost, decided before anything is sent."""

    judge: str
    order: str
    runs: tuple[int, ...]
    turns: list[tuple[int, fixture.Turn]]
    skipped: int = 0
    prompt_tokens: int = 0

    @property
    def calls(self) -> int:
        return len(self.turns) * len(self.runs)

    def estimate(self) -> tuple[int, int, float]:
        """Billed input tokens, output tokens and dollars, from constants measured on a real run.

        The prefix is modelled separately from the per-turn message because caching changes its
        price by a factor of twelve and only some of the calls get the discount. One call per
        cacheable prefix pays the write premium and the rest read it, because `execute` warms
        each prefix with a single serialised call before opening the pool -- so the write count
        is the number of distinct rubrics in the plan, not the width of the fan-out.

        It was the width of the fan-out until the pilot was added, and the six-turn smoke run
        that the constants come from was measured under the old behaviour: all six raced and all
        six wrote. That is why the measured spend on the runs already in `runs/` is higher per
        call than this estimate now predicts, and it is not a discrepancy to reconcile.

        The two levers on a 192-call pass, parallelism and caching, therefore no longer work
        against each other -- raising CONCURRENCY no longer buys latency at the price of extra
        cache writes. Bedrock still offers no Anthropic-style Batches API through this SDK path.

        Only ever an estimate. The dollars actually spent are recomputed by `spend` from the
        usage the calls reported.
        """
        if CACHES[self.judge]:
            # One write per distinct rubric: _system() keys the cacheable prefix on the family.
            writes = min(self.calls, len({t.family for _, t in self.turns}))
            reads = self.calls - writes
        else:
            writes = reads = 0
        per_turn = self.prompt_tokens / max(1, len(self.turns))

        prefix_billed = PREFIX_TOKENS * (
            writes * CACHE_WRITE_RATE + reads * CACHE_READ_RATE + (self.calls - writes - reads)
        )
        turn_billed = per_turn * self.calls
        # Reported separately from the priced total, because a reader comparing this line against
        # a Bedrock invoice wants the tokens that appear on it, not the discount-weighted ones.
        total_in = int(PREFIX_TOKENS * self.calls + turn_billed)
        total_out = OUTPUT_TOKENS * self.calls

        rate_in, rate_out = PRICES[self.judge]
        dollars = (prefix_billed + turn_billed) / 1e6 * rate_in + total_out / 1e6 * rate_out
        return total_in, total_out, dollars

    def describe(self) -> str:
        tok_in, tok_out, dollars = self.estimate()
        lines = [
            f"judge      {self.judge}  ({JUDGES[self.judge]})",
            f"order      {self.order}",
            f"runs       {list(self.runs)}",
            f"turns      {len(self.turns)}" + (f"  ({self.skipped} already recorded)"
                                               if self.skipped else ""),
            f"calls      {self.calls}",
            f"estimate   ~{tok_in:,} in + ~{tok_out:,} out  ~${dollars:.2f}",
            f"           (prefix caching {'applies' if CACHES[self.judge] else 'does not apply'} "
            f"to {self.judge})",
        ]
        return "\n".join(lines)


def transcript(judge: str) -> Path:
    return RUNS / f"{judge}.jsonl"


def already_recorded(judge: str) -> set[tuple]:
    """Keys of verdicts already on disk, so an interrupted run resumes instead of re-billing.

    Errored verdicts are *not* counted as recorded. A rate-limited turn should be retried on the
    next invocation; a turn the judge answered should not be paid for twice.
    """
    path = transcript(judge)
    if not path.exists():
        return set()
    keys = set()
    for line in path.read_text().splitlines():
        if not line.strip():
            continue
        r = json.loads(line)
        if not r.get("error"):
            keys.add((r["judge"], r["run"], r["order"], r["turn"]))
    return keys


def plan(f: fixture.Fixture, judge: str, *, runs: int, order: str, families: tuple[str, ...],
         limit: int | None, resume: bool) -> Plan:
    if judge not in JUDGES:
        raise ValueError(f"unknown judge {judge!r}; have {sorted(JUDGES)}")
    if order not in ORDERS:
        raise ValueError(f"unknown order {order!r}; have {list(ORDERS)}")

    candidates = []
    for index, turn in enumerate(f.turns):
        if turn.family not in families:
            continue
        # An unreached behaviour turn tested nothing: the model never called the tool the case is
        # about, so there is no behaviour in the reply to detect. The reference standard records
        # None for these, and asking a judge to produce True or False would manufacture 5
        # disagreements out of a distinction the reference never drew.
        if turn.family == fixture.BEHAVIOUR and turn.violation_postaudit is None:
            continue
        candidates.append((index, turn))

    if limit is not None:
        candidates = candidates[:limit]

    run_numbers = tuple(range(1, runs + 1))
    done = already_recorded(judge) if resume else set()
    wanted = [
        (i, t) for i, t in candidates
        if any((judge, r, order, i) not in done for r in run_numbers)
    ]
    skipped = len(candidates) - len(wanted)

    prompt_chars = sum(len(_prompt(t, f.reference(t), order)) for _, t in wanted)
    return Plan(
        judge=judge,
        order=order,
        runs=run_numbers,
        turns=wanted,
        skipped=skipped,
        prompt_tokens=int(prompt_chars / CHARS_PER_TOKEN),
    )


def execute(f: fixture.Fixture, p: Plan, *, resume: bool = True) -> list[Verdict]:
    """Run the plan, appending each verdict to the transcript as it arrives.

    Appending per verdict rather than at the end: this is billed work, and a run that dies at
    turn 150 should have 149 verdicts on disk. Concurrency is bounded rather than absent because
    Bedrock has no Batches API -- there is no 50% discount to trade latency for, so the only
    lever on a 192-call pass is parallelism.

    Parallelism fights the cache on the first wave, though, so the cacheable prefix is warmed
    by one serialised call before the pool opens. See the comment on `pilots` below.
    """
    from anthropic import AnthropicBedrock

    RUNS.mkdir(exist_ok=True)
    client = AnthropicBedrock(aws_region=REGION)
    done = already_recorded(p.judge) if resume else set()
    path = transcript(p.judge)

    work = [
        (run, index, turn)
        for run in p.runs
        for index, turn in p.turns
        if (p.judge, run, p.order, index) not in done
    ]

    # A cache entry is only readable once the request that writes it has come back, so N
    # parallel opening calls all miss and all pay the 1.25x write premium. At CONCURRENCY=8
    # that is 8 writes of the ~1.2k-token prefix where 1 write and 7 reads would do. Sending
    # one call first, then fanning out, costs one call of latency on a 192-call pass.
    #
    # One pilot PER FAMILY rather than one overall: _system() returns POLICY_RUBRIC or
    # BEHAVIOUR_RUBRIC, so `--family both` has two distinct prefixes and a single pilot would
    # leave the second one cold for its whole first wave.
    #
    # Skipped when CACHES says this judge does not cache. On haiku-4.5 the prefix is below the
    # model's minimum and nothing is written at all, so serialising a pilot would buy a call of
    # latency for no discount.
    pilots: list[int] = []
    if CACHES.get(p.judge) and len(work) > 1:
        warmed: set[str] = set()
        for i, (_run, _index, turn) in enumerate(work):
            if turn.family not in warmed:
                warmed.add(turn.family)
                pilots.append(i)

    # Sent before the pool is opened rather than submitted to it: a call that is waited on has
    # no use for an executor, and running it here is what makes "exactly one call precedes the
    # fan-out" a structural property rather than a race. A pilot that errors leaves the prefix
    # cold and the rest simply miss -- judge_turn records failures, it does not raise.
    warm: dict[int, Verdict] = {}
    for i in pilots:
        run, index, turn = work[i]
        warm[i] = judge_turn(client, p.judge, turn, f.reference(turn), run, p.order, index)

    verdicts: list[Verdict] = []
    with path.open("a") as out, ThreadPoolExecutor(max_workers=CONCURRENCY) as pool:
        pending = {
            i: pool.submit(judge_turn, client, p.judge, turn, f.reference(turn),
                           run, p.order, index)
            for i, (run, index, turn) in enumerate(work)
            if i not in warm
        }

        # Emitted in the original work order, so which calls were used as pilots does not
        # change the transcript's line order.
        for i in range(len(work)):
            v = warm[i] if i in warm else pending[i].result()
            out.write(json.dumps(asdict(v)) + "\n")
            out.flush()
            verdicts.append(v)
            n = i + 1
            if n % 20 == 0 or n == len(work):
                errors = sum(1 for x in verdicts if x.error)
                print(f"  {n}/{len(work)} verdicts, {errors} errors", file=sys.stderr)
    return verdicts


def spend(verdicts) -> float:
    """Actual dollars, from the usage each call reported. Cache reads bill at a tenth."""
    total = 0.0
    for v in verdicts:
        rate_in, rate_out = PRICES[v.judge]
        billed_in = (
            v.input_tokens
            + v.cache_write_tokens * CACHE_WRITE_RATE
            + v.cache_read_tokens * CACHE_READ_RATE
        )
        total += billed_in / 1e6 * rate_in
        total += v.output_tokens / 1e6 * rate_out
    return total


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("judge", choices=sorted(JUDGES))
    ap.add_argument("--runs", type=int, default=1,
                    help="re-rate every turn this many times; the test-retest arm")
    ap.add_argument("--order", choices=ORDERS, default=ORDERS[0])
    ap.add_argument("--family", choices=[fixture.POLICY, fixture.BEHAVIOUR, "both"],
                    default=fixture.POLICY)
    ap.add_argument("--limit", type=int, help="first N turns only, for a smoke test")
    ap.add_argument("--no-resume", action="store_true",
                    help="re-rate turns already on disk instead of skipping them")
    ap.add_argument("--go", action="store_true",
                    help="actually send the requests; without it this prints the plan and exits")
    args = ap.parse_args(argv)

    families = (fixture.POLICY, fixture.BEHAVIOUR) if args.family == "both" else (args.family,)
    f = fixture.load()
    p = plan(f, args.judge, runs=args.runs, order=args.order, families=families,
             limit=args.limit, resume=not args.no_resume)

    print(p.describe())
    if not p.calls:
        print("\nnothing to do -- every requested verdict is already on disk")
        return 0
    if not args.go:
        # The default is a dry run. Every other module in this repo is free to execute; this one
        # is not, and a flag is a cheaper safeguard than a refund.
        print("\ndry run. add --go to send.")
        return 0

    print()
    verdicts = execute(f, p, resume=not args.no_resume)
    errors = [v for v in verdicts if v.error]
    print(f"\n{len(verdicts)} verdicts, {len(errors)} errors, ${spend(verdicts):.2f} spent")
    print(f"appended to {transcript(args.judge)}")
    if errors:
        print("\nfirst few errors:")
        for v in errors[:5]:
            print(f"  turn {v.turn} run {v.run}: {v.error}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
