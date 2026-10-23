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

**Status:** Phase-3 held-out robustness run complete; independent reproduction remains.

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

The first deterministic pilot used 18 synthetic cases across six change families and
three decision conditions. The [results report](RESULTS.md) records the source commit,
case-set hash, condition counts, cost counters, and interpretation boundary.

The pass/fail baseline made 12 false-ready decisions out of 18 cases. Revision-aware
evidence made none, detected all 12 affected cases, and matched 12 of the 18 reference
decisions. The full reauthorization condition made no false-ready decisions, matched
all 18 reference decisions, and blocked all six negative controls.

The full condition used 60 relative time units compared with 18 for the baseline. The
pilot therefore exposes the expected tradeoff: stronger decision controls add work.
These are synthetic counters, not financial estimates.

The held-out robustness run added twelve compound-change cases, for 30 cases total.
The pass/fail baseline made 24 false-ready decisions. Revision-aware evidence detected
all 24 affected cases, and the full reauthorization condition made no false-ready
decisions and matched all 30 reference decisions. The full condition used 108
relative time units compared with 30 for the baseline.

## 6. Reporting and reproducibility

The protocol was publicly locked before the pilot implementation: the protocol merged
in `llm-eval-validity` commit `b1090f5068466a990fe836698177b5a0dd102278`, and the
pilot implementation was run from Agent Assurance Harness commit
`e75b35c41097efa550f7b23f4d6f1348af4696d9`. The result is bound to the case-set hash
recorded in [RESULTS.md](RESULTS.md). That implementation is now merged into the
harness `main` branch at `fb3e004b4bdc27db777f1b3c8d23f2e76ec3ad17`.

The pilot is deterministic, so it has no random seed and no sampling-based confidence
interval. Reporting a p-value or a confidence interval for this fixed matrix would
create a false appearance of population inference. The correct phase-1 report is
exact counts, control outcomes, bounded cost counters, and explicit limitations.

The code, protocol, compact result, and reporting checklist are public. The run uses
no provider API, credentials, private telemetry, or content-bearing payloads. The
[research checklist](RESEARCH_CHECKLIST.md) records the remaining artifact and
robustness requirements before this can be described as a completed study.

## 7. Limitations

The first phase is synthetic and deterministic. It can test whether the protocol is
internally coherent and whether the conditions differ on controlled cases. It cannot
establish that the protocol improves real production decisions, covers all
organizational practices, or measures hidden model state.

The decision oracle is a reference for the pilot, not a universal authority. A later
study would need independent reviewers, real change histories, or both.

## 8. Reproducibility

The intended final command will run offline from checked-in synthetic cases and emit
metadata-only results. The implementation will live in the Agent Assurance Harness;
this repository will contain the analysis and paper outputs.

## 9. Future work

The next phase is an independent reproduction from a clean checkout. After that, a
separate reviewer study may vary case difficulty and add independent reviewers without
changing the primary protocol. A later study may compare protocol decisions with real
but sanitized change histories.
