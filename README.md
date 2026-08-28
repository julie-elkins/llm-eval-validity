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

## What it found

Three findings, in descending order of how much they change the original conclusions.

**1. The eval's own item analysis is confounded, and the confound flatters it.**
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

**2. "No measurable difference" was a statement about the design, not about prompts.**
The original run found 42.7% vs 39.6% on the prompt axis and reported no difference. With a
Newcombe interval that is +3.1 points [-10.6, +16.7]: the design could not have detected
anything smaller than about 14 points, so a real 10-point prompt effect would have been
missed. The null survives stratification (-4.2 points [-20.7, +12.6] within the current
corpus), so it is not a floor artefact — but it remains uninformative rather than negative.

**3. Two findings the original run understated, and one it overstated.**
Because every marginal pools the floor arm, the published figures *understate* the effects
that are real: the retriever contrast is +15.6 points [+1.7, +28.7] pooled but +29.2 points
[+12.5, +44.2] within the current corpus, and the model contrast +25.0 rather than +37.5. The
pooled retriever bound clears zero by only 1.7 points — inside the scale of the 26-turn
grader audit described below — so as published it was directionally supported rather than
established. Stratified, it is solid.

The judge-validation and cut-score stages are not yet written; see [Status](#status).

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
  grader could not reliably detect negation on two policy topics.
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
```

Every statistic is implemented in this repository rather than imported, and each is tested
against a worked example from the literature with the expected value hard-coded. The offline
analysis has **no dependencies** — a study whose subject is whether a measurement can be
trusted should not ask the reader to take its own measurements on faith.

## Running it

```sh
make analyse   # both analyses, no network, no credentials, no dependencies
make test      # 44 tests
make docs      # regenerate docs/ from the fixture
```

## Provenance

`fixtures/turns.json` is a vendored extract, not a re-run. The source AWS estate has been torn
down, which is exactly why the fixture exists: the eval output persisted full reply text, all
four axis labels, and the pre-audit grades frozen as the run wrote them, so every analysis
here is offline and reproducible. The fixture records the source commit, the run date
(2026-08-26), the axes and what was held constant. `load()` re-derives the eight published
accuracy figures and raises if any has moved.

## Status

Complete: precision re-analysis, item analysis, 44 tests.

Not yet written: LLM-judge validation against the human-adjudicated standard (sensitivity and
specificity with intervals, confusion matrix, Krippendorff's alpha and PABAK given the skewed
marginals, judge test–retest and prompt-order sensitivity); cut-score analysis with
conjunctive per-family thresholds; the technical and executive write-ups. The judge stage is
the only part that needs network access or a key.
