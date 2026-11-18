# Human-Grounded Judge Calibration Study

This document turns the response-quality study's open calibration work into a
reproducible analysis contract. It does not claim that the required human labels
already exist.

## Decision to support

Decide whether a model-based judge is suitable for:

1. **screening** — routing cases to a human reviewer; or
2. **release** — acting as part of a release gate.

Screening and release are different decisions. A judge can be useful for finding
cases for human review without being trustworthy enough to approve a release.

## Required evidence

### Independent human reference

- Two independent human raters review the same held-out cases.
- Each rater works from the frozen rubric before seeing the other rater's labels.
- A third adjudicator resolves disagreements only after independent labels are
  recorded.
- The human-human ceiling is the agreement between the two independent raters.

### Judge agreement

- Compare the judge with each human rater separately.
- Report raw agreement and Cohen's kappa with the category marginals.
- Keep abstentions visible; do not turn an unavailable judge label into a pass.

### Judge repeatability

- Run the same judge and rubric at least three times on the same cases.
- Report pairwise agreement and the minimum/maximum range.
- A judge difference smaller than its own repeatability spread is not a reliable
  ranking signal.

### Rubric and bias probes

- Test redundant rubric criteria and remove criteria that count the same evidence
  twice.
- Swap candidate position to measure position bias.
- Hold the decision constant while varying answer verbosity to measure verbosity
  bias.
- Record abstention as an outcome with an explicit reason code.

## Decision rule

The analysis helper in `validity/calibration.py` returns:

- `screening_and_release_candidate` only when human-grounded agreement,
  repeatability, and abstention thresholds are all met;
- `screening_only` when judge-human agreement is acceptable but one or more
  release requirements remain open; or
- `not_ready` when judge-human agreement is below the declared threshold or no
  human-grounded comparison exists.

Thresholds must be declared before inspecting the result. The defaults in the
helper are teaching values, not universal production standards.

## Public-data boundary

The public repository may contain aggregate counts, synthetic examples, reason
codes, rubric versions, and analysis code. It must not contain reviewer
identities, contact information, completed forms, raw provider responses,
private prompts, credentials, or unpublished case content.

## What this proves

The study can distinguish a human-agreement ceiling, judge-human agreement,
repeatability, bias probes, and abstention before making a deployment claim.

## What this does not prove

A completed calibration study would not prove general model quality, production
safety, or agreement on every future task. It would support only the declared
rubric, case population, judge configuration, and decision boundary.
