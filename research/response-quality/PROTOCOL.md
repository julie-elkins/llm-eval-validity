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

## Replication result

The pre-registered second-model replication used the adapter's approved Haiku
identifier, `claude-haiku-5-5`:

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

Both arms completed without exceeding their planning ceilings. The next
research phase is not another prompt or schema retuning pass; it is a broader
scenario or independent-review design chosen after this result is documented.

The replication is intended to test whether the observed result is specific to
the model/provider configuration or persists across a second model. It is not
permission to claim cross-model generality by itself.

## Cross-provider replication

The next pre-registered arm adds OpenAI as a second provider:

- OpenAI Responses API native function-call/result loop.
- The same ten synthetic scenarios and three replicates per scenario.
- The same three-turn ceiling and five-dollar planning ceiling per arm.
- The same local evidence validator and refusal policy.
- One baseline arm using prompt instructions plus local validation.
- One separate arm using provider-enforced JSON Schema plus local validation.
- The model identifier is fixed before the live run and recorded in its
  metadata-only report.
- No prompt, tool schema, or validator changes are allowed after seeing the
  OpenAI baseline.

The purpose is to separate a Claude-family observation from a
structured-output observation. The OpenAI result will remain separate from the
four Claude arms; it will not be pooled into a provider ranking or treated as
an estimate of general model quality.

### OpenAI baseline result

The OpenAI prompt-plus-local-validation arm used the preregistered `gpt-5.6`
identifier, the same 30-case matrix, the same three-turn ceiling, and the same
five-dollar planning ceiling:

- attempted: 30;
- accepted: 26;
- refused: 4;
- protocol acceptance: 86.7%;
- accepted traces satisfying the evidence contract: 15/26 (57.7%);
- evidence-contract satisfaction over all attempted cases: 15/30 (50.0%);
- planning estimate: $3.30 of $5.00.

All four refusals occurred after the provider response. The
`http-200-empty-context-retry` scenario refused in all three replicates, and
one `ambiguous-side-effect-retry` replicate also refused. The arm is frozen as
an incomplete but interpretable provider result. The OpenAI structured-output
arm remains a separate, not-yet-run condition.

### OpenAI structured-output result

The OpenAI provider-structured-output arm used the same preregistered
`gpt-5.6` identifier, 30-case matrix, three-turn ceiling, five-dollar
planning ceiling, and local evidence validator:

- attempted: 30;
- accepted: 27;
- refused: 3;
- protocol acceptance: 90.0%;
- accepted traces satisfying the evidence contract: 14/27 (51.9%);
- evidence-contract satisfaction over all attempted cases: 14/30 (46.7%);
- planning estimate: $3.25 of $5.00.

All three refusals were `tool_loop_turn_limit_exceeded` stop refusals for the
`http-200-empty-context-retry` scenario. Compared with the OpenAI baseline,
structured output increased protocol acceptance by 3.3 percentage points, but
decreased evidence-contract satisfaction among accepted traces by 5.8 points
and over all attempted cases by 3.3 points. This is a descriptive,
configuration-specific comparison, not a provider ranking or a general claim.

## Data boundary

The public study stores counts, statuses, refusal codes, stages, and cost
estimates only. It does not store model prompts, model responses, tool
arguments, private traces, or credentials. The detailed live-provider reports
remain local to the executable experiment repository.
