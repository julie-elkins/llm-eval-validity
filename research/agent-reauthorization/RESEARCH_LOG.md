# Research log

This log records decisions made before results. It is part of the study record.

## 2026-10-23

### Decision: use the existing validity repository

- **Decided:** Store the paper scaffold and statistical analysis in
  `llm-eval-validity`.
- **Instead of:** Creating a new paper-only repository.
- **Why:** The repository already contains reproducible fixtures, validity analyses,
  reports, and limitations. Separating the paper from that evidence would make the
  argument easier to read but harder to verify.
- **Costs if wrong:** The repository gains a second study area and needs clear
  navigation.
- **Decided by:** Julie Elkins, following the project recommendation.

### Decision: begin with an offline synthetic pilot

- **Decided:** Phase 1 uses deterministic synthetic claim-change cases.
- **Instead of:** Starting with live model calls, private telemetry, or a human
  reviewer study.
- **Why:** The protocol must be replayable and its decision logic must be inspectable
  before provider variance or access constraints are introduced.
- **Costs if wrong:** The first results will have limited external validity, meaning
  they may not transfer to real organizations without later validation.
- **Decided by:** Julie Elkins, following the project recommendation.

### Decision: compare three conditions

- **Decided:** Compare pass/fail reporting, revision-aware evidence, and
  revision-aware evidence plus reauthorization.
- **Instead of:** Comparing only an ordinary report with the complete protocol.
- **Why:** The intermediate condition tests whether revision identity and invalidation
  explain the result, rather than attributing every improvement to the full
  organizational protocol.
- **Costs if wrong:** The pilot requires more fixtures and analysis.
- **Decided by:** Julie Elkins, following the project recommendation.

### Decision: freeze the protocol before implementation

- **Decided:** Write the question, hypotheses, cases, measures, exclusions, and
  stopping rule before generating pilot results.
- **Instead of:** Building a result-producing script first and documenting the method
  afterward.
- **Why:** Retrofitting a method after seeing results creates researcher degrees of
  freedom—the ability to change choices until the result looks favorable.
- **Costs if wrong:** Some early implementation choices may be discarded.
- **Decided by:** Julie Elkins, following the project recommendation.

### Decision: apply computational-research reporting controls

- **Decided:** Keep a public reporting checklist covering protocol order, artifact
  availability, environment, data boundary, statistical claims, limitations, ethics,
  and independent reproduction.
- **Instead of:** Treating a passing synthetic run as sufficient documentation for
  a research paper.
- **Why:** A reproducible study needs to show how the result was produced and where
  the result stops applying. Without that record, a clean run can be mistaken for
  production evidence.
- **Costs if wrong:** The paper carries a visible checklist and additional maintenance
  work when the robustness phase begins.
- **Decided by:** Julie Elkins, following the research-guideline review.

### Decision: bind the robustness result to merged main and reproduce from clean checkouts

- **Decided:** Record the harness merge commit, reproduce the robustness run from fresh
  clones, and compare the compact outcome fields against the checked-in fixture.
- **Instead of:** Treating the local feature branches or a byte-for-byte comparison
  between the detailed executable output and compact public fixture as sufficient.
- **Why:** A clean-checkout reproduction tests that the public merged artifacts work
  without local branch state, while the compact fixture intentionally omits
  content-like case-level detail.
- **Costs if wrong:** The study records two revisions and a disclosed environment
  difference, which adds maintenance but makes the evidence easier to audit.
- **Decided by:** Julie Elkins, following the research protocol.

### Decision: expand to a research-grade Phase 4 synthetic matrix

- **Decided:** Add 210 new cases with independent metadata variation, frozen
  development/robustness/locked-holdout splits, and a separate structured reference
  manifest.
- **Instead of:** Treating the 30-case matrix as sufficient empirical evidence or
  counting identifier-only permutations as independent observations.
- **Why:** A graduate-level presentation needs stronger coverage and clearer
  separation between development evidence and final evaluation. The expansion
  improves protocol validity while keeping the public artifact deterministic,
  offline, and metadata-only.
- **Costs if wrong:** The result is still synthetic, the manifest is still a study
  oracle, and external validity remains unestablished until an LLM-backed and/or
  human-reviewer phase is run.
- **Decided by:** Julie Elkins, with Codex implementation support.

### Decision: separate protocol validation from system validation

- **Decided:** Keep Phase 4 offline and add a later LLM-backed system phase with
  bounded tools, traces, an independent evaluator, and cost/latency controls.
- **Instead of:** Adding live model calls to the synthetic phase and treating a
  provider-dependent run as if it were a cleaner test of protocol mechanics.
- **Why:** The offline phase isolates the governance logic; the later system phase
  tests whether the logic survives model and tool behavior. Combining them would
  make failures harder to diagnose and reproducibility weaker.
- **Costs if wrong:** The research takes longer and requires a second protocol,
  model/version recording, repeat runs, and variance analysis.
- **Decided by:** Julie Elkins, with Codex implementation support.
