# Research question

## Primary question

On a fixed agent-evaluation case matrix, does adding evidence provenance,
executable verification, and blinded human adjudication reduce false-positive
evaluation decisions compared with outcome-only grading?

## Definitions

**Outcome-only grading** means deciding from the task and final result without
requiring the supporting evidence path.

**Evidence provenance** means the recorded origin, revision, and relationship of
an evidence item to the claim it is being used to support.

**Executable verification** means deterministic code checks that can replay,
validate, or falsify a stated property of the result. It does not establish
that the research question was well chosen or that the interpretation is
causally justified.

**Blinded human adjudication** means an independent reviewer makes a judgment
without seeing the private reference decision or another reviewer's answer.

## Primary estimand

The primary estimand is the difference in false-acceptance rate between:

```text
outcome-only review
versus
the full layered protocol
```

on the locked holdout set.

The estimand is descriptive for the synthetic study. It is not a population
parameter and does not generalize to production systems without external
validation.

## Secondary questions

1. How much does evidence-aware review change decisions beyond outcome-only
   review?
2. How much does executable verification change decisions beyond evidence-aware
   review?
3. How much does blinded human adjudication change decisions beyond automated
   checks?
4. Which defect classes remain difficult after all four layers?
5. What time, cost, and refusal burden does each layer add?
6. How often do human reviewers disagree with one another or with the
   pre-specified reference disposition?

## Hypotheses

**H1:** The full layered protocol has a lower false-acceptance rate than
outcome-only review on the locked holdout set.

**H2:** Evidence-aware review catches more unsupported or stale claims than
outcome-only review.

**H3:** Executable verification catches defects that remain plausible under
textual and metadata review.

**H4:** Human adjudication identifies residual ambiguity that automated checks
cannot safely resolve.

These are protocol hypotheses, not claims that the results are already known.
