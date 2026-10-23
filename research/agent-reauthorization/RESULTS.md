# Agent reauthorization study results

## Run identity

- **Source repository:** `julie-elkins/agent-assurance-harness`
- **Source commit:** `e75b35c41097efa550f7b23f4d6f1348af4696d9`
- **Artifact merge commit:** `fb3e004b4bdc27db777f1b3c8d23f2e76ec3ad17`
- **Case-set SHA-256:** `cf2a5661240cef17452bfb7217b9c91469f7590bd999490b99d648e6368c4ee3`
- **Case count:** 18
- **Change families:** prompt, tool, retrieval, authorization, evaluator, deployment
- **Run mode:** offline, deterministic, synthetic, metadata-only

The checked-in summary is [fixtures/reauthorization_pilot.json](../../fixtures/reauthorization_pilot.json).
The executable source is in the [Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness),
and the pilot command is:

```bash
uv run python tools/reauthorization_pilot.py \
  --output /tmp/agent-reauthorization-pilot.json \
  --markdown \
  --fail-on-findings
```

## Observed result

| condition | false-ready decisions | stale claims detected | correct reference decisions | relative time units |
|---|---:|---:|---:|---:|
| Pass/fail reporting | 12/18 | 0/12 | 6/18 | 18 |
| Revision-aware evidence | 0/18 | 12/12 | 12/18 | 42 |
| Revision-aware reauthorization | 0/18 | 12/12 | 18/18 | 60 |

A false-ready decision is an approval when the reference decision was
`review_required` or `blocked`. The baseline falsely approved every affected case in
the fixed matrix. Revision-aware evidence detected every affected case, but it did not
classify the missing owner and rollback controls in the negative controls. The full
reauthorization condition blocked all six negative controls and matched the reference
decision for all 18 cases.

The full condition used 60 relative time units versus 18 for the baseline. These units
are bounded study counters, not financial estimates. The result therefore shows a
tradeoff in the synthetic protocol: fewer unsupported approvals at the cost of more
review and evaluation work.

## What this result supports

This run supports the narrow claim that the implementation can produce the
pre-specified differences on the fixed synthetic case set:

- ordinary pass/fail reporting can approve a changed system without detecting the
  affected evidence;
- revision identity and invalidation can detect affected evidence; and
- the additional organizational controls can distinguish missing ownership and
  rollback evidence in the negative controls.

## What this result does not support

It does not establish that the protocol improves real production decisions, that the
reference oracle is universally correct, or that the controls cover every way an agent
system can change. It does not measure model quality, hidden model state, or business
impact.

## Held-out robustness run

The robustness run added twelve compound-change cases that were not part of the
original 18-case matrix. Expected decisions came from the separate
`reference-decisions.json` manifest in the harness rather than from the evaluator
logic.

- **Source commit:** `f260b3a34df7b2ca3717af1225c79f99aeba7921`
- **Artifact merge commit:** `026e3e902c121ee334551b539879f4e835afe9b5`
- **Case-set SHA-256:** `bae8a87462aadb05ee1d6ade23d7e6e839be580cad5f8f29bf042d19b95740f2`
- **Case count:** 30

| condition | false-ready decisions | stale claims detected | correct reference decisions | relative time units |
|---|---:|---:|---:|---:|
| Pass/fail reporting | 24/30 | 0/24 | 6/30 | 30 |
| Revision-aware evidence | 0/30 | 24/24 | 18/30 | 78 |
| Revision-aware reauthorization | 0/30 | 24/24 | 30/30 | 108 |

The full condition retained zero false-ready decisions and matched all 30 reference
decisions on the held-out matrix. This is a robustness observation, not
population-level evidence: the cases remain synthetic and deterministic.

## Independent reproduction

The robustness run was reproduced on 2026-10-23 from newly cloned repositories:

- Harness `main`: `026e3e902c121ee334551b539879f4e835afe9b5`
- Validity analysis `main`: `bcb83112361d22a2bcc03b4767cc7a51b04b1eeb`
- Case-set hash: `bae8a87462aadb05ee1d6ade23d7e6e839be580cad5f8f29bf042d19b95740f2`

The fresh run matched the checked-in compact fixture's case count, case-set hash,
condition counts, false-ready counts, stale-claim detection counts, correct
escalation counts, and bounded time counters. The executable also emits detailed
case-level fields that are intentionally omitted from the public compact fixture;
that representation difference is expected and does not change the reported
outcomes.

The independent reproduction requirement is complete for this phase. A later phase
may add independent reviewers without changing the primary protocol.
