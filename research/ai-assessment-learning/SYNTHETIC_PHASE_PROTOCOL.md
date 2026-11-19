# Synthetic phase protocol

## Version and status

Protocol version: `0.2-synthetic`

This is the current executable phase. It is a non-participant study: no
volunteers, learner records, participant answers, or human-subjects data are
collected.

## Research purpose

Test whether an evidence-aware assessment rubric can detect planted cases where
a correct-looking AI-assisted response does not provide sufficient evidence for
independent learning.

This phase tests the measurement design. It does not measure whether real people
learn.

## Synthetic unit

The unit is a synthetic assessment trace with:

- an assessment task;
- an AI-assisted response;
- declared evidence fields;
- an evaluator view;
- a matched transfer disposition;
- a private expected disposition;
- a public failure reason code.

The matched transfer disposition is a controlled reference label, not a learner
outcome. It represents what the protocol says the transfer result would be in
the constructed case.

## Conditions

### Final-answer-only view

The evaluator sees the task, rubric, and submitted answer. It does not see the
declared evidence fields or workflow metadata.

### Evidence-aware view

The evaluator sees the same task and answer plus the declared evidence fields,
verification signals, and bounded workflow metadata.

Both views receive the same case and task rubric. The only difference is the
evidence available to the evaluator.

## Required case classes

The synthetic phase must include:

1. correct answer with supported evidence;
2. correct answer with unsupported justification;
3. fluent answer with incomplete evidence;
4. stale or contradictory evidence;
5. uncertainty that should trigger escalation;
6. evidence-aware view that can detect a missing boundary;
7. polished negative control.

The public manifest records identifiers and reason codes. The expected
dispositions remain in a private answer key until the study artifact is
released.

## Synthetic execution sequence

1. Validate the public task manifest.
2. Load the private expected-disposition key.
3. Generate or load metadata-only traces for each case and view.
4. Apply the evidence rubric.
5. Compare the evaluator disposition with the private synthetic reference.
6. Report paired disagreements, missing evidence, and failure reasons.
7. Freeze the output and record the protocol revision.

No live provider call is required. A future provider-backed arm must have its
own credential, cost, and privacy boundary and must not alter the synthetic
baseline.

## Primary outcome

The primary outcome is detection of the synthetic evidence failure:

> Does the evidence-aware view reject planted cases where final-answer-only
> evaluation would incorrectly support an inference of independent learning?

Report:

- true supported cases;
- false-supported cases;
- unsupported-but-correct cases;
- contradictory-evidence cases;
- uncertainty and escalation cases;
- missing or not-assessable cases.

## What the synthetic phase may support

- A demonstration that the rubric can distinguish answer correctness from
  evidence sufficiency in controlled cases.
- A taxonomy of failure modes.
- A reproducible protocol for a later human validation study.
- A feasibility result showing whether the two evaluator views produce different
  decisions on planted controls.

## What it may not support

- That real learners learned or failed to learn.
- That AI assistance improves learning.
- That the rubric is valid for a population of students.
- That the synthetic reference labels equal human learner outcomes.
- A claim that one AI system or architecture is better for education.

## Future human-validation phase

A separate future phase may use adult volunteers after an appropriate ethics
determination. That phase is documented in [PROTOCOL.md](PROTOCOL.md) and
[PARTICIPANT_INFORMATION_AND_CONSENT_DRAFT.md](PARTICIPANT_INFORMATION_AND_CONSENT_DRAFT.md).
