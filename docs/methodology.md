# Methodology: validating an eval the way a certification exam is validated

This document is the technical companion to the four generated reports. It states what was done,
which psychometric method each step borrows, where the borrowing breaks down because the examinee
is a system rather than a person, and which design decisions would move the numbers if made
differently. The reports themselves contain the findings; this contains the reasoning and the
threats.

The one-page version for a decision-maker is [executive-summary.md](executive-summary.md).

## 1. The question, and why it comes before the score

An eval reports a score. A certification programme cannot, because a score that decides whether
someone may practise a profession has to survive a challenge, and "our model got 84%" does not
survive anything. So the field built a standard set of prior questions — is the instrument
measuring the intended construct, precisely enough, with labels a second reader would reproduce,
against a threshold someone will defend? — and a methodology for each. Almost all of it applies
to evaluating an AI system, and almost none of it appears in published eval work.

The four analyses here are those prior questions, in dependency order. Each one can invalidate
the ones after it, which is why the order is not arbitrary:

| # | Question | Certification analogue | Report |
|---|---|---|---|
| 1 | Could this design have detected the effects it reports? | test precision, standard error of measurement | [precision.md](precision.md) |
| 2 | Do the items measure one thing, and which ones carry the test? | item analysis, discrimination indices, reliability | [item-analysis.md](item-analysis.md) |
| 3 | Would a second reader assign the same labels? | inter-rater reliability, reference standard | [judge-validation.md](judge-validation.md) |
| 4 | What score licenses the decision, and how often would it flip? | standard setting, decision consistency | [cut-score.md](cut-score.md) |

## 2. The data, and why it suits the question

216 graded agent turns from a Claude-powered customer-service agent, run across a 24-cell
factorial design — 3 models × 2 prompts × 2 document corpora × 2 retrievers — with 8 policy
questions and 1 behaviour probe per cell. 192 policy turns, 24 behaviour turns.

The property that makes this data unusually suitable is not its size. It is that **two
independent label sets survive over identical, untouched replies**: a programmatic grader's
verdicts as the run wrote them, and a human auditor's verdicts after reading all 216 and
correcting 26. That is a reference standard with a documented cause for every disagreement, which
is exactly what an inter-rater study needs and what eval datasets almost never retain.

It is vendored as a fixture rather than re-run — the source AWS estate has been torn down. The
loader re-derives the eight published accuracy figures from the fixture and refuses to load if
any has moved, and separately refuses to load a fixture in which the pre-audit and post-audit
label sets have converged, because a fixture with one label set has nothing to validate against.

## 3. Method by method

### 3.1 Precision (analysis 1)

Every proportion is reported as a Wilson score interval, and every difference of proportions as a
Newcombe hybrid-score interval. Wilson rather than Wald because every interesting cell here is
small or extreme: on a 0/8 cell Wald returns the degenerate [0, 0], which would let a category
with no evidence at all clear a threshold test.

The analysis then inverts the usual reading. Instead of asking whether an observed difference is
significant, it asks **what the design could have detected** — the minimum detectable effect at
each sample size. That converts a null result from a finding about the system into a finding
about the study: the prompt axis is +3.1 points [-10.6, +16.7], and the design could not have
resolved anything below about 14 points, so a real 10-point prompt effect would have been
reported as "no measurable difference".

### 3.2 Item analysis (analysis 2)

Corrected item-total correlations, mean inter-item correlation, and Cronbach's alpha, computed
over configurations as the unit of analysis — configurations are the "examinees", items are the
eight policy questions.

The methodological content is in what happens next. Run over all 24 configurations the item table
looks excellent (item-total +0.68 to +0.90, alpha 0.94) and it is an artefact: nine
configurations scored 0/8 and all nine are the superseded-corpus arm, so the low-scoring
comparison group consists entirely of configurations that answered nothing. Every item
"discriminates" because every item detects the corpus. **Stratifying to the arm where the corpus
is not the binding constraint** drops mean inter-item correlation from +0.65 to +0.22 and alpha
from 0.94 to 0.76, and reveals that two of the eight items are at ceiling (12/12) and cannot rank
anything. The general lesson: a floor or ceiling arm in the design inflates every reliability
statistic computed over the pool, and the inflation looks like good news.

### 3.3 Inter-rater reliability (analysis 3)

Two judges — Sonnet 5 and Haiku 4.5 — read all 192 policy replies **five times each**, plus a
sixth pass with the two policy statements presented in reversed order, and the 19 scored
behaviour turns five times each — blind throughout to the configuration, the incumbent grade, and
the audit verdict. 2,494 verdicts, 0 errors, $6.95.

Agreement is reported four ways, because no single coefficient is safe here:

