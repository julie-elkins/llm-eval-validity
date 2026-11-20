# From Plausible to Defensible

## Layered evidence protocol for agent evaluation

## Status

**Protocol design only. No provider run or confirmatory result has been
completed.**

## Research question

Does adding evidence provenance, executable verification, and human adjudication
reduce false-positive evaluation decisions compared with outcome-only grading?

A false-positive evaluation decision is an approval that the available evidence
does not support.

## Why this study exists

Agent benchmarks can report a correct-looking outcome while leaving important
questions unanswered:

- Was the required evidence actually retrieved?
- Did the tool call use the correct permission and argument?
- Does the code or data support the reported result?
- Was uncertainty handled correctly?
- Did a reviewer mistake fluency for validity?

The existing research in this repository studies evidence contracts, response
quality, and reauthorization separately. This protocol connects those layers in
one matched comparison.

## Four review layers

Every layer receives the same case, task, tools, budget, and stopping rule.
Only the evidence available to the layer changes.

1. **Outcome-only review** — sees the task and final result and assigns the
   requested outcome.
2. **Evidence-aware review** — also sees approved evidence fields, provenance,
   revision identifiers, uncertainty signals, and bounded workflow metadata.
3. **Executable verification** — also runs deterministic checks for schema
   validity, claim-to-evidence alignment, replayable calculations, invariants,
   and negative controls.
4. **Blinded human adjudication** — an independent reviewer applies the rubric
   to the same evidence package without seeing the private reference decision
   or another reviewer's judgment.

The layers are cumulative for the primary comparison. Incremental comparisons
report what changes when each additional evidence layer is introduced.

## Core artifacts

- [Research question](RESEARCH_QUESTION.md)
- [Protocol](PROTOCOL.md)
- [Analysis plan](ANALYSIS_PLAN.md)
- [Related work](RELATED_WORK.md)
- [Research log](RESEARCH_LOG.md)

## Relationship to the repositories

- [Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness)
  owns the executable control checks.
- This repository owns the research protocol, frozen metadata, analysis, and
  claim limits.
- The design-guide repositories provide reusable evaluation and evidence
  patterns, but they do not supply results for this study.

## What the study will not claim

It will not claim that:

- executable checks prove scientific truth;
- human review is infallible;
- one benchmark represents production reliability;
- one provider or model is generally better;
- more agents are always better; or
- synthetic cases establish population-level or production outcomes.
