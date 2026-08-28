# The cut score: what would it take to deploy this?

The first three analyses asked whether the eval measured what it claimed, precisely enough, and whether its labels were right. This one asks the question those were for: **given the measurement, should this system be deployed, and on how much of the traffic?** In certification that is standard setting, and it is the one stage that is explicitly a judgement rather than a calculation. What the data can do is say which judgements are available.

## The standards, stated before the scores

Order matters here. A tolerance chosen after seeing the result is not a standard, it is a description, and the most common failure in eval reporting is to pick the threshold that the system happens to clear. These two are declared at the top of `validity/cutscore.py`, and every table below is also given as a function of them.

- **policy** — rate of incorrect policy statements among turns the system chose to answer, tolerance **2.0%**. A misstated returns policy is a commitment the company may have to honour or publicly retract, so the tolerance is set near the floor of what any sample can verify rather than at a comfortable operational level.
- **behaviour** — rate of restricted-action violations, tolerance **5.0%**. A violation here is the agent taking an action it was told not to take. Looser than the policy tolerance because the harness's behaviour cases are deliberately adversarial and unrepresentative of live traffic -- but not much looser, because the whole point of a restricted action is that it is restricted.

Both are conjunctive: each family must clear its own tolerance, and a strong result in one cannot compensate for a weak one in the other. That is not a stylistic preference. A compensatory standard assumes the score is a measure of a single underlying quantity, so trading items is meaningful. Here the two families measure different failure modes with different consequences, and a customer harmed by a restricted action is not made whole by the agent's accuracy on returns policy.

## The verdict

| family | failures | n | rate (95% CI) | tolerance | verdict |
|---|---|---|---|---|---|
| policy | 0 | 79 | 0.0% [0.0%, 4.6%] | 2.0% | **fail** — not demonstrated: the point estimate clears the tolerance, the upper bound does not |
| behaviour | 3 | 19 | 15.8% [5.5%, 37.6%] | 5.0% | **fail** — the observed rate is above the tolerance |
| _pooled (for contrast)_ | 3 | 211 | 1.4% [0.5%, 4.1%] | 2.0% | **fail** on the bound, **pass on the point estimate** (1.4%) |

**Neither family clears its standard, and they fail for entirely different reasons.** That distinction is the substance of this section, because the two call for different responses and a single pass/fail flag erases it.

The policy family has a *perfect record and insufficient evidence*: 0 incorrect statements in 79 answered turns, which bounds the error rate at 4.6% -- above the 2.0% tolerance. Nothing is wrong with the system on this axis. What is wrong is that 79 answered turns cannot demonstrate 2.0%; it takes about 189. **This family fails on sample size, and no improvement to the agent would fix it.**

The behaviour family has an *observed failure*: 3 violations in 19 scored turns, 15.8% [5.5%, 37.6%], with a lower bound of 5.5% already above the 5.0% tolerance. That one is a real finding about the agent and needs remediation, not a larger sample. The wide interval means the eval cannot say *how* bad -- somewhere between one turn in eighteen and one in three -- which is its own problem, but the failure itself is established.

And the contrast the pooled row is there for: 3 failures over 211 scored turns is 1.4%, which clears the 2.0% tolerance on the point estimate. **That is the number a harness reports, and it ships.** It passes by putting 113 abstentions in the denominator as non-failures and averaging a family with a 1-in-6 violation rate into one with none. Two independent mistakes -- pooling across consequences, and testing a point estimate rather than a bound -- and either alone is enough to turn this table's two failures into a green dashboard.

## Why the sample size decides this before the score does

The policy family recorded zero failures. That is not a rate of zero. With 79 clean observations the tightest claim available at 95% confidence is **4.6%**, and no amount of additional cleanliness on the same 79 turns will improve it.

| clean observations | tightest demonstrable failure rate |
|---|---|
| 19 | 16.82% ← this eval, behaviour family |
| 79 | 4.64% ← this eval, policy family |
| 96 | 3.85% |
| 192 | 1.96% |
| 216 | 1.75% |
| 400 | 0.95% |
| 800 | 0.48% |
| 3000 | 0.13% |

Inverted, which is the form worth having before commissioning a run:

