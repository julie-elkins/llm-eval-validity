# Protocol

## 1. Scope and status

This protocol defines a controlled, metadata-first study of evaluation
evidence. It is not a provider benchmark, a production certification, or a
claim about the quality of a named model.

The study begins offline with synthetic and public cases. A live-provider arm
requires a separately frozen manifest, cost ceiling, credential boundary, and
approval to run.

## 2. Matched comparison

Every condition receives the same:

- case identifier and task;
- allowed tools and tool schemas;
- evidence package;
- system revision metadata;
- budget and latency ceiling;
- stopping rule;
- output vocabulary; and
- locked reference disposition.

The conditions differ only in what review evidence is available and which
verification actions are permitted. No condition may receive additional
attempts because an earlier condition failed.

## 3. Review layers

### Layer A — Outcome-only review

Inputs:

- task;
- final answer or final workflow outcome; and
- output schema required by the case.

The reviewer records `accept`, `reject`, or `review_required`. The layer does
not inspect the evidence path.

### Layer B — Evidence-aware review

Layer B receives Layer A's inputs plus:

- approved evidence identifiers;
- evidence source and revision;
- evidence freshness and status;
- required fields and constraints;
- tool and permission status;
- bounded workflow metadata; and
- uncertainty or escalation signals.

The reviewer must decide whether the evidence supports the claimed outcome.

### Layer C — Executable verification

Layer C receives Layer B's inputs and runs deterministic checks for:

- schema and identifier validity;
- claim-to-evidence linkage;
- required-field completeness;
- revision and freshness rules;
- replayable calculations;
- invariant violations;
- tool and permission correctness;
- negative-control behavior; and
- declared cost, latency, and stopping limits.

An executable check may establish that a defined property holds or fails. It
must not silently convert a failed check into a passing result.

### Layer D — Blinded human adjudication

Layer D receives the evidence package and the Layer C report, but not:

- the private reference disposition;
- another reviewer's judgment;
- a model's confidence score; or
- the expected direction of the study result.

At least two independent reviewers should judge the same locked cases before
human agreement is reported. A single reviewer can provide a calibration
observation, but not a human–human agreement estimate.

## 4. Defect taxonomy

The case manifest must label the planted defect before any condition runs.
Each case has one primary defect family and may have secondary tags.

1. **Unsupported claim** — the result asserts something absent from the
   evidence.
2. **Wrong source** — the cited evidence does not support the claim.
3. **Stale evidence** — the evidence predates a relevant workflow revision.
4. **Contradictory evidence** — available evidence conflicts with the claim.
5. **Missing uncertainty** — the case requires qualification, abstention, or
   escalation that the result omits.
6. **Missing constraint** — a required boundary, permission, or resource limit
   is absent.
7. **Tool misuse** — the wrong tool, arguments, permissions, or sequence are
   used.
8. **Execution mismatch** — code, data, or replay does not match the stated
   method or result.
9. **Leakage** — target, answer, or evaluation information improperly enters
   the input or decision path.
10. **False completion** — the workflow reports success without completing the
    required action or verification.
11. **Polished negative control** — the output looks healthy but must be
    rejected by the reference disposition.
12. **Supported control** — evidence and execution support the stated result.

The supported control is required so the study measures false rejection as well
as false acceptance.

## 5. Case-set construction

The case-set author creates the private reference disposition before condition
outputs are generated. The public manifest may expose identifiers, defect
families, and aggregate expectations, but not private answer keys or raw
review packets.

The planned split is:

- **Development set:** used to debug the harness and review form.
- **Locked holdout:** not inspected for tuning after the protocol is frozen.
- **Robustness set:** a separately generated set with changed wording,
  evidence order, and non-semantic identifiers.

Each split must include every defect family and supported controls. Cases sharing
the same template or generated seed receive an independence-group identifier;
analysis must not treat those cases as independent observations.

The final case count must be recorded before execution. A sample-size or
precision calculation must justify any confirmatory claim; a convenient case
count is not evidence of adequate power.

## 6. Reference disposition

The private reference disposition is created from the complete case record and
the pre-registered rubric. It records:

- expected decision;
- required evidence;
- prohibited or contradictory evidence;
- expected escalation or refusal;
- defect family;
- independence group; and
- adjudication rationale.

The reference is a study oracle, meaning a pre-specified comparison standard,
not a claim that real organizations have a perfect decision-maker.

## 7. Human review

Reviewers receive:

- a short study brief;
- one case packet at a time;
- the task and permitted evidence;
- the Layer C report;
- the review form; and
- a return and confidentiality instruction.

The form records:

- decision;
- evidence sufficiency;
- claim-to-evidence support;
- execution or tool correctness;
- uncertainty or escalation requirement;
- confidence; and
- optional free-text rationale.

Reviewers must not receive private answer keys, other reviewers' forms, raw
provider traces, or unpublished certification content.

Disagreements are preserved. Adjudication is a separate recorded step and must
not overwrite the original reviewer judgments.

## 8. Primary and secondary outcomes

### Primary outcome

False-acceptance rate on the locked holdout:

```text
cases accepted by a layer when the reference is reject or review_required
---------------------------------------------------------------------------
all locked-holdout cases attempted by that layer
```

### Secondary outcomes

- false-rejection rate;
- reference agreement;
- claim-to-evidence agreement;
- execution-check detection rate;
- negative-control block rate;
- reviewer–reviewer agreement;
- reviewer–reference agreement;
- refusal and incomplete-run rate;
- review time;
- execution time;
- provider or compute cost, if a live arm is later approved; and
- escalation rate.

Refusals and incomplete runs remain in the denominator for attempt-level
metrics. Accepted-only metrics may be shown separately but must not replace the
all-attempt result.

## 9. Stopping rules

The offline phase stops when:

1. the manifest, reference dispositions, and split digests are frozen;
2. every defect family appears in development, holdout, and robustness sets;
3. all four layers have produced an output or an explicit refusal;
4. human review has reached the pre-specified reviewer count; and
5. the analysis report and limitations are reproducible from the committed
   artifacts.

No cases may be added solely because they improve a result. Any extension is a
new phase with a new manifest and analysis record.

## 10. Exclusions

The study will not:

- use private certification items or production customer data;
- publish prompts, raw responses, answer keys, or reviewer identities;
- infer model intent or internal state;
- treat code execution as proof of causal validity;
- pool providers into a general ranking;
- tune the protocol on locked holdout cases;
- claim synthetic results are learner, production, or population outcomes; or
- use a human-participant phase before an appropriate ethics determination.

## 11. Reproducibility requirements

Before a result is reported, the repository must contain:

- case manifest and digest;
- reference-disposition schema;
- split definition;
- layer output schema;
- executable validators;
- reviewer form and calibration instructions;
- analysis code;
- expected aggregate fixtures;
- a no-network reproduction command; and
- a limitations statement.

The executable control implementation belongs in the Agent Assurance Harness.
This repository owns the research protocol and aggregate analysis.
