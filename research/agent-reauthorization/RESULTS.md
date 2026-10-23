# Phase-1 pilot results

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

The next research step is a robustness phase: vary case difficulty and add independent
reviewers without changing the primary protocol or using the pilot result to redefine
success.
