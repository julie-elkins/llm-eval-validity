# Should this agent go live? — one page

**Decision: not yet, and only one of the two blockers is about the agent.**

A Claude-powered customer-service agent was evaluated over 216 graded turns in a 24-configuration
factorial design. The original report's headline was a 0% wrong-answer rate in all 24
configurations. That is true, and it does not support a deployment decision. Re-analysed against
the standards a certification programme would apply, the same data says this:

| question | answer |
|---|---|
| Can it be deployed on this evidence? | **No.** One family fails on the evidence; the other cannot be certified at this sample size. |
| What can it safely do today? | Handles **77% of policy questions itself** when documents are current [67.7%, 84.4%], escalating the rest. All 74 of those it answered were correct, and the eval bounds its error rate on them at **4.9%**. Across every configuration: 79 answered, **79 correct**, bound 4.6%. |
| What blocks it? | **3 restricted-action violations in 19 scored turns** (lower bound 5.5%, tolerance 5%). A real defect, not a measurement artefact. |
| What would a bigger eval fix? | The policy standard. Zero errors in 79 answered turns proves "under 4.6%", not "under 2%". Demonstrating 2% needs about **189 answered turns**; 0.5% needs about **765**. |
| What does the value actually depend on? | **Document freshness, not model choice.** On superseded documents the agent correctly declines almost everything, and coverage falls from 77% to 5% — the automation benefit disappears while accuracy stays perfect. |

## Why the harness's own number would have shipped it

The harness reports one pooled failure rate: 3 failures across all 211 scored turns, or 1.4%,
which clears a 2% tolerance. It gets there two ways, and either alone is enough. It averages a
family with a 1-in-6 violation rate into a family with none — so a customer harmed by a
restricted action is treated as offset by correct answers about returns policy. And it tests a
point estimate rather than a confidence bound — so a small eval passes because it is small.
Judged per family and on the bound, as a certification programme would, both families fail.

## What to do, in order of what changes the decision

1. **Fix the restricted-action violations.** The only item here about the agent, and the only one
   a larger eval would not resolve.
2. **Grow the behaviour suite to ~73 turns.** Even with a perfect record, 19 turns can only ever
   bound the violation rate at 16.8% — three times its own tolerance. It is the smallest and
   highest-consequence part of the suite, which is backwards.
3. **Buy answered policy turns, not more configurations.** Only 79 of 192 policy turns were
   answered at all, so the effective sample is under half the nominal one. Nine of the 24
   configurations spent their entire sample establishing that stale documents produce
   abstentions.
4. **Stop reporting a pooled rate**, and stop reporting a pass rate. The deployable quantities
   are *share of volume automated* and *error rate not ruled out*.
5. **Treat the standard as monitoring, not a launch gate.** The correct answers already changed
   once when the policy documents changed.

## Two by-products worth having

**The automation economics have a break-even, and it is not about the model.** Automating beats
escalating every turn to a human until one incorrect policy statement costs more than about **20
unnecessary escalations** — using the eval's most pessimistic reading of its own error rate.
Coverage cancels out of that comparison; the lever that moves it is sample size, because sample
size sets the bound.

**The grading itself can be automated, and it was the weakest link.** The programmatic grader
that produced the original labels disagreed with the human auditor on 26 of 216 turns,
concentrated on two questions where a regex cannot see negation (54% and 58% agreement, against
≥96% elsewhere). An LLM judge run as a screen flags about 16% of turns for human reading and
caught all 23 of the grader's policy errors — though 23 for 23 is still consistent with missing
one error in seven, so it reduces the review burden rather than removing it. Total cost of the
judge validation: **$6.95**.

## What this does not establish

The reference standard is **one auditor's single pass** over all 216 turns, so there is no
human–human agreement ceiling: a judge that matches it matches one reader's judgement. A second
independent pass over 40–60 turns would settle it and is the first thing to add. Each question was
also asked once per configuration, so the agent's own run-to-run variance is not recoverable from
this data at all. And the two tolerances above are stipulated placeholders — a real standard would
come from whoever carries the consequence of a misstated policy.

---

Full analyses: [precision](precision.md) · [item analysis](item-analysis.md) ·
[judge validation](judge-validation.md) · [cut score](cut-score.md) ·
[methodology](methodology.md). Every figure above is regenerated from the vendored fixture by
`make docs`, and 135 tests pin the claims.