- **Cohen's kappa, always printed beside `kappa_max`.** kappa_max is the highest kappa the
  observed marginals permit; kappa/kappa_max is the share of the attainable agreement actually
  attained. Without it, kappa on skewed marginals is uninterpretable.
- **PABAK**, generalised to k categories as `(p_o − 1/k)/(1 − 1/k)`, as the prevalence-independent
  cross-check.
- **Weighted kappa with harm-cost weights**, so that confusing two safe grades is not penalised
  like confusing a safe grade with a harmful one.
- **Krippendorff's alpha** via the coincidence matrix, used for intra-rater stability across the
  five passes, where a rater's own passes are the coders.

Percentile bootstrap (5,000 resamples, seed 20260828) for every interval on a coefficient.

Two results drove the design. First, **the kappa paradox is not a footnote here, it is half the
data.** In the superseded-corpus stratum raw agreement is about 95% and kappa is −0.018 (Sonnet)
and exactly 0.000 (Haiku) — because `kappa_max` there is 0.322 and 0.000 respectively. Haiku
answered `abstained` on all 96 turns, and a rater that uses a single category forces
`p_observed_max = p_expected`, pinning kappa_max at zero however good the rater is. Reported
alone, kappa would describe the study's best-behaved stratum as its worst failure. The same
mechanism makes the harmful/safe collapse — the fold that matters most for a deployment decision
— the one where kappa is least usable, because the human reference never uses a harmful grade.

Second, **five passes changed the headline.** Pass 1 alone has Haiku beating Sonnet by 0.03 of
kappa. Across all five, Sonnet's range is 0.872–0.892 and Haiku's is 0.882–0.935: overlapping,
with Haiku's worst pass inside Sonnet's range. The between-model difference this study can see is
no larger than the within-model, run-to-run difference, so no ranking is supportable. Both beat
the incumbent regex grader (+0.87 and +0.90 against +0.77), which is the comparison that matters.

Finally, the judge is evaluated **as the thing it would actually be deployed as** — a screening
test that decides which turns a human reads. Sensitivity, specificity, PPV, and review load, with
the positive class defined as "the grader disagrees with the reference". Haiku flags 15.6% of
turns and catches all 23 of the grader's policy errors; the honest number is the interval, since
23/23 is consistent with a true sensitivity of 0.86 — as many as one grader error in seven could
be missed by a screen that looked flawless.

### 3.4 Standard setting (analysis 4)

Four borrowings, in order of how much they change the conclusion:

1. **Declare the standard before reading the score.** The two tolerances are literals at the top
   of `validity/cutscore.py` with written rationales. A threshold chosen after seeing the result
   is not a standard, it is a description.
2. **Conjunctive, per-family standards.** Each family clears its own tolerance or fails; a strong
   result in one cannot offset a weak one in the other. Compensatory scoring assumes the total
   measures a single underlying quantity, and these two families measure different failure modes
   with different consequences.
3. **Judge the interval bound, not the point estimate.** A standard applied to point estimates
   passes any sufficiently small eval, because a small eval's point estimate is zero.
4. **Report decision consistency, not measurement precision.** Subkoviak's
   single-administration estimate: treating a cell's eight items as binomial trials, `q` is the
   chance it clears the cut on a fresh administration and `q² + (1−q)²` the chance two
   administrations agree. Averaged over cells, that is the probability the *decision* survives a
   re-run — which is what ships, unlike the score.

Sample sizing uses the binomial rule of three, inverted and solved by search rather than by the
`3/p` approximation: at these sizes the approximation says 150 turns for a 2% tolerance where the
binomial needs 189, a 26% underestimate of the run.

And the part that does not transfer. A modified-Angoff study asks experts what proportion of
*minimally competent candidates* would answer each item correctly. Four objections, two fixable
and two not: there is **no candidate population** (configurations differ by experimental design,
not ability — not fixable, a category difference between people and systems); the **examinee can
be edited in response to failing** (prompt-rewriting against the items it failed is item
exposure, not studying — fixable, with held-out items and rotation); **failure costs are not
exchangeable across items** (fixable, with conjunctive standards); and **the construct drifts**
(the correct answers changed when the policy documents changed — not fixable, so the cut has to
be re-derived on a schedule).

## 4. Design decisions that would move the numbers

Stated because each is a judgement, and a reader who disagrees should be able to find where.

- **Abstentions leave the policy denominator.** An agent that declines and hands off has not made
  an error; it has declined. Folding the two together produces a 59% "failure rate" for a system
  that was never once wrong. The cost of abstaining is accounted for separately, as escalation
  volume, which is where it belongs.
- **Behaviour turns that never reached the restricted action are excluded, not scored as
  compliant.** Scoring them as passes would improve the rate by inventing evidence. It costs 5 of
  24 turns.
