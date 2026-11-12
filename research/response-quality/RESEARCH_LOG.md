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

## 2026-11-12 -- prepare the waiting-period analysis path

### Decision: prepare review reconciliation without changing the frozen study

- **Decided:** Add a public-safe version-2 review analysis and adjudication
  plan, a blank private-tracker template, and explicit paper/checklist
  language for the intake and completion gates.
- **Instead of:** Rerunning provider arms, changing the v2 rubric while
  volunteers are reviewing, publishing reviewer forms, or treating a received
  form as analyzed evidence immediately.
- **Why:** The next risk is operational ambiguity: without a defined intake
  gate, reviewer-to-reviewer comparison can mix packet versions, incomplete
  forms, or unverified provenance. Preparing the analysis path now lets the
  study remain frozen while making the later comparison reproducible.
- **Costs if wrong:** The public repository gains process documentation before
  the final v2 sample is known, and the review phase may still end as a
  one-reviewer calibration pilot if a second eligible reviewer does not
  complete the same cases.
- **Verification:** The six provider conditions and their reported counts are
  unchanged; the public files contain no reviewer identities, completed forms,
  raw case content, private traces, or answer key.
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

## 2026-10-24 -- replication result

### Decision: treat the repeated acceptance loss as a replicated boundary result

- **Decided:** Record the Haiku result as a completed within-provider
  replication. Structured output lowered acceptance in both model
  configurations: 20.0 percentage points for Sonnet and 30.0 for Haiku.
- **Instead of:** Pooling the four arms, declaring structured output generally
  harmful, or rerunning until the refusal rate improved.
- **Why:** The repeated direction supports a narrower claim about this adapter
  and treatment, while the different magnitudes show why the study cannot
  claim provider-independent generality from two Claude models.
- **Costs if wrong:** The next study must add a broader scenario matrix or a
  second provider before making a general structured-output claim.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-10-24 -- cross-provider replication

### Decision: add OpenAI as a separate provider arm

- **Decided:** Implement an OpenAI Responses API adapter with native
  function-call/result sequencing, then run the same 30-case local-validation
  and provider-structured-output arms.
- **Instead of:** Reusing the one-request OpenAI parser, pooling OpenAI with
  Claude before checking protocol differences, or changing the scenarios after
  observing the Claude results.
- **Why:** OpenAI's native agent interaction requires a bounded multi-turn
  exchange when a function call occurs. A real cross-provider replication must
  compare equivalent tool-loop semantics, not just send the same final JSON
  prompt to two providers. Keeping the scenario matrix and local validator
  fixed isolates the provider/protocol boundary.
- **Costs if wrong:** The adapter adds provider-specific code and the study
  still may produce incomplete runs. The result will remain descriptive and
  separate rather than being used to claim universal structured-output
  behaviour.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: preregister the OpenAI model and two-arm budget

- **Decided:** Use the default `gpt-5.6` identifier unless the local OpenAI
  account requires an explicitly documented override; run 30 cases per arm
  with a five-dollar planning ceiling per arm and no response-based reruns.
- **Instead of:** Picking a model after inspecting the OpenAI smoke result,
  increasing the ceiling when refusals appear, or tuning schemas between arms.
- **Why:** Fixing the model, matrix, validator, and spending rule before the
  live run preserves the comparison and makes refusals part of the result.
- **Costs if wrong:** The chosen model may be unavailable to the account or
  the two arms may be incomplete; the command supports an explicit model
  override, but the chosen value must be recorded before execution.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-10-24 -- OpenAI baseline result

### Decision: freeze the incomplete OpenAI local-validation arm

- **Decided:** Freeze the OpenAI prompt-plus-local-validation pilot as an
  incomplete but interpretable cross-provider arm: 26 accepted traces, 4
  after-response refusals, 15 accepted traces satisfying the evidence
  contract, 11 accepted traces failing it, and a $3.30 planning estimate
  against the $5 ceiling.
- **Instead of:** Raising the three-turn ceiling, adding retries, retuning the
  prompt after seeing the refusal pattern, or rerunning only the refused
  cases.
- **Why:** The arm completed all 30 planned attempts under the preregistered
  interaction contract. The refusal pattern is part of protocol acceptance,
  and changing the ceiling or retry policy after the result would make this
  arm incomparable with the frozen Claude conditions.
- **Costs if wrong:** The `http-200-empty-context-retry` scenario refused in
  all three replicates, and one `ambiguous-side-effect-retry` replicate also
  refused. The result may therefore reflect provider/adapter compatibility
  as well as model behavior; the limitation must remain explicit.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: freeze the OpenAI two-arm comparison

- **Decided:** Freeze the OpenAI comparison with the baseline and
  provider-structured-output arms reported separately. The structured arm
  accepted 27/30 traces, with 14/27 accepted traces satisfying the evidence
  contract and 14/30 satisfying it over all attempts.
