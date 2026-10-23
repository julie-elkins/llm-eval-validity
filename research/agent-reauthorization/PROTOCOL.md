# Phase-1 protocol

## Purpose

Test whether a small, reproducible protocol can distinguish a current reliability claim
from a stale one after a synthetic agent-workflow change.

The protocol is intentionally offline. It uses deterministic records and synthetic
workflow outcomes so another reader can replay the study without credentials, private
telemetry, or a live model.

## Conditions

Each claim-change case is evaluated under three conditions.

### Condition A: pass/fail baseline

The record contains the prior evaluation result and a current pass/fail result. The
decision process does not require revision identity, change impact analysis, or an
explicit reauthorization record.

This represents a plausible ordinary reporting workflow, not a claim that every
production team uses this exact process.

### Condition B: revision-aware evidence

The record contains:

- system revision identifier;
- evaluation revision identifier;
- scenario-pack identifier;
- evidence digest;
- changed component;
- evidence status; and
- a rule that affected evidence becomes stale until reevaluated.

This condition tests whether provenance and invalidation alone reduce unsupported
decisions.

### Condition C: revision-aware reauthorization

Condition C includes everything in Condition B plus:

- change classification;
- accountable owner;
- required reevaluation scope;
- rollback evidence;
- incident or escalation path;
- residual-risk statement;
- human approval boundary; and
- a final decision of `reauthorized`, `blocked`, or `review_required`.

This condition tests the organizational decision layer rather than only the evidence
record.

## Synthetic change families

The pilot will include at least one case in each family:

1. prompt or instruction change;
2. tool or API change;
3. retrieval-data or policy-source change;
4. authorization or permission-policy change;
5. evaluator or threshold change;
6. deployment or dependency change.

Each family will contain:

- one case where the prior claim remains applicable;
- one case where affected evidence must be rerun; and
- one negative control that looks healthy but must not be approved.

A negative control is a deliberately plausible green-looking case used to test whether
the protocol catches the condition it claims to govern.

## Decision oracle

The pilot needs a deterministic reference decision for each synthetic case. The oracle
will be defined before condition outputs are generated and will inspect the complete
synthetic case record, including the declared change and the required evidence.

The oracle is a study reference, not a claim that real organizations have one perfect
decision-maker. Its purpose is to make disagreement measurable in the pilot.

## Primary outcomes

### False-ready rate

The proportion of cases approved as ready when the reference decision is
`blocked` or `review_required`.

### Stale-claim detection rate

The proportion of cases requiring reevaluation where the condition identifies stale
evidence before approval.

### Detection latency

The number of decision steps between the change and the first stale-evidence or
missing-evidence finding.

### Correct escalation rate

The proportion of cases routed to `review_required` when the case cannot be safely
resolved by the available evidence.

### Operational cost

Count evaluation runs, review steps, blocked approvals, and synthetic time units.
Cost must be reported alongside safety-relevant outcomes.

## Secondary outcomes

- unsupported-claim rate;
- incorrect automatic closure rate;
- rollback-evidence completeness;
- ownership completeness;
- proportion of cases that remain unestablished;
- false-block rate.

## Analysis plan

Phase 1 will report counts and exact proportions by condition and change family. It
will not claim inferential generalization from the synthetic cases.

If the pilot produces enough repeated cases per family, the report may include
confidence intervals. A confidence interval is a range describing uncertainty around
an estimate; it does not turn synthetic coverage into production evidence.

The primary comparison is:

```text
Condition A versus Condition C on false-ready rate
```

Condition B is the intermediate comparison that tests whether versioned evidence
accounts for the result without the organizational protocol.

## Exclusions

The pilot will not:

- call a provider API;
- use private production traces;
- make claims about a named vendor's safety;
- infer model intent or internal state;
- use unreviewed human-subject data;
- tune the protocol after seeing pilot outcomes;
- treat a passing negative control as evidence that the protocol works.

## Stopping rule

The pilot stops after every change family has the required current, stale, and
negative-control cases and all three conditions have been evaluated on the same case
set.

No additional cases may be added solely because they improve a result. Any extension
must be recorded as a new pilot or a pre-specified robustness phase.

## Reproducibility requirements

The implementation must check in:

- synthetic case definitions;
- the decision oracle;
- condition outputs;
- analysis code;
- expected result fixtures;
- a command that runs offline; and
- a report that states what the run proves and does not prove.

The first executable implementation belongs in the Agent Assurance Harness. This
repository will consume the resulting metadata and analysis rather than duplicating
the harness protocol.
