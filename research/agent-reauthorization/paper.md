# From Evaluation to Reauthorization: Change-Aware Governance for AI Agent Releases

## Abstract

AI-agent evaluations are tied to a particular system revision, but release and
continued-operation decisions often outlive the evidence that supports them. A change
to a prompt, tool, data source, policy, evaluator, or deployment environment can make a
previous reliability claim incomplete without changing the stored score.

This working paper proposes a reproducible pilot study of that problem. The study
compares ordinary pass/fail reporting, revision-aware evidence, and revision-aware
evidence combined with an explicit reauthorization protocol. The protocol records
change impact, required reevaluation, accountable ownership, rollback evidence,
escalation, residual risk, and human approval boundaries.

Phase 1 uses deterministic synthetic cases and an offline decision oracle. The pilot
does not claim production safety or general agent capability. It asks a narrower
question: whether the added evidence and decision controls reduce unsupported
approval decisions after a defined workflow change, and what operational cost those
controls add.

**Status:** Protocol scaffold. Results are not yet available.

## 1. Introduction

An evaluation result is not a property of an agent in the abstract. It is evidence
produced by a particular scenario set, evaluator, workflow, and system revision.

That distinction becomes operationally important when the system changes. A team may
update a tool, prompt, retrieval corpus, authorization policy, evaluator threshold,
dependency, or deployment configuration while continuing to cite an earlier result.
The stored result can remain internally correct while no longer supporting the decision
being made.

This paper studies that gap between evaluation and release decision.

## 2. Research question

See [RESEARCH_QUESTION.md](RESEARCH_QUESTION.md).

## 3. Related work

See [RELATED_WORK.md](RELATED_WORK.md). The contribution is not a new claim about
provenance, continuous evaluation, or agent reliability in isolation. It is the
controlled study of how revision-aware evidence and reauthorization controls affect
operational decisions after change.

## 4. Method

See [PROTOCOL.md](PROTOCOL.md). The protocol is written before the pilot results so
that the conditions and primary outcomes are not selected after observing an outcome.

## 5. Results

**Not yet run.**

This section will contain the frozen case-set identifier, condition counts, primary
outcomes, cost accounting, and negative-control results. No result should be added
without the corresponding reproducible fixture and command.

## 6. Limitations

The first phase is synthetic and deterministic. It can test whether the protocol is
internally coherent and whether the conditions differ on controlled cases. It cannot
establish that the protocol improves real production decisions, covers all
organizational practices, or measures hidden model state.

The decision oracle is a reference for the pilot, not a universal authority. A later
study would need independent reviewers, real change histories, or both.

## 7. Reproducibility

The intended final command will run offline from checked-in synthetic cases and emit
metadata-only results. The implementation will live in the Agent Assurance Harness;
this repository will contain the analysis and paper outputs.

## 8. Future work

The next phase will implement the synthetic case generator and three-condition
decision runner. A later robustness phase may vary case difficulty, add independent
reviewers, and compare protocol decisions with decisions made from real but
sanitized change histories.
