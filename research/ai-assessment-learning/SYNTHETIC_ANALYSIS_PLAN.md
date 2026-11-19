# Synthetic phase analysis plan

## Status

Current analysis plan for protocol version `0.3-synthetic`.

## Primary estimand

The primary estimand is the difference between the final-answer-only and
evidence-aware views in detecting planted unsupported-learning inferences.

This is a controlled measurement result, not a learner-outcome estimate.

## Unit of analysis

The unit is one synthetic case under one evaluator view. Paired views share the
same case identifier and synthetic reference disposition. The public fixture
records the two observed view dispositions; the expected reference disposition
remains private. The 30-case matrix contains repeated cases within seven
planted failure classes; repetitions are descriptive robustness checks, not
independent learner observations.

## Primary summaries

For each view, report:

- supported-case agreement;
- unsupported-case detection;
- false-supported count;
- contradiction detection;
- uncertainty or escalation handling;
- not-assessable count;
- denominator and missingness.

Report paired disagreements by public reason code and 95% Wilson intervals for
agreement. Do not report a single overall score without the case-class
breakdown.

## Secondary summaries

- evidence-contract satisfaction;
- answer correctness;
- explanation validity;
- evidence alignment;
- verification behavior;
- evaluator-view disagreement;
- protocol refusals;
- malformed or incomplete case counts.

## Negative controls

The analysis must include planted controls where:

- the answer is correct but the justification is wrong;
- the answer is fluent but evidence is absent;
- a cited source is stale or contradictory;
- a confident conclusion exceeds the supplied evidence;
- a polished response fails the declared evidence contract.

A clean result on ordinary cases does not compensate for failure to catch these
controls.

## Decision rule

The synthetic phase is complete only if:

1. every required case class is present;
2. both evaluator views run against the same case set;
3. the private reference disposition is available for analysis;
4. the report distinguishes unsupported from incorrect;
5. missing or malformed cases cannot appear as passes; and
6. the report states that no learner outcome was observed.

## Interpretation

If the evidence-aware view catches a planted failure that the final-answer-only
view misses, the result supports a design hypothesis: preserving evidence can
improve the *assessment inference* in the constructed case.

It does not support the stronger claim that evidence-aware AI assessment
improves real learning. That claim requires a separate human validation phase.
