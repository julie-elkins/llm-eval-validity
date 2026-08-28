# Is the eval trustworthy?

A validity and reliability study of an LLM evaluation harness, run the way a certification
exam is validated rather than the way an eval suite usually is.

Most published eval work reports a pass rate. This asks the prior question: **does the
instrument that produced the pass rate measure what it claims to, precisely enough to support
the decision being made on it?** In certification that question has a settled methodology --
item analysis, inter-rater reliability, standard setting, a documented reference standard --
and almost all of it transfers to evaluating an AI system. This repository applies it to a
real, already-published eval run and reports what it finds, including where it contradicts the
original write-up.

The data is 216 graded agent turns from
[northwind-connect-ai](https://github.com/JulieElkinsAWS/northwind-connect-ai): a Claude-powered
customer-service agent tested across a 24-cell factorial design (3 models x 2 prompts x 2
document corpora x 2 retrievers). It is vendored here as a fixture, not re-run — see
[Provenance](#provenance).

**Two ways in:** [docs/executive-summary.md](docs/executive-summary.md) is the one-page
deployment decision; [docs/methodology.md](docs/methodology.md) is the technical companion —
which psychometric method each step borrows, where the borrowing breaks down because the examinee
is a system rather than a person, and every design decision that would move the numbers.

## What it found

Five findings, in descending order of how much they change the original conclusions.

**1. Both LLM judges agree with the human auditor more closely than the harness's own grader
did — and a single-run comparison of the two judges would have reported a winner that does not
exist.**
Two judges (Sonnet 5 and Haiku 4.5) read all 192 policy replies five times each, blind to the
configuration, the incumbent grade and the audit verdict. Against the human reference both beat
the regex grader (kappa +0.87 and +0.90 against +0.77). But read pass 1 alone and Haiku leads
Sonnet by 0.03 of kappa; read all five and Haiku's range (0.882–0.935) contains Sonnet's
(0.872–0.892). **The between-model difference is no larger than the within-model, run-to-run
difference**, and there is no temperature or seed to suppress it — sampling parameters are not
available at all in the SDK's 1.x line. Every judge comparison this study could find reports a
single run.

Framed as what it would actually be deployed for — a screen deciding which turns a human
should read — Haiku flags 15.6% of turns and catches all 23 of the grader's policy errors. The
interval is the honest number: 23/23 is still consistent with a true sensitivity of 0.86, so as
many as one grader error in seven could be missed by a screen that looked flawless here.

And the coefficient itself fails on half the data. Split by corpus and the stale-corpus arm
gives 95% raw agreement with a kappa of 0.00 — because `kappa_max` there is *also* 0.00. Both
the judges and the human answer `abstained` almost everywhere, and a rater using one category
pins kappa at zero however good it is. Reported alone, kappa would describe the study's
best-behaved stratum as its worst failure. Full report: [docs/judge-validation.md](docs/judge-validation.md).

**2. The eval is too small to license the decision it was built for, and the pooled rate it
reports would ship a failing family.**
Two standards were declared before any score was looked at — incorrect policy statements ≤2%,
restricted-action violations ≤5% — and judged conjunctively, on the interval bound rather than
the point estimate. Both fail, for opposite reasons that a single pass/fail flag erases. Policy
handling has a *perfect record and insufficient evidence*: 0 errors in the 79 turns any
configuration answered, which bounds the error rate at 4.6%. It takes about 189 answered turns
to demonstrate 2%, so **that family fails on sample size and no improvement to the agent would
fix it.** Behaviour has an *observed failure*: 3 violations in 19 turns, lower bound 5.5%,
already above its tolerance. Pool the two the way a harness does — 3 failures over all 211
scored turns — and you get 1.4%, which clears the tighter tolerance on the point estimate. Two
independent mistakes, pooling across consequences and testing a point estimate rather than a
bound, and either alone turns two failures into a green dashboard.

The deployable number is not a pass rate. With current documents the system **automates 77.1%
of policy volume [67.7%, 84.4%] with its error rate on those turns bounded at 4.9%**; on stale
documents coverage collapses to 5.2%, so the value of deploying it is a claim about the document
pipeline rather than about the model. Automating beats escalating everything until one wrong
answer costs more than about 20 unnecessary escalations — and the lever that moves that
break-even is sample size, not model choice, because the bound is what sets it. A per-cell cut
score cannot be set at all: at eight items, 7/8 is consistent with a true accuracy anywhere in
[52.9%, 97.8%], and every candidate cut would reclassify more than one configuration in eight on
a re-run. Full report: [docs/cut-score.md](docs/cut-score.md).

**3. The eval's own item analysis is confounded, and the confound flatters it.**
Run over all 24 configurations, all eight test questions look excellent — corrected
item-total correlations of +0.68 to +0.90, Cronbach's alpha 0.94. That is the table an eval
harness produces by default, and it is an artefact. Nine of the 24 configurations scored
0/8, and all nine are the stale-corpus arm, so the lower comparison group consists entirely
of configurations that answered nothing at all. Every question "discriminates" because every
question detects the corpus. It is one fact discovered eight times.

Stratify to the 12 configurations where the corpus is not the binding constraint and mean
inter-item correlation falls from +0.65 to +0.22, alpha from 0.94 to 0.76 — and two of the
eight questions turn out to be at ceiling (12/12), unable to rank any configuration that has
the current documents. They are corpus regression checks, not comparison items.

**4. "No measurable difference" was a statement about the design, not about prompts.**
The original run found 42.7% vs 39.6% on the prompt axis and reported no difference. With a
Newcombe interval that is +3.1 points [-10.6, +16.7]: the design could not have detected
anything smaller than about 14 points, so a real 10-point prompt effect would have been
missed. The null survives stratification (-4.2 points [-20.7, +12.6] within the current
corpus), so it is not a floor artefact — but it remains uninformative rather than negative.

**5. Two findings the original run understated, and one it overstated.**
Because every marginal pools the floor arm, the published figures *understate* the effects
that are real: the retriever contrast is +15.6 points [+1.7, +28.7] pooled but +29.2 points
[+12.5, +44.2] within the current corpus, and the model contrast +25.0 rather than +37.5. The
pooled retriever bound clears zero by only 1.7 points — inside the scale of the 26-turn
grader audit described below — so as published it was directionally supported rather than
established. Stratified, it is solid.

## Why this data is unusually suited to the question

The source project graded 216 replies with a programmatic grader, then a human audited every
one of them and corrected 26. Both label sets survive in the fixture, over identical
untouched replies. That yields something eval work rarely has: **two independent passes over
the same responses, with a documented cause for every disagreement.**

It also means the source project's headline claim — *the wrong-answer rate was 0% in all 24
cells* — is true only of the post-audit labels. The grader as it originally ran recorded 7
wrong and 5 confused verdicts, 6.3% of 192. Same replies, different reader. That gap is the
subject of the judge-validation stage, and `validity/fixture.py` refuses to load a fixture in
which it has closed, because a fixture with one label set has nothing to validate against.

## Limitations

Stated here rather than at the end, because they bound every number above.

- **n = 1 per item per configuration.** Each question was asked once in each cell, so agent
  run-to-run variance is not recoverable from this data at all. Some of what the item analysis
  attributes to configurations is sampling noise, and nothing here can say how much.
- **One human rater.** The 26-correction audit is a single pass by one person, so the
  human–human agreement ceiling is unestimated. A judge that matches this reference standard
  matches *one* reader's judgement; without a second rater there is no way to know how much of
  the residual disagreement is judge error and how much is legitimate ambiguity.
- **12 observations per stratified item.** Sampling error on a correlation at n=12 is roughly
  ±0.5 near zero — wider than most gaps in the item table. It separates "clearly working" from
  "clearly not" and supports no finer ranking than that.
- **Two topics' wrong-answer rate is a lower bound**, inherited from the source project: its
  grader could not reliably detect negation on two policy topics. Finding 1 quantifies this —
  the grader agrees with the human on 54% and 58% of those two topics against ≥96% elsewhere —
  but quantifying it does not repair the published per-topic figures.
- **The two tolerances are stipulated, not elicited.** A real standard-setting study would get
  them from the business owner who carries the consequence; these were chosen to be defensible
  for a customer-facing policy agent and declared before any score was looked at. Every table in
  the cut-score report is also given as a function of them, so a reader who disagrees can find
  their own row — but the pass/fail verdicts are only as good as the numbers they are set against.
- **The stratified analyses halve the sample.** Every interval in them is wider than its
  pooled counterpart. Both are reported; neither is the single right answer.

## Layout

```
fixtures/extract.py     one-shot extraction from the source repo, with provenance
fixtures/turns.json     216 turns, both label sets, pinned to a source commit
validity/fixture.py     loader that refuses to proceed if the data drifted
validity/intervals.py   Wilson, Newcombe, sample sizing
validity/precision.py   analysis 1: what the published run could have detected
validity/discrimination.py  analysis 2: which questions carry the eval
validity/agreement.py   kappa, kappa_max, PABAK, weighted kappa, Krippendorff's alpha, bootstrap
validity/judge.py       analysis 3, the only module that spends money: runs the judges
validity/reliability.py analysis 3's report, offline over runs/*.jsonl
validity/cutscore.py    analysis 4: the standards, the coverage claim, the cost decision
runs/*.jsonl            2,494 recorded verdicts (gitignored; regenerate with `make judge`)
docs/*.md               four generated reports, plus the methodology and executive write-ups
```

Every statistic is implemented in this repository rather than imported, and each is tested
against a worked example from the literature with the expected value hard-coded. The offline
analysis has **no dependencies** — a study whose subject is whether a measurement can be
trusted should not ask the reader to take its own measurements on faith.

## Running it

```sh
make analyse   # all four offline analyses: no network, no credentials, no dependencies
make test      # 131 tests
make docs      # regenerate docs/ from the fixture and runs/
```

The judge stage is the only part that costs anything, and it is not part of `make analyse`:

```sh
make judge JUDGE=haiku-4.5 ARGS="--runs 5"        # dry run: prints calls and estimated spend
make judge JUDGE=haiku-4.5 ARGS="--runs 5 --go"   # sends; resumable, appends to runs/
```

It dry-runs by default and refuses to send without `--go`. The full study as reported — two
judges, five passes each plus a swapped-order pass, 2,494 verdicts — cost **$6.95** on Bedrock
against a $6.73 estimate. `runs/*.jsonl` is gitignored, so the committed report is reproducible
from the transcripts but the transcripts are regenerated rather than vendored.

## Provenance

`fixtures/turns.json` is a vendored extract, not a re-run. The source AWS estate has been torn
down, which is exactly why the fixture exists: the eval output persisted full reply text, all
four axis labels, and the pre-audit grades frozen as the run wrote them, so every analysis
here is offline and reproducible. The fixture records the source commit, the run date
(2026-08-26), the axes and what was held constant. `load()` re-derives the eight published
accuracy figures and raises if any has moved.

## Status

Complete: all four analyses — precision re-analysis, item analysis, judge validation, cut score —
the methodology and executive write-ups, and 131 tests.

Known gap, and the most useful thing to add next: **there is no second human rater**, so the
human–human agreement ceiling is unestimated and the judge–human kappas above cannot be
compared against one. A second independent pass over a stratified subsample of 40–60 turns
would settle it.
