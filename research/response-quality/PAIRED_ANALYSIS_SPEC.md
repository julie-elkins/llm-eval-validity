# Paired comparison analysis contract

## Purpose

The provider conditions used the same scenario and replicate identifiers. A
paired comparison would compare the two conditions on the same case rather
than treating them as unrelated samples.

The public repository does not contain the private case-level outcomes needed
to calculate that comparison. Aggregate counts cannot recover which individual
cases were accepted or satisfied the evidence contract.

This document defines the analysis that may be run if the private metadata is
available. It does not authorize reconstructing or publishing private traces.

## Required private input

The private input must contain one record for each matched case:

```json
{
  "model": "claude-sonnet-5-5",
  "scenario_id": "scenario-name",
  "replicate": 1,
  "prompt": {
    "accepted": true,
    "evidence_satisfied": false
  },
  "structured": {
    "accepted": false,
    "evidence_satisfied": false
  }
}
```

Only boolean outcomes and matched identifiers are needed. Raw prompts,
responses, tool arguments, credentials, and reviewer information must not be
included in the analysis output.

## Planned comparison

For each model and outcome:

1. Pair prompt and structured results by `scenario_id` and `replicate`.
2. Report paired wins, losses, and ties.
3. Report the paired percentage-point difference.
4. Use a scenario-clustered bootstrap interval, meaning whole scenarios are
   resampled so the three replicates from one scenario are not treated as
   independent evidence.
5. Keep the result descriptive; do not convert this pilot into a population
   significance claim.

The OpenAI conditions remain separate from the Claude conditions and are not
pooled into a provider ranking.

## Current status

The public aggregate artifact supports Wilson score intervals for each reported
proportion. The paired comparison is **not reported yet** because the
case-level private metadata has not been recovered in this workspace. This is
an intentional evidence boundary, not a missing calculation hidden from the
reader.
