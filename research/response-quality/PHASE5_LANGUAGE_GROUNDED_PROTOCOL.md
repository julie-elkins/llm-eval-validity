# Phase 5: language-grounded response-quality protocol

## Status

**Protocol drafted; experiment not run.**

This is a new, separately labelled phase. It does not alter the six frozen
provider conditions already reported in this repository.

## Purpose

The phase connects the existing evidence-contract study to an actual language
task. A language-grounded task requires the agent to produce a natural-language
answer that is supported by declared evidence and appropriate to the task
outcome.

The phase is intended to test ARR scope and strengthen the response-quality
paper. It is not a production evaluation or a provider benchmark.

## Research question

When the same language task, tools, model, budget, and stopping rules are used,
does provider-enforced structured output improve usable evidence and language
response quality compared with prompt instructions plus local validation?

## Planned task families

The task set should contain synthetic but natural-language cases across:

1. evidence-grounded question answering;
2. stale or conflicting source handling;
3. appropriate refusal or abstention;
4. tool-mediated customer-support or documentation actions; and
5. evidence-complete final responses after a bounded tool loop.

Each case must declare:

- a task identifier;
- the user-facing question or request;
- approved evidence identifiers;
- the required evidence contract;
- the expected task outcome;
- applicable refusal or escalation conditions;
- the allowed tools and permissions;
- the required final-response properties; and
- the reason the case is held out or included in development.

Raw prompts, responses, and private review packets remain local. Public
artifacts contain only identifiers, counts, hashes, statuses, and aggregate
results.

## Planned design

### Pilot matrix

The pilot should use 30 unique language tasks, with three replicates for each
of ten task families or scenarios. At least one-third of the tasks should be
held out before any prompt, schema, or rubric interpretation is changed.

The pilot is descriptive. It is not large enough to support a population-level
claim by itself.

### Conditions

The new phase will compare two conditions:

| condition | description |
|---|---|
| Prompt plus local validation | Prompt instructions produce the response; the local validator checks structure, evidence, and task requirements. |
| Provider structured output plus local validation | The same prompt, task, tools, budget, stopping rules, and local validator, with a provider-enforced output schema added. |

The model and provider must be fixed before the run. The model identifier,
schema revision, prompt revision, tool definitions, evaluator revision, and
spend ceiling must be recorded before execution.

### Matched controls

Both conditions must use the same:

- task and replicate matrix;
- model identifier;
- prompt except for the declared output-format intervention;
- tools, permissions, and source identifiers;
- maximum turns and retry policy;
- token, time, and spend ceilings;
- evaluator and reference rubric;
- output retention and privacy boundary; and
- stop and escalation rules.

No response-based reruns, prompt changes, schema changes, or case deletions are
allowed after inspecting a result.

## Reference review

At least 20 held-out cases should receive independent human review when the
private review round is available. Reviewers should assess:

- task correctness;
- evidence support or grounding;
- required evidence completeness;
- appropriate refusal or escalation;
- final-response completeness; and
- confidence, with `unclear` allowed.

Human agreement means how similarly two reviewers judge the same case. It must
be reported separately from agreement between the local validator and a
reviewer. A single reviewer can support a calibration pilot but cannot support
a strong claim that the rubric is independently validated.

The existing version-2 review analysis and adjudication plan governs packet
versioning, intake, disagreement handling, and public reporting.

## Outcomes

Report each outcome separately:

- protocol acceptance rate;
- provider refusal rate;
- task correctness;
- evidence-grounding rate;
- evidence-contract satisfaction;
- appropriate refusal or escalation rate;
- repeated-run reliability;
- Pass@1, meaning success on one attempt;
- Pass@3, meaning success on at least one of three attempts;
- Pass^3, meaning success on all three attempts;
- flip rate, meaning the share of tasks whose outcome changes across attempts;
- latency;
- cost or bounded usage units; and
- incomplete, unavailable, or not-evaluated cases.

Do not collapse these into one universal quality score. A higher answer score
does not compensate for an unauthorized action, missing evidence, or an
unreported refusal.

## Analysis plan

The primary comparison is the difference in usable end-to-end evidence between
the two conditions on the held-out language tasks.

The analysis must also report:

- task-level outcomes rather than only aggregate rates;
- failure attribution across task, model, tool, evidence, evaluator, and
  harness layers;
- accepted-trace and all-attempt denominators;
- reviewer disagreements and `unclear` judgments;
- repeated-run variation;
- cost and latency tradeoffs; and
- cases where a condition improves protocol acceptance but not language-task
  quality.

The result remains a bounded study of the declared task set. It cannot establish
general language ability, production safety, or provider-wide behavior.

## Phase gates

### Gate 1: protocol freeze

Before any new provider calls:

- finalize the task manifest;
- finalize the prompt and schema revisions;
- finalize the evaluator and reference rubric;
- finalize held-out membership;
- set the spend and turn ceilings;
- record the exact model and provider; and
- verify that raw responses will remain local.

### Gate 2: pilot execution

Run the matched pilot once per condition under the frozen protocol. Preserve
refusals and incomplete cases. Do not rerun only failures.

### Gate 3: review and analysis

Privately reconcile reviewer forms, compare independent judgments, run the
metadata-only analysis, and record disagreements before drafting conclusions.

### Gate 4: paper decision

Submit to ARR only if the language-grounded result supports a substantive,
clearly stated language-processing contribution. Otherwise, keep the result as
an evaluation-methods pilot and choose a better-fitting venue.

## Not yet authorized

This protocol does not authorize a live-provider run, spend, public release of
raw responses, or a new submission. Those actions require the protocol and
budget to be reviewed first.
