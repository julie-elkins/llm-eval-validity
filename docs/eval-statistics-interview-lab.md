# Eval Statistics Interview Lab

This offline lab practices statistics that appear repeatedly in evaluation-engineer
interviews. It uses synthetic observations, so it needs no API key, network connection,
or model run.

Run it with:

```bash
uv run python -m examples.eval_statistics_interview_lab
```

## What it demonstrates

- **Paired bootstrap** resamples matched cases, preserving the fact that both systems saw
  the same tasks.
- **McNemar's test** is a paired test for binary outcomes. It asks whether two systems
  differ on cases where exactly one passes.
- **Cluster bootstrap** resamples independent groups, such as users or task families,
  rather than treating correlated turns as independent.
- **Multiple comparisons** shows why a family of tests needs a declared correction. The
  example uses Bonferroni, which divides the decision threshold across tests.
- **Confidence intervals and sample size** reuse the Wilson and planning utilities already
  in this repository. A point estimate is what happened in the sample; the interval is
  what the sample can support about the population.
- **ROC-AUC versus PR-AUC** shows that ranking all negatives well is not the same as
  finding a rare positive class. ROC-AUC is the probability a positive ranks above a
  negative; PR-AUC focuses on precision and recall for the positive class.
- **pass@k versus pass^k** separates “at least one of k attempts succeeds” from “all k
  attempts succeed.”
- **Cost per solved task** refuses to report a number when no task was solved, because
  dividing spend by zero would create a misleading metric.

## Interview prompts

1. Why is a paired bootstrap preferable when the same cases are evaluated by both systems?
2. Why does McNemar's test ignore concordant pairs?
3. What dependence does a cluster bootstrap preserve?
4. When would you prefer PR-AUC to ROC-AUC?
5. Why can pass@k increase while pass^k decreases?
6. What decision would you make if cost per solved task is undefined?

## What this proves

The code makes calculation choices executable, deterministic, and testable on small
examples. It demonstrates statistical reasoning for evaluation design.

## What this does not prove

The synthetic examples do not establish model rankings, production quality, or a universal
sample-size rule. A real study must declare the unit of analysis, dependence structure,
decision threshold, multiple-testing family, and cost accounting before inspecting results.
