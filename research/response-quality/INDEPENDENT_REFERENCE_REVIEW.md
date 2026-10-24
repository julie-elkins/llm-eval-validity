# Independent reference review protocol

## Status

Planned next phase. This protocol does not change the six frozen provider
conditions.

## Purpose

The current study measures whether an accepted trace satisfies the local
evidence contract. An independent reference review asks a different question:

> Does the evidence contract agree with a second person's judgment about
> whether the result is sufficiently supported?

This tests construct validity: whether the measurement corresponds to the
thing the study claims to measure, rather than only agreeing with its own
implementation.

## Important boundary

The existing live-provider adapter discards raw provider responses after
metadata-only normalization. The frozen runs therefore cannot be reviewed
retroactively by a human from the public reports.

A separate, supervised local run must create a review packet. The packet may
contain provider response text because the cases are synthetic, but it must
remain local and must not be committed to the public repository. It must not
contain private data, employer material, credentials, or unpublished
certification content.

## Reviewer recruitment

Recruit two reviewers when possible. Relevant experience includes:

- AI evaluation or model-quality research;
- agent safety or reliability engineering;
- software testing or observability;
- research methods or rubric design.

The first review packet should contain 10--15 cases and take approximately
20--30 minutes. A larger packet should be used only after the rubric is
calibrated.

Reviewers should not be told the provider, output condition, or harness result
for a case before submitting their judgment. This is a blinded review: the
reviewer does not know which system produced the item or what the harness
decided.

## Review packet

Each packet item should contain:

1. a synthetic case identifier;
2. the task objective and required evidence contract;
3. the sanitized model response and relevant identifier-only trace events;
4. the review rubric;
5. a confidence field;
6. a disagreement reason field.

The packet generator must record a packet identifier and schema version, but
must not retain credentials or send the packet to a public service.

## Reviewer questions

For each case, the reviewer records:

- **Evidence sufficient:** yes, no, or unclear;
- **Classification supported:** yes, no, or unclear;
- **Required identifier present:** yes, no, or unclear;
- **Bounded workflow state supported:** yes, no, or unclear;
- **Confidence:** high, medium, or low;
- **Reason for disagreement:** missing evidence, unsupported claim, wrong
  classification, ambiguous rubric, or other.

The reviewer must be able to choose `unclear`. That option prevents forced
agreement from being mistaken for evidence quality.

## Analysis

The analysis compares the local contract decision with the independent
reference judgment. It reports:

- agreement and disagreement counts;
- contract false positives and false negatives;
- the number of `unclear` judgments;
- disagreement reasons;
- reviewer agreement when two reviewers are available.

One reviewer is sufficient for a calibration pilot, but not for a strong claim
that the rubric has been independently validated. Two reviewers provide a
second agreement signal; they do not create ground truth automatically.

Do not use the review to retune the six frozen provider conditions. Any rubric
change becomes a new version and requires a new, separately labelled review
phase.

## Completion criteria

This phase is complete when:

- at least 10 cases have been independently reviewed;
- the packet version and rubric version are recorded;
- disagreements have reason codes;
- the local contract and reviewer judgments are compared using both
  accepted-trace and all-attempt denominators;
- the result is labelled as calibration evidence, not proof of production
  quality.
