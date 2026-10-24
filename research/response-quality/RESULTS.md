# Frozen pilot results

## Decision

**Condition B did not improve the measured evidence contract in this
configuration.** It lowered protocol acceptance from 93.3% to 73.3%. Among
traces that were accepted, evidence-contract satisfaction was effectively
unchanged: 53.6% in Condition A versus 54.5% in Condition B.

This is a boundary result. It shows that provider-valid structured output is
not equivalent to usable assurance evidence. It does not show that structured
output is generally harmful or that the model is generally unreliable.

## Results

| measure | Condition A: local validation | Condition B: provider structured output |
|---|---:|---:|
| attempted | 30 | 30 |
| accepted | 28 | 22 |
| refused | 2 | 8 |
| acceptance rate | 93.3% | 73.3% |
| refusal rate | 6.7% | 26.7% |
| accepted and contract-satisfying | 15 | 12 |
| contract satisfaction among accepted | 53.6% | 54.5% |
| contract satisfaction over all attempted | 50.0% | 40.0% |
| planning estimate | $2.95 | $2.30 |
| planning ceiling | $5.00 | $5.00 |

Percentage-point changes are calculated as Condition B minus Condition A:

- acceptance: **-20.0 points**;
- refusal: **+20.0 points**;
- contract satisfaction among accepted traces: **+0.9 points**;
- contract satisfaction over all attempted cases: **-10.0 points**.

The planning estimate is not evidence that Condition B is cheaper. The
structured condition completed fewer provider interactions successfully, so
comparing its estimate as a standalone cost result would confound cost with
refusal behavior.

## Refusal pattern

Condition A recorded two after-response provider refusals. Condition B recorded
eight after-response refusals, including one schema-specific
`claude_schema_reliability_id_required` refusal and seven generic provider
response refusals. These are wire-level outcome codes, meaning they describe
the adapter's observed protocol state rather than the content of a model
response.

The refusal pattern matters because the intervention was intended to improve
output reliability. In this run, the intervention changed the failure surface
more than it changed the evidence quality of accepted traces.

## Interpretation

The pilot supports three restrained conclusions:

1. The local evidence contract catches failures that provider-enforced output
   structure does not eliminate.
2. Adding the provider schema did not increase the proportion of accepted traces
   that satisfied the local contract.
3. The structured condition had lower usable-evidence yield over all attempted
   cases because it produced more refusals.

The pilot does not support these stronger claims:

- that provider structured output is inferior in general;
- that Claude Sonnet 5.5 is inferior to another model;
- that the result transfers to production agents;
- that the evidence contract measures user-perceived answer quality;
- that the observed differences are statistically significant.

## Limitations

- **One model configuration.** The pilot uses one Claude Sonnet 5.5
  configuration. A second model replication is needed to separate provider/schema
  effects from model-specific behavior.
- **Small fixed matrix.** Thirty cases are enough to expose protocol behavior,
  not enough to estimate a production failure rate precisely.
- **Synthetic scenarios.** The cases exercise bounded assurance patterns rather
  than real user traffic or production tools.
- **Accepted-trace conditioning.** The among-accepted comparison can look stable
  while the overall usable-evidence yield falls. Both denominators are reported
  to keep this selection effect visible.
- **No raw response review.** The public artifact intentionally retains no
  prompts or responses, so this study cannot explain every provider refusal from
  content inspection.
- **Schema implementation is one treatment.** A different schema, prompt,
  native-tool arrangement, or provider feature could produce a different result.

## Next test

Run the pre-registered second-model replication in
[PROTOCOL.md](PROTOCOL.md) without changing the frozen Sonnet conditions.
After that replication, the study can justify a larger matrix or a human-reviewer
phase. It should not add either phase merely to replace an inconvenient result.
