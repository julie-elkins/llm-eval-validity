# Synthetic task specification

## Purpose

The task set must test whether an assessment can distinguish an answer produced
with AI assistance from evidence that the learner can apply the target skill
independently.

Synthetic means the task is authored for this study, safe to publish, and not
copied from private certification or production material.

## Task-family requirements

The first task set should contain at least three families so the result is not
an artefact of one content form:

1. **Concept application** — apply a stated principle to a new situation.
2. **Evidence interpretation** — choose or justify a conclusion from bounded
   evidence.
3. **Procedure or troubleshooting** — select the next valid step under declared
   constraints.

The final families may change after a feasibility review, but the change must be
recorded before participant execution.

## Required task fields

Each task definition must include:

- `task_id`;
- `task_family`;
- `target_skill`;
- `learning_objective`;
- `allowed_evidence`;
- `assistance_boundary`;
- `baseline_form`;
- `assisted_form`;
- `transfer_form`;
- `rubric_dimensions`;
- `expected_failure_modes`;
- `public_reason_code`;
- `private_expected_disposition`.

The public task description must not include the answer key.

## Matched-form rules

The baseline, assisted, and transfer forms must:

- test the same target skill;
- use different surface wording;
- avoid repeating answer phrases;
- preserve comparable difficulty;
- use the same evidence policy;
- avoid requiring private or specialized knowledge;
- be reviewed for ambiguity before use.

The transfer form is invalid if a participant can succeed by copying the original
answer without applying the skill.

## Negative controls

At least one case in each pilot must look strong on the surface while failing a
declared requirement. Examples include:

- a correct answer paired with an irrelevant explanation;
- a citation that does not support the claim;
- a confident conclusion when the evidence is incomplete;
- a polished response that skips the required transfer step;
- an answer that uses a stale evidence identifier.

Negative controls are required because a green-looking response that cannot be
trusted is the central failure mode under study.

## Task review gate

Before participant use, two reviewers should independently inspect each task for:

- target-skill alignment;
- unambiguous wording;
- answerability from the allowed evidence;
- transfer-form independence;
- fairness and accessibility;
- unintended clues;
- safe public release.

Their disagreement should be resolved before the task is frozen, not after the
results are seen.
