# From evaluation to reauthorization

This directory contains a multi-phase synthetic research paper and protocol for studying how teams
should decide whether an AI agent may continue operating after its workflow changes.

The research question is deliberately narrower than "are AI agents reliable?" It asks
whether evidence collected for one revision of a tool-using agent remains sufficient to
support the same release or operating decision after the system changes.

## Current status

**Phase 4 in progress:** the larger split-aware synthetic matrix is implemented and
validated. The paper is being revised to report phases 1--4 without presenting
synthetic evidence as production validation.

The research question, hypotheses, study conditions, measures, related-work boundary,
and reporting checklist are complete. The first deterministic pilot, held-out
robustness matrix, and Phase-4 split-aware matrix have run. A clean-checkout
reproduction of Phase 4 remains the next verification step.
The [results](RESULTS.md) report what those runs establish and what they cannot
establish.

## Documents

- [Research question and hypotheses](RESEARCH_QUESTION.md)
- [Phase-1 protocol](PROTOCOL.md)
- [Related work and positioning](RELATED_WORK.md)
- [Research log](RESEARCH_LOG.md)
- [Research reporting checklist](RESEARCH_CHECKLIST.md)
- [Pilot and Phase-4 results](RESULTS.md)
- [Research paper](paper.md)

## Repository boundaries

The paper and statistical analysis live here because this repository owns the validity
question: whether a measurement supports the decision made from it.

The synthetic workflow scenarios and operational controls belong in the
[Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness),
because that repository owns executable workflow evidence, negative controls, incident
handling, and release gates.

The two repositories will link to each other. Neither repository will copy the other's
canonical implementation.

## What the current pilot can establish

The current synthetic phases can establish whether the proposed protocol is executable, whether the
conditions produce distinguishable decisions on controlled synthetic changes, and which
measures are useful enough for an empirical system or reviewer study.

It cannot establish general production safety, model capability, or how every
organization should govern agents. Those would require broader systems, populations,
and validation. A future reviewer study could recruit volunteers through a public
call, but that would be a new phase with its own consent, privacy, sampling, and
agreement protocol.

## Running the existing study

The existing validity study remains unchanged:

```sh
make analyse
make test
```

The reauthorization pilot source lives in the Agent Assurance Harness. This repository
stores compact metadata-only results and validates their shape before the results are
used in the paper.

To validate the Phase-4 fixture directly:

```sh
python -m validity.reauthorization fixtures/reauthorization_phase4.json
```
