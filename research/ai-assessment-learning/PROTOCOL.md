# Future human-validation protocol: AI-assisted assessment and independent learning evidence

## Version

Protocol version: `0.1-human-validation-draft`

Status: future-phase draft. No participant recruitment or provider run is
authorized by this document.

The current study is the non-participant synthetic phase described in
[SYNTHETIC_PHASE_PROTOCOL.md](SYNTHETIC_PHASE_PROTOCOL.md).

## Design summary

This is a small, exploratory, within-participant matched study. Each participant
completes a public synthetic task with bounded AI assistance and then completes a
matched transfer task without AI assistance.

The evaluator comparison is paired:

| View | Available evidence |
|---|---|
| Final-answer-only | The submitted answer and task rubric |
| Evidence-aware | The submitted answer, declared evidence fields, bounded workflow metadata, and verification signals |

The transfer result is kept separate from the evaluator view. It is the
criterion used to test whether an assessment inference was supported.

## Participants

The planned pilot population is adults who volunteer to complete a short,
public, low-risk learning task. The pilot must not recruit minors, collect
protected educational records, or use employer, customer, or certification
content.

The sample size is exploratory rather than confirmatory. A final target must be
justified after the task duration, ethics boundary, and analysis unit are
reviewed. No population claim may be made from the pilot.

## Task sequence

### Stage 1: orientation and consent

Participants receive:

- study purpose in plain language;
- AI-use boundary;
- data collected and retained;
- withdrawal process;
- contact and review information;
- statement that participation has no employment, certification, or academic
  consequence.

### Stage 2: baseline task

The participant completes a short public task without AI assistance. This
establishes a baseline and identifies whether the task is understandable.

### Stage 3: bounded AI-assisted task

The participant may use the designated AI assistant under a fixed protocol. The
assistant may provide hints, explanations, or evidence references, but the
protocol must declare what it is allowed to do.

The workflow records metadata only:

- task and form identifiers;
- condition and protocol revision;
- assistance boundary;
- evidence identifiers;
- response-status and completion-status codes;
- confidence or verification fields;
- bounded counts, timings, and refusal states;
- hashes of retained artifacts where needed for integrity.

It must not retain raw participant answers, private prompts, or provider
responses in the public repository.

### Stage 4: evaluator judgments

Evaluators receive anonymized packets. Each case is scored under both views,
with presentation order counterbalanced when feasible.

Evaluators answer:

- Was the submitted answer correct?
- Was the explanation or justification correct and relevant?
- Was the claimed evidence actually available?
- Were claims supported by that evidence?
- Did the participant demonstrate verification or uncertainty handling?
- Does the available evidence support an inference of independent learning?

### Stage 5: independent transfer

The participant completes a matched task without AI assistance. The transfer
task must test the same target skill while changing the surface form, values,
context, or required application.

The transfer task must not be a memory test of the original answer. A participant
who repeats a memorized phrase without applying the skill should not count as
transfer success.

### Stage 6: optional delayed transfer

If ethics review and study capacity permit, a delayed transfer task may be
administered after a declared interval. It is optional and must not be added
after seeing the initial results.

## Primary outcome

The primary outcome is agreement between the assessment inference and independent
transfer performance, reported separately for final-answer-only and
evidence-aware evaluation.

The study must report:

- correct transfer;
- incorrect transfer;
- incomplete or unavailable transfer;
- evaluator refusal or uncertainty;
- denominator policy;
- missing-data counts.

## Secondary outcomes

- final-answer correctness;
- evidence-contract satisfaction;
- unsupported-claim rate;
- reviewer agreement;
- confidence calibration;
- time and bounded interaction counts;
- transfer performance by task family;
- cases where the two evaluator views disagree.

## Controls

The synthetic task set must include:

1. an evidence-complete task where the answer and transfer should be supported;
2. a fluent-but-unsupported task;
3. a correct answer with incorrect or irrelevant justification;
4. a stale or contradictory evidence case;
5. an ambiguous case where uncertainty or clarification is appropriate;
6. a task where the AI assistant's help is useful but does not complete the
   transfer task for the participant;
7. a negative control where a response looks polished but fails the rubric.

Each case needs a private expected disposition and a public reason code. The
public artifact must not expose answer keys or participant responses.

## Analysis plan

The first analysis is descriptive and paired. It must not begin with a single
overall score.

Report, by evaluator view and task family:

- confusion matrix against independent transfer;
- sensitivity and specificity where the labels support them;
- positive and negative predictive value with denominators;
- reviewer agreement and uncertainty;
- evidence-contract satisfaction;
- missingness and refusal rates;
- interval estimates appropriate to the sample size;
- disagreement cases with metadata-only reason codes.

If the sample is too small for stable interval estimates, say so and report the
study as a feasibility pilot.

No model ranking, treatment-effect claim, or learning-improvement claim is
permitted unless it was predeclared and the design supports it.

## Reproducibility

The public repository should contain:

- synthetic task identifiers and task-family descriptions;
- protocol revision;
- rubric dimensions;
- report schema;
- anonymized metadata-only examples;
- analysis code and tests;
- a limitations statement.

It must not contain:

- participant answers;
- private certification content;
- answer keys;
- reviewer identities;
- raw provider traces;
- credentials or access tokens;
- copied proprietary educational material.

## Stop conditions

Stop the pilot if:

- the consent or ethics boundary is unresolved;
- a task exposes private or sensitive content;
- the AI assistant crosses its declared assistance boundary;
- the transfer task is leaked or repeated verbatim;
- the cost, time, or participant burden exceeds the declared ceiling;
- the data cannot be separated from identity or private content;
- a protocol change would alter the primary outcome after execution begins.

## What would justify a larger study

A larger study is justified only if the pilot demonstrates:

1. the task and transfer forms are understandable;
2. the evidence contract can be scored consistently;
3. the evaluator views produce interpretable disagreement;
4. the transfer outcome is observable without leaking the answer; and
5. the uncertainty identifies a decision that a larger sample could resolve.
