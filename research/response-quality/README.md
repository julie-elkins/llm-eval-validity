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

**Claude pilot comparison frozen; OpenAI baseline added.** The study contains
four frozen 30-case conditions across two approved Claude model identifiers and
one frozen OpenAI local-validation baseline, using the same synthetic case
matrix, bounded tool loop, cost ceiling, and local validator:

- Sonnet Condition A: prompt plus local validation.
- Sonnet Condition B: provider-enforced structured output plus local validation.
- Haiku Condition A: prompt plus local validation.
- Haiku Condition B: provider-enforced structured output plus local validation.
- OpenAI baseline: prompt plus local validation.

The OpenAI structured-output condition remains to be run as a separate
comparison arm.

The results are metadata-only. Prompts, model responses, tool arguments, and
credentials are not part of the public artifact.

## Result at a glance

### Sonnet 5.5

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
The same direction appeared in the Haiku replication, but the magnitude was
larger; the result is still limited to these two model configurations.

### Haiku 5.5 replication

| measure | Condition A | Condition B | change |
|---|---:|---:|---:|
| attempted cases | 30 | 30 | -- |
| accepted traces | 18 (60.0%) | 9 (30.0%) | -30.0 pp |
| provider refusals | 12 (40.0%) | 21 (70.0%) | +30.0 pp |
| accepted traces satisfying the evidence contract | 9/18 (50.0%) | 3/9 (33.3%) | -16.7 pp |
| all attempted cases satisfying the evidence contract | 9/30 (30.0%) | 3/30 (10.0%) | -20.0 pp |

### OpenAI baseline

| measure | OpenAI baseline |
|---|---:|
| attempted cases | 30 |
| accepted traces | 26 (86.7%) |
| provider refusals | 4 (13.3%) |
| accepted traces satisfying the evidence contract | 15/26 (57.7%) |
| all attempted cases satisfying the evidence contract | 15/30 (50.0%) |

The OpenAI arm is a frozen cross-provider baseline, not a provider ranking.
Its structured-output counterpart has not yet been run.

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

It can establish the observed differences between the five frozen baseline or
comparison conditions on the fixed 30-case matrix, including the refusal and
evidence-contract counts. The OpenAI baseline is descriptive until its
structured-output counterpart is run.

It cannot establish general model quality, production safety, causal superiority
of structured output, user-facing response quality, or performance across other
providers, schemas, prompts, tools, or model versions. The OpenAI structured-
output arm, a wider scenario matrix, and an independent quality reference are
required before making those claims.

## Reproduction boundary

The live-provider adapter and raw responses remain local to
`agent-reliability-lab`. This public repository records compact metadata-only
results so the research record can be reviewed without publishing prompts,
responses, tool arguments, or API credentials.
