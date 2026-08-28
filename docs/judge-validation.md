# Judge validation: is the grader's label the right label?

192 policy turns, each graded four ways by a regex-based harness, read once by a human auditor, and read 5 times each by two LLM judges -- sonnet-5, haiku-4.5 -- plus a further pass per judge with the two policy statements swapped. 2494 verdicts in total.

The judges saw the customer's question, the current policy statement, the superseded one, and the reply. They did not see the configuration, the incumbent grade, or the audit verdict. `tests/test_judge.py` asserts that over all 216 turns, because a judge that can see the existing label produces a high kappa that measures leakage and nothing downstream reveals it.

## Agreement with the human reference

Majority of five passes, against the post-audit human labels.

| rater | n | raw agreement | kappa | 95% CI | kappa_max | attained | PABAK | weighted |
|---|---|---|---|---|---|---|---|---|
| sonnet-5 | 192 | 0.938 | +0.872 | [+0.80, +0.94] | 0.893 | 0.98 | 0.917 | +0.834 |
| haiku-4.5 | 192 | 0.953 | +0.904 | [+0.84, +0.96] | 0.914 | 0.99 | 0.938 | +0.880 |
| regex grader | 192 | 0.880 | +0.772 | [+0.69, +0.85] | 0.841 | 0.92 | 0.840 | +0.721 |

Both judges agree with the human auditor more closely than the incumbent grader does (kappa +0.772). That is the result the study was run to get: the labels the eval reported are not the labels a careful reader would assign, and an LLM judge recovers more of the difference than the regex did.

## Why one run is not enough to rank two judges

| judge | kappa per pass | range | intra-judge alpha | turns that ever flipped |
|---|---|---|---|---|
| sonnet-5 | 0.882, 0.892, 0.872, 0.883, 0.872 | 0.872–0.892 | 0.983 | 3/192 |
| haiku-4.5 | 0.914, 0.882, 0.904, 0.935, 0.904 | 0.882–0.935 | 0.956 | 7/192 |

Read pass 1 alone and haiku-4.5 beats sonnet-5. Read all 5 and the intervals overlap: haiku-4.5's worst pass (0.872) sits inside sonnet-5's range. **The between-model difference is no larger than the within-model, run-to-run difference**, so this study cannot rank the two judges, and a study that had run each judge once would have ranked them anyway.

There is no temperature control to fall back on: the Python SDK's `messages.create` does not accept sampling parameters at all in the 1.x line -- `temperature` is a `TypeError`, not a rejected request -- and there is no seed. Repeated passes are the only way to see this variance, which is the practical reason to budget for them.

The instability is not spread evenly. It concentrates on `restocking_fee` (4), `price_match` (3), `electronics_returns` (2) -- the same items the order-sensitivity check below picks out, which suggests genuinely borderline replies rather than random noise.

## Order sensitivity

| judge | turns relabelled when the statements were swapped |
|---|---|
| sonnet-5 | 4/192 (2.1%) |
| haiku-4.5 | 3/192 (1.6%) |

Small, and smaller than the run-to-run variance -- so presenting the current policy first is not doing the judges' work for them. Worth measuring anyway: the arm costs one extra pass, and a judge that flipped 20% of its labels on a permutation of its own prompt would invalidate everything above it.

## The stratum where kappa cannot work

| stratum | rater | n | raw agreement | kappa | kappa_max | PABAK |
|---|---|---|---|---|---|---|
| `corpus=v1` | sonnet-5 | 96 | 0.938 | -0.018 | 0.322 | 0.917 |
| `corpus=v1` | haiku-4.5 | 96 | 0.948 | +0.000 | 0.000 | 0.931 |
| `corpus=v1` | regex grader | 96 | 0.833 | +0.340 | 0.340 | 0.778 |
| `corpus=v2` | sonnet-5 | 96 | 0.938 | +0.842 | 0.842 | 0.917 |
| `corpus=v2` | haiku-4.5 | 96 | 0.958 | +0.890 | 0.917 | 0.944 |
| `corpus=v2` | regex grader | 96 | 0.927 | +0.811 | 0.892 | 0.903 |

Read the `corpus=v1` rows again. Both judges agree with the human on about 94.8% of these turns and both score a kappa of zero or below. For haiku-4.5 the ceiling itself is **0.00**: it answered `abstained` on all 96 turns, and a rater that uses one category forces `p_observed_max = p_expected`, which pins kappa at 0.00 however good that rater is. On this half of the data every retrieved document is superseded, the human reference gives the same label to 94.8% of turns, and answering it throughout is very nearly the correct behaviour.

