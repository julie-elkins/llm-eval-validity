# Frozen pilot results

## Decision

**Condition B did not improve the measured evidence contract in either
replicated model configuration.** In Sonnet 5.5 it lowered protocol acceptance
from 93.3% to 73.3%. In Haiku 5.5 it lowered acceptance from 60.0% to 30.0%.
Among accepted traces, evidence-contract satisfaction was effectively unchanged
for Sonnet and lower for Haiku.

This is a boundary result. It shows that provider-valid structured output is
not equivalent to usable assurance evidence in these runs. It does not show
that structured output is generally harmful or that either model is generally
unreliable.

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

### Haiku 5.5 replication

| measure | Condition A: local validation | Condition B: provider structured output |
|---|---:|---:|
| attempted | 30 | 30 |
| accepted | 18 | 9 |
| refused | 12 | 21 |
| acceptance rate | 60.0% | 30.0% |
| refusal rate | 40.0% | 70.0% |
| accepted and contract-satisfying | 9 | 3 |
| contract satisfaction among accepted | 50.0% | 33.3% |
| contract satisfaction over all attempted | 30.0% | 10.0% |
| planning estimate | $2.35 | $1.50 |
| planning ceiling | $5.00 | $5.00 |

Percentage-point changes are calculated as Condition B minus Condition A:

- acceptance: **-30.0 points**;
- refusal: **+30.0 points**;
- contract satisfaction among accepted traces: **-16.7 points**;
- contract satisfaction over all attempted cases: **-20.0 points**.

The lower structured-output planning estimate is again not a cost finding. It
reflects fewer successful provider interactions, not proof that the treatment
uses fewer resources for equivalent work.

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

## Cross-model interpretation

| model | condition | accepted | refused | contract-satisfying | contract among accepted | contract over all |
|---|---|---:|---:|---:|---:|---:|
| Sonnet 5.5 | local validation | 28/30 | 2/30 | 15 | 53.6% | 50.0% |
| Sonnet 5.5 | structured output | 22/30 | 8/30 | 12 | 54.5% | 40.0% |
| Haiku 5.5 | local validation | 18/30 | 12/30 | 9 | 50.0% | 30.0% |
| Haiku 5.5 | structured output | 9/30 | 21/30 | 3 | 33.3% | 10.0% |

The structured-output arm lowered acceptance in both model configurations:
20.0 percentage points for Sonnet and 30.0 for Haiku. That repeated direction
is stronger evidence than the original one-model result, but it remains a
within-provider replication, not a cross-provider finding.

The model effect is also visible: Haiku accepted fewer traces than Sonnet under
both output conditions. Because the arms were not designed as a model benchmark,
this is a descriptive observation, not a ranking or a claim about capability.

## OpenAI cross-provider baseline

The OpenAI prompt-plus-local-validation arm was run against the same fixed
30-case matrix using the preregistered `gpt-5.6` identifier and the same
three-turn ceiling.

| measure | OpenAI baseline |
|---|---:|
| attempted | 30 |
| accepted | 26 |
| refused | 4 |
| acceptance rate | 86.7% |
| refusal rate | 13.3% |
| accepted and contract-satisfying | 15 |
| contract satisfaction among accepted | 57.7% |
| contract satisfaction over all attempted | 50.0% |
| planning estimate | $3.30 |
| planning ceiling | $5.00 |

All four refusals occurred after the provider response. The
`http-200-empty-context-retry` scenario refused in all three replicates, and
one `ambiguous-side-effect-retry` replicate also refused. The refusal codes
describe the frozen adapter boundary; they do not establish why the provider
failed to produce an acceptable final event.

This is a cross-provider baseline, not a provider ranking. The corresponding
OpenAI structured-output condition has not been run, so no OpenAI
structured-output comparison is reported here.

### OpenAI structured-output comparison

| measure | OpenAI baseline | OpenAI structured output | change |
|---|---:|---:|---:|
| attempted | 30 | 30 | -- |
| accepted | 26 | 27 | +1 |
| refused | 4 | 3 | -1 |
| acceptance rate | 86.7% | 90.0% | +3.3 pp |
| accepted and contract-satisfying | 15 | 14 | -1 |
| contract satisfaction among accepted | 57.7% | 51.9% | -5.8 pp |
| contract satisfaction over all attempted | 50.0% | 46.7% | -3.3 pp |
| planning estimate | $3.30 | $3.25 | -- |
| planning ceiling | $5.00 | $5.00 | -- |

Structured output slightly improved OpenAI protocol acceptance, but it did
not improve end-to-end usable evidence. The three structured-arm refusals were
all bounded `tool_loop_turn_limit_exceeded` stops for the
`http-200-empty-context-retry` scenario. The planning estimates are not a cost
finding because they are affected by refusal and turn behavior.

## Interpretation

The pilot supports three restrained conclusions:

1. The local evidence contract catches failures that provider-enforced output
   structure does not eliminate.
2. Adding the provider schema did not increase the proportion of accepted traces
   that satisfied the local contract in either model configuration.
3. The structured condition had lower usable-evidence yield over all attempted
   cases because it produced more refusals.
4. The direction of the acceptance loss replicated across Sonnet and Haiku,
   while the magnitude and accepted-trace contract rate varied by model.
5. The OpenAI baseline and structured-output arms show that a small increase
   in protocol acceptance can coexist with lower evidence-contract
   satisfaction; formatting acceptance is not the same as usable evidence.

The pilot does not support these stronger claims:

- that provider structured output is inferior in general;
- that Claude Sonnet 5.5 is inferior to another model;
- that the result transfers to production agents;
- that the evidence contract measures user-perceived answer quality;
- that the observed differences are statistically significant.

## Limitations

- **Provider-specific configurations.** The OpenAI comparison is complete for
  this fixed model, schema, prompt, tool loop, and synthetic matrix, but it
  cannot establish a general provider or model effect.
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

Design a broader scenario matrix or an independent reviewer/reference phase.
The next phase should be selected for a measurement reason, not to replace the
inconvenient refusal result or retune the completed OpenAI comparison.
