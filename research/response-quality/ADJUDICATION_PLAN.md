# Version-2 review analysis and adjudication plan

## Purpose

This plan defines how completed version-2 independent reviews will be
reconciled and reported. It is a calibration plan, not a way to reopen the six
frozen provider conditions.

Calibration means testing whether another person can apply the rubric
consistently. It does not mean proving that a provider, model, or workflow is
safe in production.

## What remains frozen

The following must not change after a reviewer receives a packet:

- the six provider conditions and their reported results;
- the version-2 case set and rubric version;
- the local evidence-contract definitions;
- the private answer key;
- the reviewer instructions and allowed response categories;
- the decision to retain refusals rather than rerun them.

If the rubric needs to change, record a new rubric version and start a
separately labelled calibration phase. Do not silently recode completed forms.

## Private intake gate

A returned form is eligible for analysis only after the private packet record
has been reconciled. The private record must confirm:

1. the returned form belongs to the intended packet version;
2. the packet digest and reviewer form can be linked without publishing either;
3. the reviewer completed the requested case set;
4. the return date and any provenance statement are recorded;
5. no communication conflict or duplicate submission remains unresolved.

Reviewer statements about AI assistance are provenance fields: they record what
the reviewer reported, but they do not independently prove how the review was
produced. A conflict remains unresolved until it is checked privately.

Only the private record may contain names, email addresses, packet digests,
completed forms, raw case content, or the answer key.

## Analysis order

Analyze the forms in this order:

1. Assign an internal reviewer identifier that does not reveal identity.
2. Confirm the packet and rubric versions.
3. Lock the returned judgments before comparing them with another reviewer or
   the answer key.
4. Compare each judgment with the local evidence-contract result.
5. Compare reviewers with each other when at least two reviewers judged the
   same case.
6. Record disagreement reason codes without replacing the original judgments.
7. Compare the disagreements with the private answer key.
8. Write a metadata-only public summary after the private reconciliation is
   complete.

The comparison must preserve `yes`, `no`, and `unclear`. An `unclear` judgment
is evidence of rubric ambiguity, not a failed reviewer.

## Measures to report

For each reviewed field, report:

- cases reviewed and cases eligible for analysis;
- exact agreement with the local contract;
- disagreement counts;
- `unclear` counts;
- false-positive and false-negative counts where the comparison supports them;
- disagreement reason counts;
- reviewer-to-reviewer agreement when two or more reviewers share cases;
- confidence distribution when the form records confidence.

Reviewer-to-reviewer agreement means how similarly two humans judged the same
cases. Agreement between the local contract and a reviewer answers a different
question and must remain a separate measure.

Raw agreement is the primary small-sample description. A chance-adjusted
coefficient such as Cohen's kappa may be reported only if category coverage and
the denominators are shown. If kappa is reported, include the category
marginals and the maximum attainable kappa; do not present a lone coefficient
as proof of rubric quality.

## Disagreement handling

Independent judgments are the data. Do not force reviewers to reach consensus
before calculating agreement.

If an adjudication discussion is useful, it happens after the independent forms
are locked. Adjudication means documenting how a disagreement is interpreted or
whether the rubric needs clarification; it does not rewrite the original
judgments or turn a discussion into a new independent rating.

The public report should distinguish:

- independent reviewer judgments;
- local-contract comparisons;
- reviewer-to-reviewer agreement;
- post-review rubric clarifications;
- unresolved disagreements.

## Completion gates

The version-2 round may be reported at one of two levels:

### Calibration pilot

- at least 10 cases are analyzable;
- the packet and rubric versions are recorded;
- disagreements have reason codes;
- the result is labelled a one-reviewer or incomplete calibration pilot when
  fewer than two reviewers share the cases.

### Independent-review comparison

- at least 10 common cases are independently judged by two reviewers;
- both forms pass the private intake gate;
- reviewer-to-reviewer agreement is reported;
- local-contract comparisons use the same cases and denominators;
- limitations and unresolved disagreements are published.

Neither gate supports a claim of production quality, model superiority, or
general rubric validity. It supports only the narrower claim that the stated
reviewers did or did not apply this version of the rubric consistently on this
synthetic packet.

## Public reporting boundary

The public repository may publish:

- packet and rubric version identifiers;
- case counts;
- aggregate agreement and disagreement counts;
- reason-code counts;
- limitations and unresolved status.

It must not publish:

- reviewer identities or contact information;
- completed forms or raw reviewer comments;
- answer keys;
- raw model responses or private traces;
- claims that the review proves production safety or general model quality.