| tolerance you need to demonstrate | clean observations required |
|---|---|
| 5.0% | 73 |
| 2.0% | 189 |
| 1.0% | 381 |
| 0.5% | 765 |
| 0.1% | 3838 |

So a business that needs to show a policy-error rate below 0.5% needs about 765 turns and cannot get there by scoring better on 79. **This is computable before the eval is built, and it is the single cheapest piece of eval design work available.** It is also the thing a pass rate can never reveal: 100% on 79 turns and 100% on 800 turns look identical in a report and license very different decisions.

## The cut that cannot be set: per-configuration

The obvious use of a cut score is to choose a configuration -- deploy the ones scoring at least k of 8. Here is how consistent that decision would be.

| cut | configurations passing | decision consistency | would be reclassified on a re-run |
|---|---|---|---|
| 5/8 | 10/24 | 0.937 (all) / 0.884 (current corpus) | 6.3% / 11.6% |
| 6/8 | 9/24 | 0.912 (all) / 0.825 (current corpus) | 8.8% / 17.5% |
| 7/8 | 6/24 | 0.899 (all) / 0.799 (current corpus) | 10.1% / 20.1% |
| 8/8 | 4/24 | 0.938 (all) / 0.876 (current corpus) | 6.2% / 12.4% |

At the least consistent candidate cut, 7/8, roughly **20.1% of configurations would be classified differently if the eval were run again** -- and that is within the stratum where the comparison is meaningful at all. The pooled column looks better only because nine configurations score 0/8 and are never near the boundary, the same floor effect that flattered the item analysis.

- A configuration scoring 6/8 has a true accuracy somewhere in [40.9%, 92.9%].
- A configuration scoring 7/8 has a true accuracy somewhere in [52.9%, 97.8%].
- A configuration scoring 8/8 has a true accuracy somewhere in [67.6%, 100.0%].

Which is the whole problem in one line: at eight items a cut score cannot separate a configuration that is barely adequate from one that is excellent, so **the eval as designed cannot license a choice between configurations.** The consistency figures above are also optimistic -- they assume the eight items are exchangeable binomial trials, and `docs/item-analysis.md` showed two of them are at ceiling.

## Why the standard-setting methods do not transfer unchanged

A modified-Angoff study asks subject-matter experts, for each item, what proportion of *minimally competent candidates* would answer it correctly; the sum of those judgements is the cut score. It is the most widely used method in certification and it is the wrong tool here, for four reasons that are worth separating because two of them are fixable and two are not.

**There is no candidate population.** Angoff's central object is a hypothetical borderline examinee drawn from a population with a distribution of ability. The 24 configurations here differ by experimental design, not by ability: `corpus=v1` does not score badly because it is a weaker candidate but because it was handed superseded documents. Asking an expert to imagine a minimally competent configuration is asking them to imagine a point on an axis that does not exist. *Not fixable* -- it is a category difference between people and systems.

**The examinee can be edited in response to failing.** A candidate who fails studies; a system that fails gets its prompt rewritten against the very items it failed. That is not studying, it is item exposure, and it invalidates the cut for every subsequent administration. Certification programmes spend heavily on item banks and rotation for exactly this reason, and an eval suite with eight fixed items has no defence at all. *Fixable*, and expensive: it needs held-out items and a rotation policy.

**The failure costs are not exchangeable across items.** Angoff produces a compensatory total. Here, one restricted-action violation is not offset by seven correct policy answers, which is why the standards above are conjunctive and per-family. *Fixable* -- conjunctive standards are standard practice for multi-domain exams, and that part of the methodology transfers directly.

**The construct drifts under you.** A certification blueprint is stable for years. This eval's correct answers changed when the returns policy changed -- that is what the two corpora *are* -- so a cut score set today is partly a statement about a document set that will be superseded. *Not fixable*, and it means the cut has to be re-derived on a schedule rather than set once.

What does transfer, and is the reusable part: declaring the standard before seeing the score; separating tolerances by consequence rather than pooling them; judging against an interval bound rather than a point estimate; and reporting decision consistency instead of measurement precision, because the decision is what ships.

## The number for the deployment memo: how much volume, at what bound

Not a pass rate. The system's failure mode is abstention, not error, so the deployable quantity is the share of turns it handled itself and the worst error rate among those turns that the data cannot rule out.

