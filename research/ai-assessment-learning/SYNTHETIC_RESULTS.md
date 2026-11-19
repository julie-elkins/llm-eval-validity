# Synthetic phase results

## Status

The 30-case synthetic phase completed offline under protocol version
`0.3-synthetic`.

No participants, learner records, live provider calls, or certification
content were used. The private reference disposition is a controlled
ground-truth-like label for each constructed case, not a learner outcome.

The 30 cases repeat seven planted failure classes. Repetition is a controlled
robustness check; it is not a sample of 30 learners and does not justify a
population claim.

## Overall summary

| Evaluator view | Cases | Agreement with synthetic reference | 95% Wilson interval |
|---|---:|---:|---:|
| Final-answer-only | 30 | 5/30 (16.7%) | [7.3%, 33.6%] |
| Evidence-aware | 30 | 30/30 (100.0%) | [88.6%, 100.0%] |

The final-answer-only view marked 26 cases as supported and four as unclear.
The evidence-aware view marked five cases as supported and 25 as not
supported. The evidence-aware view rejected all 25 planted cases where the
constructed reference did not support an independent-learning inference.

Wilson intervals are bounded descriptive uncertainty ranges for these
constructed proportions. They do not estimate learner performance or a
population effect.

## Case-class breakdown

| Case class | Cases | Final-answer-only agreement | Evidence-aware agreement |
|---|---:|---:|---:|
| Evidence supported | 5 | 5/5 | 5/5 |
| Correct answer, wrong justification | 5 | 0/5 | 5/5 |
| Fluent but unsupported | 4 | 0/4 | 4/4 |
| Stale or contradictory evidence | 4 | 0/4 | 4/4 |
| Ambiguous; requires uncertainty | 4 | 0/4 | 4/4 |
| Missing required boundary | 4 | 0/4 | 4/4 |
| Polished negative control | 4 | 0/4 | 4/4 |

## Interpretation

This controlled result supports a narrow design hypothesis: preserving and
evaluating evidence can distinguish planted unsupported inferences that a
final-answer-only view misses.

It does not establish:

- that real learners learned or failed to learn;
- that AI assistance improves learning;
- that synthetic transfer dispositions equal human learner outcomes;
- that the rubric is valid for a student population;
- that one AI system or evaluator is better in education; or
- that the result generalizes beyond these constructed cases.

The next scientific phase is human validation only after an appropriate ethics
determination, task freeze, analysis lock, and consent review.