- **The pooled contrast divides by all 211 scored turns**, not by the two families' own
  denominators, because that is what a harness's "wrong answer rate" divides by. Using the
  narrower denominator would have made the pooled figure fail too, and destroyed the contrast the
  row exists to show.
- **Judge consensus is the majority of five passes, over turns every pass answered.** Computing a
  majority from whichever passes succeeded would let the per-pass and consensus columns describe
  different turn sets, and a judge whose failures cluster on hard turns would look better in
  consensus than in any single run.
- **The swapped-order arm is never pooled into the headline.** It shares turn indices with the
  main arm; averaging it in would hide the order effect it exists to measure.
- **The stratification axis is the document corpus**, chosen because it is the axis that produces
  the floor arm. Both pooled and stratified figures are reported throughout; neither is the single
  right answer, and the stratified ones halve the sample.

## 5. Threats to validity

- **One human rater.** The 26-correction audit is one person's single pass, so there is no
  human–human agreement ceiling. A judge–human kappa of 0.91 could mean the judge nearly matches
  a human, or that it nearly matches *this* human. This is the most useful missing number in the
  study; a second independent pass over a stratified subsample of 40–60 turns would settle it.
- **n = 1 per item per configuration.** Agent run-to-run variance is not recoverable from this
  data at all, so some of what the item analysis attributes to configurations is sampling noise
  and nothing here can say how much.
- **Determinism cannot be pinned.** The SDK's 1.x line accepts no sampling parameters — no
  temperature, no seed. Repeated passes are therefore the only instrument available for judge
  variance, and the observed run-to-run spread is a floor on the variance of any single-run judge
  result.
- **The judges are not fully blind.** 51 of the 192 replies cite a source filename, all from the
  current-corpus arm, and the filenames are self-labelling (`-updated`, `-NEW`, `-v2-FINAL`). Not
  removable — the reply is the evidence, and the human auditor read the same text with the same
  cue — but part of the agreement is explained by a cue rather than by comprehension.
- **The reference standard is not independent of the judges' input.** Both readers were shown the
  current and superseded policy statements, so neither derived the answer key and an error in the
  key would be invisible to both.
- **The tolerances are stipulated, not elicited.** A real standard-setting study gets them from
  the business owner who carries the consequence. Every table is also given as a function of them.
- **Two topics' wrong-answer rate is a lower bound**, inherited from the source project's grader,
  which could not reliably detect negation on two policy topics. Analysis 3 quantifies the gap;
  quantifying it does not repair the published per-topic figures.

## 6. What transfers to any eval programme

The checklist, independent of this data and of this vertical:

1. Compute the minimum detectable effect **before** the run. It is the cheapest eval-design work
   available, and a null result without it is uninterpretable.
2. Compute the tolerance your sample size can demonstrate, and check it against the tolerance the
   business needs. 100% on 79 turns and 100% on 800 turns look identical in a report and license
   very different decisions.
3. Stratify every reliability statistic by any axis that produces a floor or ceiling arm, and
   report both. Pooled item statistics are inflated by design arms, not by item quality.
4. Keep the pre-correction labels. An eval whose grader was audited but whose original verdicts
   were overwritten has destroyed its own reference standard.
5. Never quote kappa without `kappa_max`, and never on a collapsed binary where one rater uses a
   single category.
6. Run the judge more than once. A single pass cannot distinguish a better model from a luckier
   run, and with no temperature or seed available, repetition is the only instrument.
7. Evaluate a judge as the thing it will be deployed as. If it screens for human review, report
   sensitivity and review load, not agreement.
8. Declare tolerances per failure mode, before scoring, and judge them on the interval bound.
9. Report how often the decision would flip on a re-run, not how precise the score is.
10. Separate "failed" from "not demonstrated". They call for opposite responses — a fix to the
    system versus a larger eval — and a single pass/fail flag erases the difference.

## 7. Reproducing it

```sh
make analyse   # all four offline analyses: no network, no credentials, no dependencies
make test      # 135 tests
make docs      # regenerate the four reports from the fixture and runs/
```

Every statistic is implemented in this repository rather than imported, and each is tested against
a worked example from the literature with the expected value hard-coded. The offline analysis has
no dependencies: a study whose subject is whether a measurement can be trusted should not ask the
reader to take its own measurements on faith.

The judge stage is the only part that costs money and the only part not in `make analyse`. It
dry-runs by default, prints its planned call count and estimated spend, refuses to send without
`--go`, and is resumable so an interrupted run does not re-bill. `runs/*.jsonl` is gitignored: the
committed reports are reproducible from transcripts, and the transcripts are regenerated rather
than vendored.
