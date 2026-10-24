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
| Frozen results | complete | Both Sonnet and both Haiku conditions are recorded in `RESULTS.md`. |
| Statistical inference | intentionally absent | The pilot is descriptive; no significance claim is made. |
| Second-model replication | complete | Haiku used the same matrix and frozen conditions; results remain within-provider. |
| Larger scenario matrix | not started | Select the next matrix for coverage, not for a cleaner result. |
| Cross-provider replication | not started | Needed before generalizing beyond the Claude provider family. |
| Human reviewer study | not started | Requires consent, privacy, sampling, and agreement protocol. |
| Production validation | not established | No production traces, user outcomes, or live business decision are measured. |

## Claim boundary

**Observed:** four frozen conditions across Sonnet 5.5 and Haiku 5.5 produced
the reported acceptance, refusal, and evidence-contract counts on the fixed
matrix.

**Inferred within scope:** provider-enforced structure did not improve usable
evidence yield in either tested Claude configuration and changed the refusal
surface in the same direction.

**Not established:** general model quality, production safety, cross-provider
generalization, user-perceived quality, or causal superiority of either
implementation pattern.
