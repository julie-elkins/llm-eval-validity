# Synthetic phase results

## Status

The seven-case synthetic phase completed offline under protocol version
`0.2-synthetic`.

No participants, learner records, live provider calls, or certification
content were used. The private reference disposition is a controlled
ground-truth-like label for the constructed case, not a learner outcome.

## Summary

| Evaluator view | Cases | Agreement with synthetic reference | Disagreement |
|---|---:|---:|---:|
| Final-answer-only | 7 | 1/7 (14.3%) | 6/7 (85.7%) |
| Evidence-aware | 7 | 7/7 (100.0%) | 0/7 (0.0%) |

The final-answer-only view marked six cases as supported or otherwise
acceptable even though the constructed reference did not support an inference
of independent learning. The evidence-aware view rejected those planted
unsupported-learning inferences in all six failure cases.

## Case-class breakdown

| Case class | Final-answer-only | Evidence-aware | Reference implication |
|---|---|---|---|
| Evidence supported | Supported | Supported | Independent-learning inference supported in the constructed case |
| Correct answer, wrong justification | Supported | Not supported | Correctness alone is insufficient |
| Fluent but unsupported | Supported | Not supported | Fluency does not supply missing evidence |
| Stale or contradictory evidence | Unclear | Not supported | Conflicting evidence blocks support |
| Ambiguous; requires uncertainty | Supported | Not supported | Confidence without sufficient evidence is unsafe |
| Missing required boundary | Supported | Not supported | A correct answer can still violate the evidence contract |
| Polished negative control | Supported | Not supported | Presentation quality is not evidence of learning |

## Interpretation

This controlled result supports a narrow design hypothesis: preserving and
evaluating evidence can distinguish planted unsupported inferences that a
final-answer-only view misses.

It does not establish:

- that real learners learned or failed to learn;
- that AI assistance improves learning;
- that the rubric is valid for a student population;
- that a transfer disposition equals a human learner outcome;
- that one AI system or evaluator is better in education; or
- that the result generalizes beyond these seven constructed cases.

The next research phase is human validation only after an appropriate ethics
determination, task freeze, analysis lock, and consent review.