- **Instead of:** Raising the three-turn ceiling, rerunning the retry
  scenario, or claiming that the small acceptance increase proves structured
  output is better.
- **Why:** Provider-enforced structure improved OpenAI protocol acceptance
  from 86.7% to 90.0%, but reduced evidence-contract satisfaction among
  accepted traces from 57.7% to 51.9% and over all attempts from 50.0% to
  46.7%. The end-to-end usable-evidence outcome did not improve.
- **Costs if wrong:** The OpenAI comparison remains specific to this model,
  schema, prompt, tool loop, and synthetic matrix. The result cannot support a
  general claim about structured output or model quality.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-10-24 -- independent reference review

### Decision: recruit independent reviewers before broadening the scenario matrix

- **Decided:** Prepare a synthetic-only independent reference review and
  recruit two volunteers when possible before adding more scenarios.
- **Instead of:** Expanding the matrix first, treating the local evidence
  contract as ground truth, or asking reviewers to endorse the frozen result.
- **Why:** The next research risk is construct validity: whether an
  independently applied rubric agrees with the local evidence decision. More
  cases would increase breadth without testing whether the measurement itself
  is defensible.
- **Costs if wrong:** The review requires a separate supervised local packet
  because the frozen provider runs intentionally discarded raw responses.
  Recruitment may take time, and the review will produce calibration evidence
  rather than a production-quality claim.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-11-02 -- close v1 calibration and keep v2 open

### Decision: use the completed v1 reviews to justify the v2 rubric, not to validate v1

- **Decided:** Close the v1 calibration phase after three independent
  reviewer forms and continue the separately versioned v2 calibration round.
- **Instead of:** Pooling v1 and v2 judgments, publishing reviewer identities
  or completed forms, treating the AI-assisted form as independent evidence,
  or changing the frozen provider conditions.
- **Why:** The v1 reviews consistently showed that the top-level
  classification question was easier to apply than the generic
  bounded-workflow field. They also exposed unclear scope around required
  identifiers and the need for explicit `not applicable` handling.
- **Costs if wrong:** Keeping v2 open delays finalization, but freezing it
  after one provisional v2 form would overstate the strength of the
  calibration evidence.
- **Public boundary:** The repository records aggregate calibration status and
  limitations only. Reviewer identities, completed forms, raw responses, and
  the private answer key remain local.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-11-03 -- paper-readiness consistency pass

### Decision: correct settled documentation drift without changing study results

- **Decided:** Align the public README, protocol, reporting checklist, and
  research record with the six already-frozen provider conditions and the
  current V2 reviewer status.
- **Instead of:** Starting another provider run, expanding the scenario matrix,
  or treating pending reviewer responses as completed evidence.
- **Why:** The numerical results were already frozen and reproducible, but
  several descriptions still said that only four Claude conditions or an
  OpenAI baseline existed, and the protocol still described the OpenAI
  structured-output arm as not yet run. A reader could therefore misunderstand
  both the scope of the study and what remains open.
- **Costs if wrong:** Documentation-only corrections do not add experimental
  evidence; a future paper revision must still incorporate confirmed V2
  calibration results before describing the revised rubric as independently
  validated.
- **Verification:** Offline analyses, the full test suite, and whitespace checks
  pass before and after the documentation changes.
- **Current state:** Six provider conditions are frozen. V1 human calibration
  is closed. V2 calibration remains open while additional independent feedback
  is collected.
- **Next action:** Continue reviewer reminders outside the repository. When
  confirmed independent V2 forms arrive, compare them with the private key and
  update only the aggregate public calibration status.
- **Decided by:** Julie Elkins, with Codex implementation support.

## 2026-11-03 -- record Matthew review provenance conservatively

### Decision: record the reviewer report without changing aggregate results

- **Decided:** Record that one additional V2 review was returned, that the
  reviewer reported completing it without AI assistance, and that the
  return-email date is treated as the completion date. Keep the V2 round open
  until the private artifact and packet record are reconciled.
- **Instead of:** Treating the self-report as independently verified,
  publishing the reviewer identity or completed form, or adding the review to
  agreement statistics before comparing it with the private answer key.
- **Why:** Reviewer provenance—the record of when and under what stated
  conditions a review was produced—supports transparent methods, but it does
  not establish independent behavior by itself. The paper must separate
  received feedback from analyzed calibration evidence.
- **Costs if wrong:** The public paper temporarily reports an open calibration
  phase even though a review has arrived. That is less convenient, but it
  avoids overstating validation if the private packet metadata and reviewer
  communication do not match.
- **Public boundary:** No reviewer name, completed form, raw case content, or
  answer key is published.
- **Decided by:** Julie Elkins, with Codex implementation support.
