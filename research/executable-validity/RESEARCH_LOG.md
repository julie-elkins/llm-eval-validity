# Research log

## 2026-11-20 — Define a layered evidence protocol

**Decided:** Build one follow-on protocol studying whether outcome-only review
can be improved by adding evidence provenance, executable verification, and
blinded human adjudication on the same matched cases.

**Instead of:** Starting a separate AI-and-relationships paper, writing another
generic benchmark checklist, or creating a new repository.

**Why:** The current research already contains evidence contracts,
response-quality review, reauthorization, and synthetic assessment validity.
The adjacent benchmark literature supplies checklists, tool-use environments,
and repeated-state measures, but the missing connection is a controlled
comparison of review layers and the false-positive decisions they prevent.

**Costs if wrong:** The study may still overlap with existing benchmark-validity
work, and a synthetic case matrix will limit external validity. The protocol
therefore requires explicit positioning, locked holdouts, human review, and
narrow claims before any execution.

**Decided by:** Julie Elkins, with Codex implementation support.

## 2026-11-20 — Keep the study provider-neutral

**Decided:** Make the offline protocol and analysis provider-neutral and treat
any live model run as a separately approved arm with its own cost ceiling and
frozen manifest.

**Instead of:** Building the research around one provider's evaluation API or
pooling provider results into a general model ranking.

**Why:** The research question concerns evidence layers, not vendor position,
and provider services, model identifiers, and platform behavior can change.
Provider neutrality preserves reproducibility and keeps the claim aligned with
the protocol.

**Costs if wrong:** A provider-specific implementation may be less convenient
for a pilot. That convenience is not worth making the research artifact
dependent on a changing external service.

**Decided by:** Julie Elkins, with Codex implementation support.
