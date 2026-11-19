# Reproducibility appendix

## A. Frozen study boundary

The study compares prompt instructions plus local validation with
provider-enforced structured output plus the same local validation. The six
conditions, ten scenarios, three replicates per scenario, refusal handling,
cost ceilings, and evidence-contract definitions were frozen before the
reported interpretation.

The study is descriptive and synthetic. It does not estimate production failure
rates, rank providers, or measure user outcomes.

## B. Public artifacts

The public repository contains:

- `research/response-quality/PROTOCOL.md` — study design and controls;
- `research/response-quality/RESULTS.md` — frozen aggregate results;
- `research/response-quality/FROZEN_AGGREGATES.json` — machine-readable
  metadata-only counts;
- `research/response-quality/STATISTICAL_SUMMARY.md` — descriptive uncertainty
  intervals;
- `research/response-quality/PAIRED_ANALYSIS_SPEC.md` — guarded matched-outcome
  analysis contract;
- `research/response-quality/RELATED_WORK.md` — research positioning;
- validation and analysis code under `validity/`, `tools/`, and `tests/`.

## C. Uncertainty reporting

Reported proportions use 95% Wilson score intervals. The interval is a
bounded uncertainty range for a proportion and is reported to make the small
fixed matrix visible. It is not interpreted as a confidence statement about
future production traffic.

The study has three replicates per scenario. A future paired comparison must
resample complete scenarios rather than individual replicates. This preserves
the dependence among replicates from the same scenario family.

## D. Paired-analysis boundary

The provider arms use the same scenario and replicate identifiers, but the
public artifact intentionally omits private case-level outcomes. Aggregate
counts do not reveal which matched cases changed between conditions.

Therefore the current public report does not claim a paired effect estimate.
If the private metadata is recovered, the analysis must:

1. pair by scenario and replicate;
2. report wins, losses, and ties;
3. report paired percentage-point differences;
4. calculate scenario-clustered uncertainty intervals; and
5. retain the descriptive claim boundary.

No raw prompts, model responses, tool arguments, credentials, answer keys,
reviewer identities, or private traces are required in the public output.

## E. Reproduction command

From the repository root:

```bash
make response-quality-stats
```

The command is offline, reads only the frozen aggregate JSON, and writes the
statistical summary. It does not contact a provider or modify the frozen
results.
