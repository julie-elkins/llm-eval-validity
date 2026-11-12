# Reporting checklist

This checklist separates what the pilot demonstrates from what still requires
validation.

| area | status | evidence or remaining work |
|---|---|---|
| Research question | complete | `PROTOCOL.md` states the comparison. |
| Conditions | complete | Local validation and provider structured output are defined. |
| Fixed case matrix | complete | 30 cases, ten scenarios, three replicates per scenario. |
| Related-work positioning | complete | `RELATED_WORK.md` maps validity, benchmark, judge, variance, and tool-environment literature to this study's narrower claims. |
| Primary outcomes | complete | Acceptance, refusal, and evidence-contract satisfaction are defined. |
| Denominator policy | complete | Accepted-trace and all-attempt results are both reported. |
| Cost ceiling | complete | Each run had a five-dollar planning ceiling. |
| Data boundary | complete | Public artifact is metadata-only. |
| Frozen results | complete | Both Claude conditions for Sonnet and Haiku, plus both OpenAI conditions, are recorded in `RESULTS.md`. |
| Statistical inference | intentionally absent | The pilot is descriptive; no significance claim is made. |
| Second-model replication | complete | Haiku used the same matrix and frozen conditions; results remain within-provider. |
| Larger scenario matrix | not started | Select the next matrix for coverage, not for a cleaner result. |
| Cross-provider replication | complete | OpenAI baseline and structured-output arms are frozen and reported separately; the result remains configuration-specific. |
| Human reviewer study | v1 complete; v2 recruitment and reconciliation in progress | Three v1 calibration reviews support the v2 rubric revision. V2 uses a private intake tracker and a public-safe adjudication plan; returned forms remain outside the aggregate result until packet version, completeness, and provenance are reconciled. |
| Reviewer comparison analysis | prepared, not run | The analysis plan defines reviewer-to-reviewer agreement, local-contract comparison, `unclear` handling, disagreement reasons, and the two completion gates. |
| Public/private boundary | complete for the planned review phase | The public repository contains only blank process templates and aggregate-safe documentation; identities, forms, raw case content, traces, and the answer key remain local. |
| Production validation | not established | No production traces, user outcomes, or live business decision are measured. |

## Claim boundary

**Observed:** six frozen conditions across Claude Sonnet 5.5, Claude Haiku 5.5,
and OpenAI `gpt-5.6` produced the reported acceptance, refusal, and
evidence-contract counts on the fixed matrix.

**Inferred within scope:** provider-enforced structure did not improve usable
evidence yield in either tested Claude configuration and changed the refusal
surface in the same direction.

**Not established:** general model quality, production safety, cross-provider
generalization, user-perceived quality, or causal superiority of either
implementation pattern.

The version-2 reviewer round can strengthen calibration evidence, but it cannot
remove the small synthetic matrix, provider-specific configuration, or
metadata-only public-data limitations.
