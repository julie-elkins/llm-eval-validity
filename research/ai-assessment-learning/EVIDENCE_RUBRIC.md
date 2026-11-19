# Evidence rubric

## Purpose

This rubric separates an answer that is correct from an answer that supports a
valid inference about independent learning.

An evidence contract is a declared set of fields and conditions that must be
present before a result can be treated as usable evidence. It is not a claim
that the evidence proves learning by itself.

## Dimensions

### 1. Task correctness

Does the submitted answer satisfy the task's correctness criteria?

Labels:

- `correct`
- `partially_correct`
- `incorrect`
- `not_assessable`

### 2. Explanation or justification

Does the explanation apply the target concept or procedure rather than merely
repeat the answer?

Labels:

- `valid_application`
- `partial_application`
- `unsupported_or_irrelevant`
- `missing`

### 3. Evidence alignment

Does the cited or declared evidence support the claim being made?

Labels:

- `supported`
- `partially_supported`
- `contradicted`
- `not_available`

### 4. Verification behavior

Did the participant or workflow check the answer against available evidence,
identify uncertainty, or appropriately request clarification?

Labels:

- `verified`
- `uncertainty_handled`
- `unverified`
- `not_observable`

### 5. Independent-learning inference

Does the evidence support the claim that the participant can apply the target
skill without AI assistance?

Labels:

- `supported_by_transfer`
- `not_supported_by_transfer`
- `unclear`
- `not_tested`

This is the key judgment. It must not be inferred from answer fluency or
explanation length alone.

## Evidence-contract decision

The evaluator records one overall decision:

- `usable_evidence`: required fields are present and support the stated claim;
- `insufficient_evidence`: the result may be correct, but the evidence is
  incomplete;
- `contradictory_evidence`: the trace contains evidence against the claim;
- `not_assessable`: the task or transfer result cannot be interpreted.

## Final-answer-only view

The evaluator sees only the submitted answer and the task rubric. This view
represents the common failure mode where a correct-looking answer is treated as
proof of learning.

## Evidence-aware view

The evaluator sees the submitted answer, declared evidence identifiers,
verification signals, bounded workflow metadata, and the independent-transfer
result when the protocol permits it.

The evidence-aware view must not receive private answer keys or raw provider
traces that the final study would not make available to a real evaluator.

## Reviewer calibration

Reviewers must independently score a calibration subset before scoring the
remaining cases. Calibration means comparing judgments against a predeclared
rubric and resolving interpretation differences before the main analysis.

Report:

- eligible reviewer count;
- common cases;
- agreement by dimension;
- disagreements requiring adjudication;
- cases marked `unclear`;
- changes made to rubric wording before the pilot.

No reviewer identity or private answer key belongs in the public report.
