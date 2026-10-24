# Research log

This log records decisions made before the next result is generated.

## 2026-10-24

### Decision: preserve the live-provider comparison as a separate study

- **Decided:** Record the Claude Sonnet structured-output comparison under
  `research/response-quality/`.
- **Instead of:** Adding the result to the reauthorization paper as another
  phase of the same experiment.
- **Why:** The reauthorization paper studies whether evidence remains valid after
  a workflow revision. This comparison studies whether a provider output
  constraint changes protocol acceptance and evidence-contract satisfaction.
  Combining them would make the causal question and the evidence boundary
  unclear to a reviewer.
- **Costs if wrong:** The repository now has a second research directory and
  needs explicit navigation between the studies.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: report both accepted-trace and all-attempt denominators

- **Decided:** Report evidence-contract satisfaction among accepted traces and
  over all attempted cases.
- **Instead of:** Reporting only the accepted-trace percentage, which is the
  cleaner-looking denominator.
- **Why:** A refusal produces no usable evidence. Reporting only accepted traces
  would hide the fact that Condition B rejected more cases before the local
  validator could assess them.
- **Costs if wrong:** The all-attempt measure is conservative and mixes
  protocol failure with evidence failure, so the paper must label the two
  outcomes separately.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: freeze before second-model replication

- **Decided:** Treat the Sonnet baseline and structured-output arm as frozen and
  pre-register the next second-model run before spending more provider credits.
- **Instead of:** Retuning the schema or prompts until the structured arm has a
  higher acceptance rate.
- **Why:** Post-result tuning would turn the comparison into a search over
  configurations and would hide the observed refusal behavior. A replication is
  more informative than polishing a result that already has a clear limitation.
- **Costs if wrong:** The current schema may not be the best practical schema,
  but that is a separate engineering question from whether this frozen
  intervention improved the pilot outcome.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: preregister the Haiku replication

- **Decided:** Run the same 30-case matrix with `claude-haiku-5-5` in two
  separate arms: local validation and provider structured output. Set a
  five-dollar planning ceiling per arm and a ten-dollar combined ceiling.
- **Instead of:** Selecting a second model after seeing which Sonnet result
  would be easiest to explain, or changing the schema between arms.
- **Why:** A second model tests whether the Sonnet result is configuration
  specific. Holding the matrix, adapter, schema, validator, and refusal policy
  constant makes the replication interpretable instead of turning it into a
  new tuning exercise.
- **Costs if wrong:** The replication can spend up to ten dollars and may
  produce another incomplete result. That is an expected research outcome, not
  a reason to rerun until the output is clean.
- **Decided by:** Julie Elkins, with Codex implementation support.