This is Feinstein and Cicchetti's paradox in its pure form, and it is the practical warning the whole module exists to deliver: **a judge evaluated on a task whose answer is usually the same answer will score a kappa near zero while being right almost every time.** Report kappa alone and the study's best-behaved stratum reads as its worst failure. Report `kappa_max` beside it and the number explains itself. `tests/test_agreement.py` pins both of Feinstein's published tables for the same reason.

In the `corpus=v2` stratum, where the reference standard actually varies, kappa becomes informative again and the ordering from the headline table returns.

## The deployment question: the judge as a screen, not a grader

Nobody deploys a judge to relabel an eval. They deploy it to decide which turns a human should read. So the positive class here is *the grader's label disagrees with the human reference*, and the test is *the judge disagrees with the grader*. 26 of the 216 turns were corrected by the audit.

| judge | prevalence | sensitivity | specificity | precision | review load |
|---|---|---|---|---|---|
| sonnet-5 | 0.120 | 0.957 [0.79, 0.99] | 0.935 [0.89, 0.96] | 0.667 [0.50, 0.80] | 17.2% |
| haiku-4.5 | 0.120 | 1.000 [0.86, 1.00] | 0.959 [0.92, 0.98] | 0.767 [0.59, 0.88] | 15.6% |

That is the number for a deployment memo. haiku-4.5 flags 15.6% of turns for human review and catches 23 of the grader's 23 actual errors. But read the interval, not the point estimate: 23 positives is a small denominator, so a perfect 23/23 is still only consistent with a true sensitivity as low as **0.86** -- as many as one grader error in 7 could be missed by a screen that looked flawless on this sample. Reporting the point estimate alone would be the single most misleading thing this study could do.

Precision is the number that decides whether anyone keeps using it. At a prevalence of 0.12, 95.9% specificity still means roughly one in 4 flagged turns is a false alarm, and a reviewer experiences that as noise no matter how good the sensitivity is.

## Where each rater fails

| question | n | sonnet-5 | haiku-4.5 | regex grader | |
|---|---|---|---|---|---|
| `electronics_returns` | 24 | 0.917 | 0.958 | 1.000 |  |
| `expedited_shipping` | 24 | 1.000 | 0.958 | 0.958 |  |
| `price_match` | 24 | 0.958 | 0.917 | 0.542 | negation-sensitive |
| `restocking_fee` | 24 | 0.750 | 0.917 | 0.958 |  |
| `return_shipping` | 24 | 0.917 | 0.917 | 1.000 |  |
| `returns_window` | 24 | 1.000 | 1.000 | 1.000 |  |
| `warranty_proof` | 24 | 0.958 | 0.958 | 0.583 | negation-sensitive |
| `warranty_term` | 24 | 1.000 | 1.000 | 1.000 |  |

The grader's two worst questions are exactly the two negation-sensitive ones (`price_match` at 0.54, `warranty_proof` at 0.58), where the correct policy is that the company does *not* do something. Pattern-matching for the policy's keywords cannot tell "we do not price match" from "we will price match". Both judges are near-ceiling on both. This is the clearest statement of what the judge buys: not a uniform lift, but the repair of a specific, predictable class of grader failure.

It runs the other way too. The judges' weakest questions are ones the grader handles cleanly, so the two disagree about different turns -- which is an argument for keeping the grader and screening it, rather than replacing it with a judge.

## The four-way scheme was a two-way scheme

| rater | grades actually used |
|---|---|
| sonnet-5 | `abstained`, `confused`, `correct` |
| haiku-4.5 | `abstained`, `confused`, `correct`, `wrong` |
| human audit | `abstained`, `correct` |
| regex grader | `abstained`, `confused`, `correct`, `wrong` |

The human reference standard uses 2 of the four grades (`abstained`, `correct`) and never once uses `wrong`, `confused`. Once a careful reader had looked at all 192 replies, the harmful categories were empty: the system either answered correctly or declined. So the four-way rubric collapsed to a two-way one in practice, the judges mostly followed, and the `wrong` row of every confusion matrix above is structural rather than incidental.

Worth being precise about what that does and does not mean. It is a finding about this system on this corpus, not about the rubric: a distinction the examinee never triggers is untested, not unnecessary. But it does mean the four-way kappas above are carrying less information than four categories suggest, and it is the direct cause of the `kappa_max` ceilings in the stratified table.

## Confusion matrices

### sonnet-5

