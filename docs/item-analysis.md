# Item analysis: which questions carry the eval

8 policy questions, each attempted by every configuration. Post-audit labels.

## First, the analysis that looks like good news

Over all 24 configurations, upper and lower groups being the top and bottom 8 by total score:

| question | correct | difficulty | r (corrected) | D | upper | lower | verdict |
|---|---|---|---|---|---|---|---|
| `expedited_shipping` | 11/24 | 0.46 | +0.90 | +1.00 | 1.00 | 0.00 | strong -- keep |
| `returns_window` | 12/24 | 0.50 | +0.85 | +1.00 | 1.00 | 0.00 | strong -- keep |
| `price_match` | 8/24 | 0.33 | +0.83 | +0.88 | 0.88 | 0.00 | strong -- keep |
| `return_shipping` | 14/24 | 0.58 | +0.78 | +1.00 | 1.00 | 0.00 | strong -- keep |
| `warranty_term` | 8/24 | 0.33 | +0.75 | +0.88 | 0.88 | 0.00 | strong -- keep |
| `electronics_returns` | 7/24 | 0.29 | +0.73 | +0.75 | 0.75 | 0.00 | strong -- keep |
| `restocking_fee` | 10/24 | 0.42 | +0.69 | +1.00 | 1.00 | 0.00 | strong -- keep |
| `warranty_proof` | 9/24 | 0.38 | +0.68 | +0.75 | 0.75 | 0.00 | strong -- keep |

Every item strong, every lower-group pass rate exactly 0.00. That last column is the tell.

## Why it is not good news

9 of the 24 configurations scored 0/8, and all 9 of them are `corpus=v1`. 8 of the 8 cells in the lower group are among them, so the lower group is nothing but configurations that answered nothing at all. `lower` is therefore 0.00 for every question by construction, and `D` collapses to the upper group's pass rate -- a difficulty statistic wearing a discrimination statistic's name.

What every item is detecting is the corpus. Mean inter-item correlation over the full grid is **+0.65** (range +0.39 to +0.92) and Cronbach's alpha is **0.94** -- values that in test development would be read as eight near-duplicate items rather than eight good ones. The suite is behaving as a single item asked eight times: *did this configuration retrieve the current policy document*.

## The analysis that says something about the questions

Restricted to the 12 `corpus=v2` configurations, where the corpus is not the binding constraint and the total scores actually spread:

| question | correct | difficulty | r (corrected) | D | upper | lower | verdict |
|---|---|---|---|---|---|---|---|
| `restocking_fee` | 8/12 | 0.67 | +0.68 | +1.00 | 1.00 | 0.00 | strong -- keep |
| `price_match` | 8/12 | 0.67 | +0.68 | +0.75 | 1.00 | 0.25 | strong -- keep |
| `expedited_shipping` | 11/12 | 0.92 | +0.56 | +0.25 | 1.00 | 0.75 | strong -- keep |
| `warranty_proof` | 8/12 | 0.67 | +0.55 | +0.50 | 1.00 | 0.50 | strong -- keep |
| `electronics_returns` | 7/12 | 0.58 | +0.52 | +0.75 | 1.00 | 0.25 | strong -- keep |
| `warranty_term` | 8/12 | 0.67 | +0.43 | +0.75 | 1.00 | 0.25 | strong -- keep |
| `returns_window` | 12/12 | 1.00 | +0.00 | +0.00 | 1.00 | 1.00 | at ceiling -- regression check only |
| `return_shipping` | 12/12 | 1.00 | +0.00 | +0.00 | 1.00 | 1.00 | at ceiling -- regression check only |

Mean inter-item correlation falls to **+0.22** (range +0.00 to +0.63), alpha to **0.76**. Both are what a suite of eight questions that measure related-but-distinct things should look like -- so the redundancy in the first table was the corpus axis, not a property of the questions.

**6 of 8 questions still discriminate at r >= 0.30 once the floor is removed.** Those are the ones ranking configurations on anything other than which corpus they were pointed at.

**`returns_window` is at the ceiling within this stratum (12/12).** Every configuration passed it, so it has no variance and its r of +0.00 is arithmetic, not evidence of a defect. It still separates v1 from v2 -- it is a corpus detector, and a fine one. What it cannot do is rank two configurations that both have the current corpus, which is the decision this eval is for. Keep it as a regression check, stop counting it toward configuration comparisons, and add a harder question on the same topic if that topic needs to stay in the ranking.

**`return_shipping` is at the ceiling within this stratum (12/12).** Every configuration passed it, so it has no variance and its r of +0.00 is arithmetic, not evidence of a defect. It still separates v1 from v2 -- it is a corpus detector, and a fine one. What it cannot do is rank two configurations that both have the current corpus, which is the decision this eval is for. Keep it as a regression check, stop counting it toward configuration comparisons, and add a harder question on the same topic if that topic needs to stay in the ranking.

## What this table can and cannot support

The stratified correlations rest on 12 observations each. Sampling error on a correlation at n=12 is roughly +/-0.5 near r = 0, which is wider than most of the gaps in the table. So it separates 'clearly working' from 'clearly not' and the ordering within those groups should not be read at all. Retiring a question on this evidence alone would be overreach; flagging it for review is what the number supports.

Two design lessons that do generalise, and are the reusable part:

1. **Run item analysis inside strata, not over the whole grid.** A factorial eval with one dominant axis will report every item as excellent, because every item detects the dominant axis. The full-grid table above is exactly the artefact, and it is the table an eval harness produces by default.
2. **Check the lower group before trusting a discrimination index.** A lower group scoring 0.00 on every item means the index is measuring the floor. Here that was 9 of 24 configurations; the statistic gave no warning, the raw column did.

## Difficulty spread

Within the stratum, difficulty runs 0.58 (`electronics_returns`) to 1.00 (`returns_window`).
12 configurations, of which 4 scored full marks -- so the suite is approaching its ceiling for the better configurations and would need harder questions to keep separating them.
