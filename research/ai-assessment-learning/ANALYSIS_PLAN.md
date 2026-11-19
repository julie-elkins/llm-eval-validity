# Analysis plan

## Status

Future human-validation phase. The current analysis plan is
[SYNTHETIC_ANALYSIS_PLAN.md](SYNTHETIC_ANALYSIS_PLAN.md).

This plan must be locked before any participant data is collected.

## Unit of analysis

The primary unit is a participant-task attempt. A participant may contribute
multiple attempts, so the analysis must preserve the participant identifier
privately and must not treat every attempt as independent without checking the
dependence structure.

## Primary estimand

The primary estimand is the agreement between each evaluator view and the
independent-transfer outcome:

- final-answer-only view;
- evidence-aware view.

The study asks which view makes a more defensible inference about independent
transfer. It does not ask which view produces the most favorable score.

## Primary classification

For each participant-task attempt:

- `transfer_success`: the participant applies the target skill on the matched
  no-AI transfer task;
- `transfer_not_demonstrated`: the participant does not apply the skill,
  provides an incomplete response, or the task cannot be scored;
- `inference_supported`: the evaluator's evidence view supports the claim that
  independent transfer was demonstrated;
- `inference_not_supported`: the evaluator says the available evidence is
  insufficient or contradictory.

The exact label rules must be frozen with the private answer key before
execution.

## Primary summaries

Report separately for each evaluator view:

1. agreement with transfer outcome;
2. false-supported rate, where the evaluator supports learning but transfer is
   not demonstrated;
3. false-not-supported rate, where transfer is demonstrated but the evaluator
   does not support the inference;
4. missing or unscorable cases;
5. uncertainty intervals appropriate to the pilot size.

Do not collapse these into a single leaderboard score.

## Secondary summaries

- final-answer correctness;
- evidence-contract satisfaction;
- unsupported-claim rate;
- reviewer agreement by rubric dimension;
- confidence calibration;
- time and bounded interaction counts;
- differences by task family;
- cases where answer-only and evidence-aware views disagree.

## Paired comparison

Each view must receive the same case, task rubric, and declared evidence
boundary. Only the view's evidence access changes.

The comparison must be paired within participant-task attempt. The analysis must
not compare two different participant groups as if they had received the same
task.

## Missing data

The report must distinguish:

- `not_started`;
- `incomplete`;
- `not_scored`;
- `transfer_not_demonstrated`;
- `transfer_success`.

Missing data must not silently become a correct or incorrect result. The report
must publish the denominator used for every percentage.

## Reviewer calibration

Reviewers score a calibration subset independently before the main packet.
Calibration disagreement is recorded and resolved by rubric clarification before
the main scoring pass.

Report:

- eligible reviewer count;
- common-case count;
- agreement by dimension;
- unresolved disagreement count;
- cases marked `unclear`;
- rubric changes made before the main pass.

## Pilot interpretation

The pilot is feasibility evidence if the sample is too small to estimate the
primary comparison precisely. In that case, the paper must report:

- whether the protocol was usable;
- whether the transfer task was observable;
- where evaluator views disagreed;
- which uncertainty a larger study would resolve.

The pilot must not claim that the workflow improves learning.

## Analysis freeze

Before data collection, freeze:

- primary outcome;
- label definitions;
- task-family strata;
- missing-data rules;
- reviewer calibration procedure;
- interval method;
- stopping rule;
- exclusion criteria.

Any later change creates a new protocol version and must not overwrite the
original analysis.
