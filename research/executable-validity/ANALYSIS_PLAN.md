# Analysis plan

## Analysis boundary

This plan is written before the new case matrix is executed. It separates
protocol behavior from claims about real systems.

The locked holdout is the primary analysis set. Development cases are excluded
from confirmatory comparisons. Robustness cases are reported separately.

## Primary comparison

Compare Layer A, outcome-only review, with Layer D, the full layered protocol,
on false-acceptance rate.

For each case, define:

```text
false_accept = 1 if layer decision == accept
                    and reference decision != accept
             = 0 otherwise
```

Report:

- numerator and denominator;
- exact proportion;
- Wilson 95% interval;
- paired case-level difference;
- McNemar's test for paired binary decisions when its assumptions are
  appropriate; and
- a clustered bootstrap by independence group.

A confidence interval is an uncertainty range around an estimate; it does not
turn synthetic cases into production or population evidence.

## Incremental comparisons

Report these comparisons separately:

1. Layer A versus Layer B: contribution of evidence provenance.
2. Layer B versus Layer C: contribution of executable verification.
3. Layer C versus Layer D: contribution of human adjudication.
4. Layer A versus Layer D: total layered-protocol difference.

The primary paper claim must not rely on a post-hoc choice among these
comparisons.

## Secondary analyses

For every layer, report:

- reference agreement;
- false rejection;
- false acceptance;
- supported-control acceptance;
- negative-control blocking;
- missing or refused outputs;
- review or execution time; and
- cost where applicable.

Report results by defect family and by split. Defect-family results are
descriptive unless the case count and pre-specified precision target justify an
inferential comparison.

## Human-review analysis

For two or more reviewers:

- report exact reviewer–reviewer agreement;
- report reviewer–reference agreement;
- report disagreement counts by field;
- use Cohen's kappa only when the category structure and prevalence make it
  interpretable;
- retain raw category counts and avoid presenting kappa as the only evidence;
- adjudicate disagreements after independent forms are locked; and
- report adjudicated decisions separately from original judgments.

If only one reviewer completes the packet, report a calibration observation and
do not claim human–human reliability.

## Missingness and refusal policy

Every case receives one status:

- completed;
- refused;
- incomplete; or
- invalid protocol output.

Refusals and incomplete runs are not silently dropped. The primary
all-attempt denominator counts them as not accepted. Accepted-only results are
secondary and labeled as such.

## Multiple comparisons

The four layer comparisons and defect-family analyses are not all primary
claims. The paper will identify one primary comparison before execution.
Secondary p-values, if reported, will be labeled exploratory and adjusted with a
pre-specified method such as Holm correction.

## Sensitivity analyses

Run only after the primary analysis is frozen:

- all-attempt versus accepted-only denominators;
- excluding one defect family at a time;
- independence-group cluster bootstrap;
- reviewer consensus versus individual judgments; and
- robustness-set results.

Sensitivity analyses may explain instability but must not replace the primary
result.

## Reporting limits

The final report must distinguish:

- observed protocol behavior;
- agreement with the synthetic reference;
- human reviewer agreement;
- executable property checks; and
- claims that require external validation.

The study cannot establish production reliability, causal scientific validity,
general model quality, or learner outcomes.
