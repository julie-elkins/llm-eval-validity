# Design decisions

This file records the choices that shape the study. It is intentionally separate from
the numerical results: a result says what the fixture produced, while this file says why
the study was designed to make that result interpretable.

The structure follows the
[decision-reasoning template](https://github.com/julie-elkins/agent-systems-design-guide/blob/main/DESIGN_DECISION_TEMPLATE.md):
problem, decision, alternative, reason, implementation, verification, production
implication, and limit.

## 1. Test validity before trusting the score

- **Problem:** A pass rate can be precise and still measure the wrong thing.
- **Decision:** Begin with validity, reliability, sampling, stratification, and
  repeatability before treating a score as release evidence.
- **Instead of:** Ranking models or prompts from the headline pass rate first.
- **Why:** A trustworthy decision needs an instrument that measures the intended
  behaviour with enough evidence. Improving a score from an invalid instrument only
  makes the wrong conclusion look more confident.
- **Official guidance considered:** The study borrows the structure of certification
  measurement practice and states where that borrowing stops applying to AI systems.
- **Implementation:** `validity/precision.py`, `validity/reliability.py`,
  `validity/cutscore.py`, and `validity/discrimination.py` are separate analyses, and
  `docs/methodology.md` explains the transfer and its boundaries.
- **Verification:** `make analyse` reproduces the offline analyses from the checked-in
  fixture; `make test` checks the calculations and fixture invariants.
- **Costs if wrong:** A weak or invalid eval can authorize a deployment, rollback, or
  model choice on evidence that does not support the decision.
- **What this does not prove:** It does not prove that the evaluated agent is safe or
  accurate in every production context.

## 2. Preserve both the original and audited labels

- **Problem:** Replacing the original grader output with corrected labels would hide
  what the instrument actually did.
- **Decision:** Keep the programmatic labels, human audit labels, source provenance, and
  disagreement causes together in the fixture.
- **Instead of:** Publishing only the post-audit labels or silently correcting the source
  run.
- **Why:** The gap between the labels is the object of the judge-validation analysis.
  Deleting one side would remove the evidence needed to measure grader error.
- **Implementation:** `validity/fixture.py` validates the fixture and the checked-in
  JSON preserves both label sets and their provenance.
- **Verification:** Fixture tests fail if required fields drift or the disagreement
  record closes unexpectedly.
- **Costs if wrong:** The study could report agreement with a cleaned-up answer instead
  of measuring whether the original evaluator was trustworthy.
- **What this does not prove:** A one-person audit is not a complete human reference
  standard; that limitation remains explicit in the README.

## 3. Declare tolerances before inspecting the result

- **Problem:** Choosing an acceptable error rate after seeing the scores turns a
  deployment gate into a justification for a preferred outcome.
- **Decision:** Declare the policy and behaviour tolerances in the methodology and
  evaluate interval bounds against them.
- **Instead of:** Passing on a point estimate or tuning the threshold after the analysis.
- **Why:** The bound expresses what the data can support, not just what happened in this
  small sample.
- **Implementation:** `validity/cutscore.py` reports the point estimate, uncertainty
  interval, and the decision against the stated tolerance.
- **Verification:** Cut-score tests cover both observed failures and perfect-but-
  underpowered samples.
- **Costs if wrong:** A green result can conceal an unacceptably high true error rate.
- **What this does not prove:** The tolerances are defensible study assumptions, not
  business-owner standard setting for every deployment.

## 4. Stratify by consequence and binding constraint

- **Problem:** A pooled result can hide a failing high-consequence family or attribute
  a document failure to a model or prompt.
- **Decision:** Report pooled and stratified results, with the reason for each stratum.
- **Instead of:** Treating the aggregate rate as the only answer because it is simpler.
- **Why:** The production decision is made per failure consequence and operating
  condition, not for an imaginary average turn.
- **Implementation:** The analyses split by corpus, policy family, and configuration
  where the design supports it.
- **Verification:** The reports retain both views and the methodology explains when
  stratification reduces the available sample.
- **Costs if wrong:** A system can pass overall while failing the family that matters
  most.
- **What this does not prove:** Small strata may be too wide to rank systems finely;
  they support boundary decisions better than precise league tables.

## 5. Measure repeatability as its own property

- **Problem:** A difference between two judges or configurations is not useful if it is
  smaller than the same instrument's run-to-run spread.
- **Decision:** Repeat the judge comparison and report within-judge variation alongside
  between-judge differences.
- **Instead of:** Comparing one run from each judge and calling the larger score a
  winner.
- **Why:** Without repeatability, the apparent winner may be sampling noise.
- **Implementation:** `validity/reliability.py` computes agreement across repeated runs
  and reports the range rather than only one coefficient.
- **Verification:** Reliability tests cover repeated-run aggregation and the degenerate
  case where a single category makes kappa uninformative.
- **Costs if wrong:** Teams can switch models or prompts based on noise, adding cost
  without improving the deployed system.
- **What this does not prove:** Repeatability of a recorded judge run does not establish
  live-provider stability under every future prompt or model version.

## 6. Keep live judging bounded and optional

- **Problem:** A reproducible study becomes hard to rerun if the default path needs
  credentials, network access, or an uncontrolled spend.
- **Decision:** Make the offline fixture the required path and make live judge validation
  an explicit, dry-run-first optional stage.
- **Instead of:** Calling a provider during tests or requiring a live API for the basic
  learning path.
- **Why:** Readers need to reproduce the reasoning before they incur cost or introduce
  provider variability.
- **Implementation:** `make analyse` is offline; `make judge` prints the planned call
  count and estimated spend before `--go`, and supports resumable runs.
- **Verification:** Tests and documentation keep the two paths separate.
- **Costs if wrong:** A documentation reader could accidentally spend money or mistake a
  provider result for a deterministic repository result.
- **What this does not prove:** Offline reproducibility does not establish live model
  quality.

## Teaching path

The repository is the measurement step after the
[Claude Architect Lab](https://github.com/julie-elkins/claude-architect-lab) and the
[Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness).
The sequence teaches a production habit: build a workflow, check its evidence boundary,
then check whether the measurement itself can support the release decision.