```
               correct      wrong   confused  abstained      total   <- sonnet-5
correct             68          0          4          7         79
wrong                0          0          0          0          0
confused             0          0          0          0          0
abstained            1          0          0        112        113
total               69          0          4        119        192
^-- human audit
```

Collapsed to the harmful/safe decision a rollout turns on: raw agreement 0.979, up from 0.938, because collapsing turns every within-class confusion into agreement. Kappa goes the other way, to +0.000 against a ceiling of 0.00 -- the human reference labelled nothing harmful, so after the fold it is a single-category rater and the paradox from the stratified table applies with full force. **The collapse that matters most for a deployment decision is the one where kappa is least usable**, which is worth stating plainly because a binary kappa is the statistic a reader is most likely to ask for here.

### haiku-4.5

```
               correct      wrong   confused  abstained      total   <- haiku-4.5
correct             71          1          1          6         79
wrong                0          0          0          0          0
confused             0          0          0          0          0
abstained            0          0          1        112        113
total               71          1          2        118        192
^-- human audit
```

Collapsed to the harmful/safe decision a rollout turns on: raw agreement 0.984, up from 0.953, because collapsing turns every within-class confusion into agreement. Kappa goes the other way, to +0.000 against a ceiling of 0.00 -- the human reference labelled nothing harmful, so after the fold it is a single-category rater and the paradox from the stratified table applies with full force. **The collapse that matters most for a deployment decision is the one where kappa is least usable**, which is worth stating plainly because a binary kappa is the statistic a reader is most likely to ask for here.

### regex grader

```
               correct      wrong   confused  abstained      total   <- regex grader
correct             74          0          3          2         79
wrong                0          0          0          0          0
confused             0          0          0          0          0
abstained            9          7          2         95        113
total               83          7          5         97        192
^-- human audit
```

The grader's errors have a shape. 9 turns where the human read an abstention were scored `correct`, and 7 were scored `wrong` -- so the regex was finding policy language in replies that declined to state a policy. Both judges make almost none of that error, and the per-question table above says where: replies about the two negation-sensitive policies.

## The behaviour family, separately and with a much smaller n

| rater | n | raw agreement | kappa | 95% CI | kappa_max | attained | PABAK | weighted |
|---|---|---|---|---|---|---|---|---|
| sonnet-5 | 19 | 0.842 | +0.578 | -- | 0.578 | 1.00 | 0.684 | +0.578 |
| haiku-4.5 | 19 | 0.737 | +0.410 | -- | 0.410 | 1.00 | 0.474 | +0.410 |

19 turns, which is too few to support a coefficient and is reported so the omission is visible rather than silent. Five of the 24 behaviour turns never reached the tool the case is about, so the reference standard records nothing for them and they are excluded rather than counted as disagreements.

Both judges err in the same direction -- they call behaviour a violation where the human did not, concentrated on `unanswerable_invents_a_policy`, `no_selector_asks_for_unaskable_field`. An over-flagging judge is the safer failure for a screen and the wrong one for a grader, which is another reason the screening framing above is the one to deploy on.

## What this does not establish

**There is one human reader.** The 26 corrections are one auditor's pass over all 216 turns, so there is no human-human ceiling here and the judge-human agreement above cannot be compared against one. That ceiling is the single most useful missing number: without it, a kappa of 0.91 could mean the judge nearly matches a human or that it nearly matches *this* human. A second independent rater on a stratified subsample of 40-60 turns would settle it and is the first thing to add.

**The judges are not fully blind.** 51 of the 192 replies cite a source filename, all of them from the current-corpus arm, and the filenames are self-labelling (`-updated`, `-NEW`, `-v2-FINAL`). On those turns a judge could shortcut the task without reading the policy. Not removable -- the reply is the evidence, and the human auditor read the same text with the same cue -- but it means part of the agreement above is explained by a cue rather than by comprehension. The `corpus=v1` stratum, where no reply cites anything, is where the shortcut buys nothing.

**The reference standard is not independent of the judges' input.** Both were shown the current and superseded policy statements. Handing the judge only the correct statement would have made its task strictly harder than the human's and turned a validity comparison into a handicap match, so this is the right call -- but it does mean neither reader derived the answer key, and an error in the key would be invisible to both.

**Determinism cannot be pinned.** No temperature, no seed, no way to make a pass repeatable. The run-to-run spread above is therefore a floor on the variance of any single-run judge result, including every single-run judge result in this repo's sources.

**Nothing here is a pass rate.** The question this answers is whether the harness's labels can be trusted, and the answer is that they can be trusted more after screening than before. The share of volume that could be safely automated is a cut-score question, which needs the harmful-error cost weights, and is the next analysis.

