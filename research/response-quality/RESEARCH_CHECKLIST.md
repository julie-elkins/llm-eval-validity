# Reporting checklist

This checklist separates what the pilot demonstrates from what still requires
validation.

| area | status | evidence or remaining work |
|---|---|---|
| Research question | complete | `PROTOCOL.md` states the comparison. |
| Conditions | complete | Local validation and provider structured output are defined. |
| Fixed case matrix | complete | 30 cases, ten scenarios, three replicates per scenario. |
| Primary outcomes | complete | Acceptance, refusal, and evidence-contract satisfaction are defined. |
| Denominator policy | complete | Accepted-trace and all-attempt results are both reported. |
| Cost ceiling | complete | Each run had a five-dollar planning ceiling. |
| Data boundary | complete | Public artifact is metadata-only. |
| Frozen results | complete | Both Sonnet conditions are recorded in `RESULTS.md`. |
| Statistical inference | intentionally absent | The pilot is descriptive; no significance claim is made. |
| Second-model replication | not started | Must use the same matrix and frozen conditions. |
| Larger scenario matrix | not started | Consider only after the replication result. |
| Human reviewer study | not started | Requires consent, privacy, sampling, and agreement protocol. |
| Production validation | not established | No production traces, user outcomes, or live business decision are measured. |

## Claim boundary

**Observed:** the two frozen Claude conditions produced the reported acceptance,
refusal, and evidence-contract counts on the fixed matrix.

**Inferred within scope:** provider-enforced structure did not improve usable
evidence yield in this configuration and changed the refusal surface.

**Not established:** general model quality, production safety, cross-provider
generalization, user-perceived quality, or causal superiority of either
implementation pattern.
