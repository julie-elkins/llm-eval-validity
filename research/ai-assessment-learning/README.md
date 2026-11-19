# From Correct Answers to Learning Evidence

## Study status

Phase 1 synthetic-only protocol, expanded to a frozen 30-case matrix. The
human-participant validation phase is deferred pending an ethics determination.

## Research question

Can an AI-assisted assessment workflow distinguish fluent task performance from
evidence of independent learning?

The eventual human-validation phase treats **independent transfer
performance**—the ability to solve a matched problem without AI support—as the
primary observable criterion. The current synthetic phase uses controlled
transfer dispositions and does not claim to observe real learning.

## Why this study exists

The companion research in this repository asks whether an AI workflow's result is
supported by the evidence available to it. This study applies the same discipline
to educational assessment:

> Does the assessment evidence support the claim that a learner understands the
> target skill, or does it only show that the learner and an AI system produced a
> plausible answer together?

Julie began this line of work through professional technical assessment review.
That experience motivates the question but supplies no private exam content,
answer keys, reviewer identities, or internal data to this public study.

## Planned design

### Current synthetic phase

1. Load public synthetic task metadata and private expected dispositions.
2. Generate controlled assessment traces with planted evidence failures.
3. Score each trace under final-answer-only and evidence-aware views.
4. Compare both views with the synthetic reference disposition.
5. Report failure detection, disagreement, and missing evidence.

The current 30-case metadata-only fixture is executable offline:

```bash
make run-synthetic-assessment
```

The runner reads a private reference disposition and writes its summary to the
private workspace. The public case file contains only synthetic evaluator
dispositions, replicate metadata, and reason codes; it contains no learner
answers, answer key, or participant data.

### Future human-validation phase

After an appropriate ethics determination, an adult participant may complete a
bounded AI-assisted task and a matched transfer task without AI assistance.

The current phase is not designed to establish a population-wide effect or
prove that AI improves learning.

## What this study measures

- final-answer correctness;
- explanation or justification quality;
- evidence alignment;
- verification and uncertainty handling;
- confidence calibration, meaning whether confidence tracks correctness;
- synthetic transfer dispositions;
- reviewer agreement and disagreement;
- missing, contradictory, or unsupported evidence.

## What this study does not claim

- It does not claim that AI assistance produces durable learning.
- It does not treat a fluent explanation as proof of comprehension.
- It does not use private certification material.
- It does not rank AI systems from a small exploratory pilot.
- It does not replace educational judgment, instructor judgment, or formal
  assessment validation.

## Repository map

- [RESEARCH_QUESTION.md](RESEARCH_QUESTION.md) — scope and claims.
- [PROTOCOL.md](PROTOCOL.md) — pre-execution study protocol.
- [SYNTHETIC_PHASE_PROTOCOL.md](SYNTHETIC_PHASE_PROTOCOL.md) — current
  non-participant protocol.
- [SYNTHETIC_ANALYSIS_PLAN.md](SYNTHETIC_ANALYSIS_PLAN.md) — current analysis
  plan.
- [PROTOCOL_MANIFEST.json](PROTOCOL_MANIFEST.json) — machine-readable protocol
  boundary.
- [tasks/manifest.json](tasks/manifest.json) — public metadata-only task
  definitions.
- [synthetic_cases.json](synthetic_cases.json) — 30-case metadata-only
  synthetic execution fixture.
- [SYNTHETIC_RESULTS.md](SYNTHETIC_RESULTS.md) — aggregate 30-case synthetic
  result and claim boundary.
- [ABSTRACT_SUBMISSION.md](ABSTRACT_SUBMISSION.md) — draft abstract for the
  Springer special collection.
- [paper.md](paper.md) — full research manuscript draft.
- [SUBMISSION_CHECKLIST.md](SUBMISSION_CHECKLIST.md) — deadline and release
  gates.
- `make run-synthetic-assessment` — offline synthetic comparison; the summary
  remains private.
- [SYNTHETIC_TASK_SPEC.md](SYNTHETIC_TASK_SPEC.md) — public task requirements.
- [EVIDENCE_RUBRIC.md](EVIDENCE_RUBRIC.md) — evaluator contract.
- [ETHICS_AND_DATA_BOUNDARY.md](ETHICS_AND_DATA_BOUNDARY.md) — participant and
  privacy boundary.
- [ANALYSIS_PLAN.md](ANALYSIS_PLAN.md) — paired outcomes and missing-data rules.
- [PARTICIPANT_INFORMATION_AND_CONSENT_DRAFT.md](PARTICIPANT_INFORMATION_AND_CONSENT_DRAFT.md)
  — draft participant material.
- [TASK_FORMS_RELEASE_POLICY.md](TASK_FORMS_RELEASE_POLICY.md) — why task
  wording stays private before the pilot.
- [RELATED_WORK.md](RELATED_WORK.md) — literature and research gap.
- [PAPER_OUTLINE.md](PAPER_OUTLINE.md) — paper structure.
- [RESEARCH_LOG.md](RESEARCH_LOG.md) — dated decisions and protocol changes.

## Current gate

No participant recruitment or live provider run should begin. The current phase
is offline and synthetic. The 30-case expansion is a controlled repetition of
seven failure classes, not a sample of 30 learners.

The future human-validation phase must not begin until:

1. the protocol is reviewed for ethics and consent requirements;
2. the task set and transfer forms are frozen;
3. the primary outcome and analysis plan are locked; and
4. an institution or qualified review body determines whether the pilot requires
   institutional review, an exemption, or another approval route.

The task boundary can be checked offline:

```bash
make validate-assessment-tasks
```

This validates task families, matched-form identifiers, negative-control
coverage, and the absence of answer-key or participant fields. It does not
execute a learning study or collect human data.

The participant-facing task forms are held in a private local study packet until
the pilot is complete. Releasing them before the pilot could expose the transfer
tasks and invalidate the learning inference.
