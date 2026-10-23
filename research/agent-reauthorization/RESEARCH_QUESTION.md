# Research question and hypotheses

## Working title

**From Evaluation to Reauthorization: Change-Aware Governance for AI Agent Releases**

## Problem

An agent evaluation produces evidence about a particular system revision. A later
change may alter the model, prompt, tool, retrieval corpus, policy, evaluator, or
deployment environment. Teams often continue to cite the earlier result as if it
described the current system.

That is a stale claim: an older result presented as current evidence.

The practical risk is not only that an individual score is old. The risk is that an
organization makes a release, rollback, escalation, or continued-operation decision
without noticing that the evidence no longer covers the system under review.

## Primary research question

**Can revision-aware evidence plus an explicit reauthorization protocol reduce
unsupported release decisions after a tool-using AI-agent workflow changes, compared
with ordinary pass/fail reporting?**

Reauthorization means an explicit decision that the current evidence still supports
continued use after a relevant change.

## Secondary questions

1. Which change families most often invalidate a prior reliability claim?
2. Does revision-aware evidence detect invalid claims faster than ordinary reporting?
3. What evaluation and review cost does the protocol add?
4. Which controls are necessary: revision identity, change impact analysis, ownership,
   rollback evidence, or human approval?

## Pre-specified hypotheses

### H1: fewer unsupported approvals

The revision-aware conditions will produce fewer false-ready decisions than the
pass/fail baseline.

A false-ready decision is an approval that is not supported by the evidence available
for the changed system.

### H2: faster invalidation

The revision-aware conditions will identify stale evidence sooner than the baseline.

### H3: explicit cost

The revision-aware conditions will require more evaluation or review work than the
baseline.

The protocol must report this cost rather than treating it as an implementation detail.
A control that improves caution but is too expensive to use is not automatically a
successful operational design.

### H4: exploratory control value

The full reauthorization condition will identify failure modes that revision identity
alone cannot classify, especially missing ownership, missing rollback evidence, and
unresolved residual risk.

Residual risk is the risk that remains after the proposed controls are applied.

## Unit of analysis

The unit of analysis is a **claim-change case**:

1. a reliability or readiness claim;
2. the evidence that originally supported it;
3. a defined system revision;
4. the changed component or components;
5. the decision made after the change; and
6. the evidence that a reviewer was allowed to use.

This is not a claim about a model in the abstract. It is a claim about a bounded
workflow revision and a decision made from bounded evidence.

## Scope boundary

The first study will not infer hidden model state, collective mental state, or broad
capability from traces. It studies whether an operational claim remains supported by
the evidence available for the revised workflow.

The first study is offline and synthetic. It is a protocol pilot, not a production
readiness certification.
