# Protocol

## Research question

On a fixed synthetic agent-workflow matrix, does adding provider-enforced
structured output improve protocol acceptance or evidence-contract satisfaction
compared with prompt output plus local validation?

## Definitions

**Protocol acceptance** means the local adapter can complete the bounded
provider interaction and record the required metadata without a refusal.

**Evidence-contract satisfaction** means an accepted trace passes the local
validator for the scenario's required classification, identifier, bounded
operation state, and cost/retry fields. This is the study's authority for
evidence quality; a provider accepting a response does not make the trace
acceptable by itself.

**Provider refusal** means the adapter could not accept the provider response
under the frozen interaction protocol. The refusal is retained as an outcome,
not retried until it disappears.

## Conditions

### Condition A: local validation

- Claude Sonnet 5.5.
- The frozen synthetic case matrix.
- The bounded native tool loop.
- Local parsing and evidence-contract validation.
- No provider-enforced structured-output format.

### Condition B: provider structured output

- Claude Sonnet 5.5.
- The identical synthetic case matrix.
- The same bounded native tool loop and cost ceiling.
- A provider-facing JSON Schema format.
- The same local parsing and evidence-contract validation.

The conditions were run separately. Their results are not pooled into one
condition, and the lower planning estimate in Condition B is not treated as a
cost improvement because the conditions had different refusal rates.

## Outcomes

The primary outcomes are:

1. protocol acceptance rate;
2. provider refusal rate;
3. evidence-contract satisfaction among accepted traces.

The secondary descriptive outcome is evidence-contract satisfaction over all
attempted cases, counting refusals as not satisfying the contract. This is
reported because a system that refuses a case has not produced usable evidence
for that case.

## Fixed controls

- 30 attempted cases in each condition.
- The same ten synthetic scenarios.
- Three replicates per scenario.
- The same bounded tool interaction and local validator.
- A five-dollar maximum planning ceiling per run.
- Metadata-only retention.
- No response-based reruns selected after inspecting a result.

The run is a paired design at the scenario/replicate level, but the pilot is
descriptive. It does not claim inferential significance from 30 observations or
from the unequal number of accepted traces.

## Planned replication

The next condition is a pre-registered second-model replication using the
adapter's approved Haiku identifier, `claude-haiku-5-5`:

- use the same 30-case matrix;
- keep the two output conditions unchanged;
- use `claude-haiku-5-5` for both arms;
- preserve the same cost ceiling, refusal handling, and local validator;
- report the result separately from the Sonnet pilot;
- do not modify the schema or prompts in response to the Sonnet result before
  the replication run.

The replication has a five-dollar planning ceiling per arm and a ten-dollar
combined planning ceiling. The two arms are still reported separately; the
combined ceiling is only a spending control.

The replication is intended to test whether the observed result is specific to
the model/provider configuration or persists across a second model. It is not
permission to claim cross-model generality by itself.

## Data boundary

The public study stores counts, statuses, refusal codes, stages, and cost
estimates only. It does not store model prompts, model responses, tool
arguments, private traces, or credentials. The detailed live-provider reports
remain local to the executable experiment repository.
