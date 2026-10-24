# Response-quality measurement under provider output constraints

This study tests whether provider-enforced structured output improves the
reliability of a bounded LLM-backed agent workflow.

The question is narrower than "which model is better?" It asks whether adding a
provider-facing JSON Schema changes two observable properties of the same
synthetic workflow:

1. whether the model produces a trace the adapter can accept; and
2. whether an accepted trace satisfies the local evidence contract.

An evidence contract is the minimum metadata the harness requires before it
will treat a result as usable evidence: a valid classification, the required
identifier, and the bounded operation and cost fields needed for the scenario.
Provider-valid structure is not allowed to override that local contract.

## Current status

**Pilot comparison frozen.** The study contains two 30-case Claude Sonnet 5.5
conditions using the same synthetic case matrix, bounded tool loop, cost ceiling,
and local validator:

- Condition A: prompt plus local validation.
- Condition B: provider-enforced structured output plus local validation.

The results are metadata-only. Prompts, model responses, tool arguments, and
credentials are not part of the public artifact.

## Result at a glance

| measure | Condition A | Condition B | change |
|---|---:|---:|---:|
| attempted cases | 30 | 30 | -- |
| accepted traces | 28 (93.3%) | 22 (73.3%) | -20.0 pp |
| provider refusals | 2 (6.7%) | 8 (26.7%) | +20.0 pp |
| accepted traces satisfying the evidence contract | 15/28 (53.6%) | 12/22 (54.5%) | +0.9 pp |
| all attempted cases satisfying the evidence contract | 15/30 (50.0%) | 12/30 (40.0%) | -10.0 pp |

The result does **not** establish that structured output is generally worse.
It establishes that this provider/schema configuration did not improve the
measured evidence contract and produced more protocol refusals in this pilot.
The comparison is therefore useful as a boundary result, not as a model ranking.

## Documents

- [Protocol and planned replication](PROTOCOL.md)
- [Frozen results and analysis](RESULTS.md)
- [Research log](RESEARCH_LOG.md)
- [Reporting checklist](RESEARCH_CHECKLIST.md)

## Relationship to the reauthorization paper

This is a separate study from
[From Evaluation to Reauthorization](../agent-reauthorization/README.md).
The reauthorization paper asks whether evidence survives a workflow revision.
This study asks whether a provider output constraint changes trace acceptance and
evidence satisfaction. Keeping them separate prevents a reader from attributing
the live-provider result to the offline governance protocol.

## What this pilot can and cannot establish

It can establish the observed difference between these two frozen conditions on
the fixed 30-case matrix, including the refusal and evidence-contract counts.

It cannot establish general model quality, production safety, causal superiority
of structured output, user-facing response quality, or performance across other
providers, schemas, prompts, tools, or model versions. A second-model replication
and a wider scenario matrix are required before making those claims.

## Reproduction boundary

The live-provider adapter and raw responses remain local to
`agent-reliability-lab`. This public repository records compact metadata-only
results so the research record can be reviewed without publishing prompts,
responses, tool arguments, or API credentials.
