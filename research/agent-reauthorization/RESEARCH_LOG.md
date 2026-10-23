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