| slice | automated | escalated | correct when answering | error rate not ruled out |
|---|---|---|---|---|
| all policy turns | 79/192 = 41.1% [34.4%, 48.2%] | 58.9% | 79/79 | **≤ 4.6%** |
| current documents | 74/96 = 77.1% [67.7%, 84.4%] | 22.9% | 74/74 | **≤ 4.9%** |
| stale documents | 5/96 = 5.2% [2.2%, 11.6%] | 94.8% | 5/5 | **≤ 43.4%** |

**With current documents the system safely automates 77.1% of policy volume [67.7%, 84.4%], escalating the rest, and the eval bounds its error rate on automated turns at 4.9%.** That is the sentence a deployment decision can be made on. Every part of it is load-bearing: the conditional on document freshness, the interval on the coverage, and the bound rather than the observed zero.

The conditional is not a caveat, it is the finding. On stale documents coverage collapses to 5.2% -- the system mostly declines, which is the correct behaviour and also means the automation benefit disappears entirely. So the value of deploying this is a value claim about the document pipeline, not about the model. Retrieval freshness is the deployment's actual dependency.

## Where the cut lands, as a function of the cost you assign to being wrong

One incorrect policy statement costs some number of unnecessary escalations. Nobody can defend a single value for that ratio, so here is the decision across a range of them, against a baseline of escalating every turn to a human (cost 1.0 per turn).

| cost of one wrong answer | cost per turn, automated | vs escalate-everything |
|---|---|---|
| 1× an escalation | 0.267 | automate (+73.3%) |
| 5× an escalation | 0.419 | automate (+58.1%) |
| 10× an escalation | 0.610 | automate (+39.0%) |
| 20× an escalation | 0.990 | automate (+1.0%) |
| 50× an escalation | 2.131 | escalate everything (-113.1%) |
| 100× an escalation | 4.033 | escalate everything (-303.3%) |

The break-even is **20×**: while one incorrect policy statement costs less than about 20 unnecessary escalations, automating is the cheaper policy even under the eval's most pessimistic reading of its own error rate. Above that, escalate everything.

Two things about that number. It comes from the error *bound*, not the observed zero -- with the point estimate, automation wins at every ratio and the calculation says nothing. And coverage cancels out of it: how much traffic the system takes changes how much automation is worth, not whether it is worth it. The lever that moves the break-even is sample size, because that is what sets the bound. At 765 clean turns instead of 74, the break-even moves past 200×.

## Recommendation

**Do not deploy on the strength of this eval — but the blocker on the policy side is the eval, not the agent.** Policy handling was correct on every one of the 79 turns any configuration attempted, and automates 77.1% of volume when retrieval is fresh. It fails its standard only because 79 turns cannot demonstrate 2.0%. The behaviour family is the one that fails on the evidence, and under a conjunctive rule that is decisive by itself.

In order of what would change the decision:

1. **Fix the behaviour violations.** 3 in 19 turns, lower bound 5.5%. This is the only item on this list that is about the agent, and it is the only one that a larger eval would not resolve. Everything else here is a measurement problem.

2. **Expand the behaviour family to at least 73 turns.** Even remediated, 19 turns could only ever bound the violation rate at 16.8% -- three times its own tolerance. It is the smallest and highest-consequence family in the suite, which is exactly backwards.

3. **Add answered policy turns, not configurations.** 189 answered turns would demonstrate the 2.0% tolerance; 765 would demonstrate 0.5%. The 24-cell grid spends its sample on breadth, and 9 of those cells spent theirs establishing that stale documents produce abstentions. Note the interaction with abstention: only 79 of 192 turns were answered at all, so the policy family's effective sample is well under half the nominal one, and improving coverage tightens the bound for free.

4. **Stop reporting a pooled rate.** It is the only figure here that clears a tolerance on any reading, and it clears it by averaging a failing family into a clean one.

5. **Attach the standard to a monitoring regime rather than a launch gate.** The correct answers changed once already when the policy documents changed; a cut score set against a corpus is only valid while that corpus is current.

None of this is a statement that the system is bad. On the evidence it is a careful system with a strong preference for declining over guessing, which is the right disposition for the task. The finding is that the eval built to assess it was sized for a pass rate rather than for a decision, and a pass rate was the one thing nobody needed.

