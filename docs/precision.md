# Precision of the published findings

Source: https://github.com/JulieElkinsAWS/northwind-connect-ai
Commit: adb54542   Run: 2026-08-26
192 graded policy turns across 24 cells, 8 per cell. Post-audit labels.

## Accuracy by axis level, with 95% Wilson intervals

| axis | level | correct | n | accuracy | 95% CI | +/- |
|---|---|---|---|---|---|---|
| model | haiku | 17 | 64 | 26.6% | [17.3, 38.5] | 11.9 pts |
| model | opus | 33 | 64 | 51.6% | [39.6, 63.4] | 12.0 pts |
| model | sonnet | 29 | 64 | 45.3% | [33.7, 57.4] | 12.1 pts |
| prompt | naive | 41 | 96 | 42.7% | [33.3, 52.7] | 10.0 pts |
| prompt | tuned | 38 | 96 | 39.6% | [30.4, 49.6] | 10.0 pts |
| corpus | v1 | 5 | 96 | 5.2% | [2.2, 11.6] | 6.4 pts |
| corpus | v2 | 74 | 96 | 77.1% | [67.7, 84.4] | 9.4 pts |
| retriever | kb | 47 | 96 | 49.0% | [39.2, 58.8] | 9.8 pts |
| retriever | keyword | 32 | 96 | 33.3% | [24.7, 43.2] | 9.9 pts |

## The four published contrasts

| axis | contrast | published | difference, 95% CI | separates from zero? |
|---|---|---|---|---|
| corpus | v1 -> v2 | 5% -> 77% | +71.9 points [+60.5, +79.7] | **yes** |
| retriever | keyword -> kb | 33% -> 49% | +15.6 points [+1.7, +28.7] | **yes** |
| model | haiku -> opus | 27% -> 52% | +25.0 points [+8.1, +40.0] | **yes** |
| prompt | tuned -> naive | 40% -> 43% | +3.1 points [-10.6, +16.7] | no |

## What the nulls are actually saying

**prompt (prompt configuration): +3.1 points [-10.6, +16.7].** The interval spans zero, so this run does not establish a difference between `tuned` and `naive`. It also could not have established one smaller than about 14 points -- so "no measurable difference" is, at this sample size, largely a statement about the design. An effect of 10 points would have been missed.

## Which findings would not survive a relabelling

**retriever (keyword -> kb): +15.6 points [+1.7, +28.7].** Clears zero by 1.7 points. Reported as a finding in the source project, and it is one -- but the bound is close enough that a different-but-defensible grading of a few turns would move it across zero. The human audit relabelled 26 of these 216 turns; that is the scale of judgement this bound sits inside. Directionally supported, not established.

## The same contrasts within `corpus=v2` only

The marginals above pool the `corpus=v1` arm, which sits at 5% and is a floor: nothing any other knob does can show through it. Restricting to the arm where the corpus is not the binding constraint halves n and widens every interval, and is the version that answers whether a knob does anything at all.

| axis | contrast | all 192 turns | within v2 only (n=48/arm) |
|---|---|---|---|
| retriever | keyword -> kb | +15.6 points [+1.7, +28.7] | +29.2 points [+12.5, +44.2] |
| model | haiku -> opus | +25.0 points [+8.1, +40.0] | +37.5 points [+15.7, +55.3] |
| prompt | tuned -> naive | +3.1 points [-10.6, +16.7] | -4.2 points [-20.7, +12.6] |

**retriever is larger than the pooled figure suggests**, by 14 points (+15.6 points [+1.7, +28.7] pooled, +29.2 points [+12.5, +44.2] within v2). The floor arm was diluting it, so the published marginal understates what this knob buys once the corpus is not the binding constraint. This also resolves the fragile pooled bound above: within v2 the contrast clears zero comfortably.

**model is larger than the pooled figure suggests**, by 12 points (+25.0 points [+8.1, +40.0] pooled, +37.5 points [+15.7, +55.3] within v2). The floor arm was diluting it, so the published marginal understates what this knob buys once the corpus is not the binding constraint.

**prompt is null either way** (-4.2 points [-20.7, +12.6] within v2), so the pooled null is not a floor artefact -- though at n=48 per arm this version could only have detected an effect above about 17 points.

## How large would the eval set have to be?

At p=0.5, the worst case for interval width:

| target precision | turns needed per category | vs. this design |
|---|---|---|
| +/- 20 pts | 25 | 3x the 8 per cell |
| +/- 10 pts | 97 | 12x the 8 per cell |
| +/- 5 pts | 385 | 48x the 8 per cell |
| +/- 2.5 pts | 1537 | 192x the 8 per cell |

The per-cell n of 8 supports a half-width of roughly 28 points. Per-cell claims in the source tables should be read as directional only; the axis marginals, at 64 and 96, are where the run can carry an argument.
