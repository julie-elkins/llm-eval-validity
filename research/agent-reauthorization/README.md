# From evaluation to reauthorization

This directory contains a working paper and pilot protocol for studying how teams
should decide whether an AI agent may continue operating after its workflow changes.

The research question is deliberately narrower than "are AI agents reliable?" It asks
whether evidence collected for one revision of a tool-using agent remains sufficient to
support the same release or operating decision after the system changes.

## Current status

**Phase 2: deterministic pilot complete.**

The research question, hypotheses, study conditions, measures, related-work boundary,
and manuscript structure are written. The first deterministic pilot has now run over
the fixed synthetic case set. The [results](RESULTS.md) report what that run establishes
and what it cannot establish.

## Documents

- [Research question and hypotheses](RESEARCH_QUESTION.md)
- [Phase-1 protocol](PROTOCOL.md)
- [Related work and positioning](RELATED_WORK.md)
- [Research log](RESEARCH_LOG.md)
- [Research reporting checklist](RESEARCH_CHECKLIST.md)
- [Pilot results](RESULTS.md)
- [Working paper](paper.md)

## Repository boundaries

The paper and statistical analysis live here because this repository owns the validity
question: whether a measurement supports the decision made from it.

The synthetic workflow scenarios and operational controls belong in the
[Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness),
because that repository owns executable workflow evidence, negative controls, incident
handling, and release gates.

The two repositories will link to each other. Neither repository will copy the other's
canonical implementation.

## What phase 1 can establish

Phase 1 can establish whether the proposed protocol is executable, whether the
conditions produce distinguishable decisions on controlled synthetic changes, and which
measures are useful enough for a larger study.

It cannot establish general production safety, model capability, or how every
organization should govern agents. Those would require broader systems, populations,
and validation.

## Running the existing study

The existing validity study remains unchanged:

```sh
make analyse
make test
```

The reauthorization pilot source lives in the Agent Assurance Harness. This repository
stores the compact metadata-only result and validates its shape before the result is
used in the paper.
