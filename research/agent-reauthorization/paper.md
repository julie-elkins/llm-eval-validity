# From Evaluation to Reauthorization: Change-Aware Governance for AI Agent Releases

**Author:** Julie Elkins
**Artifact status:** Phase-4 synthetic research manuscript in progress; clean-checkout
reproduction and external-validity phases remain future work.
**Repository:** [LLM Eval Validity](https://github.com/julie-elkins/llm-eval-validity)

## Abstract

AI-agent evaluations are tied to a particular system revision, but release and
continued-operation decisions often outlive the evidence that supports them. A
change to a prompt, tool, data source, policy, evaluator, dependency, or deployment
environment can make a previous reliability claim incomplete without changing the
stored score.

This paper reports a reproducible pilot study of that problem. It compares ordinary
pass/fail reporting, revision-aware evidence, and revision-aware evidence combined
with an explicit reauthorization protocol. Reauthorization means an explicit
decision that current evidence still supports continued use after a relevant system
change. The protocol records change impact, required reevaluation, accountable
ownership, rollback evidence, escalation, residual risk, and human approval
boundaries.

The study is offline, deterministic, synthetic, and metadata-only. In the original
18-case pilot, the pass/fail condition made 12 false-ready decisions, the
revision-aware condition made none but matched 12 of 18 reference decisions, and the
full reauthorization condition made no false-ready decisions and matched all 18.
A held-out robustness matrix added 12 compound-change cases. Phase 4 then added
210 new cases with independent metadata variation, frozen development, robustness,
and locked-holdout splits. On the 30-case matrix,
the pass/fail condition made 24 false-ready decisions, while the full
reauthorization condition made none and matched all 30 reference decisions. The full
condition required more bounded evaluation and review work.

On the Phase-4 matrix, pass/fail reporting made 150 false-ready decisions, while
revision-aware evidence made none and full reauthorization made none. Full
reauthorization matched all 210 reference decisions. These results strengthen
coverage of the protocol's synthetic behavior; they do not establish production
effectiveness or population-level performance.

These results support a narrow claim about the behavior of the implemented protocol
on controlled synthetic cases. They do not establish production safety, general
agent capability, or organizational effectiveness.

**Keywords:** agent evaluation, evaluation validity, provenance, reauthorization,
release governance, reproducibility, synthetic study

## 1. Introduction

An evaluation result is not a property of an agent in the abstract. It is evidence
produced by a particular scenario set, evaluator, workflow, and system revision.

That distinction becomes operationally important when the system changes. A team may
update a tool, prompt, retrieval corpus, authorization policy, evaluator threshold,
dependency, or deployment configuration while continuing to cite an earlier result.
The stored result can remain internally correct while no longer supporting the
decision being made.

This paper studies the gap between evaluation evidence and the release or
continued-operation decision that relies on it. The study does not attempt to
measure all aspects of agent quality. It tests whether a small protocol can make
stale or incomplete evidence visible before an unsupported approval is made.

The contribution is deliberately bounded. The study connects revision identity,
evidence invalidation, change impact, ownership, rollback evidence, escalation, and
human approval into one decision protocol, then compares that protocol with simpler
reporting conditions on the same synthetic cases. It does not claim novelty for any
one of those controls in isolation.

## 2. Research questions and hypotheses

### 2.1 Primary research question

Can revision-aware evidence plus an explicit reauthorization protocol reduce
unsupported release decisions after a tool-using AI-agent workflow changes,
compared with ordinary pass/fail reporting?

### 2.2 Secondary questions

1. Which change families most often invalidate a prior reliability claim?
2. Does revision-aware evidence detect invalid claims before approval?
3. What evaluation and review cost does the protocol add?
4. Which controls are necessary: revision identity, change impact analysis,
   ownership, rollback evidence, or human approval?

### 2.3 Pre-specified hypotheses

- **H1, fewer unsupported approvals:** revision-aware conditions will produce fewer
  false-ready decisions than the pass/fail baseline.
- **H2, earlier invalidation:** revision-aware conditions will identify stale
  evidence sooner than the baseline.
- **H3, explicit cost:** revision-aware conditions will require more evaluation or
  review work than the baseline.
- **H4, organizational control value:** the full reauthorization condition will
  identify failure modes that revision identity alone cannot classify, especially
  missing ownership, missing rollback evidence, and unresolved residual risk.

A false-ready decision is an approval that is not supported by the evidence available
for the changed system. Residual risk is the risk that remains after the proposed
controls are applied.

## 3. Related work and positioning

The study is adjacent to several active areas: agent evaluation in production,
continuous evaluation of evolving agents, provenance and evidence invalidation,
evaluation validity, and authorization under agent evolution. These areas establish
why changing systems require more than a static score; they do not make the present
protocol a universal solution.

The paper's contribution is the tested connection between a revision-aware evidence
record and an explicit reauthorization decision. The protocol treats a release or
continued-operation decision as the unit of interest, rather than treating a score
as a property of a model independent of its surrounding workflow.

The paper does not claim novelty for agent reliability evaluation, continuous
evaluation, provenance, stale evidence, human approval, release gates, or
measurement validity individually. The positioning and adjacent references are
listed in [RELATED_WORK.md](RELATED_WORK.md).

## 4. Method

### 4.1 Study design

The unit of analysis is a claim-change case containing:

1. a reliability or readiness claim;
2. the evidence that originally supported it;
3. a defined system revision;
4. the changed component or components;
5. the decision made after the change; and
6. the evidence available to the reviewer.

Each case is evaluated under three conditions. The same synthetic case is passed
through all three conditions so the comparison isolates the decision protocol rather
than changing the case set between conditions.

| Condition | Decision inputs | Purpose |
| --- | --- | --- |
| Pass/fail baseline | Prior result and current pass/fail result | Represent ordinary reporting without explicit revision invalidation |
| Revision-aware evidence | Revision identifiers, evidence digest, changed component, evidence status, and invalidation rule | Test whether provenance and invalidation alone reduce unsupported decisions |
| Revision-aware reauthorization | Revision-aware evidence plus change classification, owner, reevaluation scope, rollback evidence, escalation, residual risk, and approval boundary | Test the organizational decision layer |

Reauthorization means an explicit decision that the current evidence still supports
continued use after a relevant change. The possible decisions are `reauthorized`,
`blocked`, and `review_required`.

### 4.2 Synthetic change families

The original pilot contains 18 cases across six change families:

1. prompt or instruction change;
2. tool or API change;
3. retrieval-data or policy-source change;
4. authorization or permission-policy change;
5. evaluator or threshold change; and
6. deployment or dependency change.

Each family contains a current case, a case requiring reevaluation, and a negative
control. A negative control is a deliberately plausible green-looking case that
must not be approved because required controls are missing.

The held-out robustness matrix adds 12 compound-change cases that combine a family
change with deployment change. Those cases were not part of the original 18-case
matrix.

Phase 4 adds 210 new cases. The base matrix contains ten cases for every
family/variant cell. It is split into 72 development cases, 54 robustness cases,
and 54 locked-holdout cases. A further 30 compound-change cases form a locked
compound holdout. Cases vary revision lineage, changed-component descriptors,
evidence revisions, template identifiers, and negative-control completeness.
Every case has a unique independence group. A locked holdout is a case set kept
out of protocol tuning so the final run tests the frozen design rather than
memorization.

### 4.3 Reference decisions

The study uses a deterministic reference decision for each synthetic case. The
reference decision is defined before condition outputs are generated and inspects
the complete synthetic case record, including the declared change and required
evidence.

The reference is a study oracle, not a universal organizational authority. Its
purpose is to make disagreement measurable. In the robustness phase, expected
decisions come from a separate `reference-decisions.json` manifest rather than from
the condition evaluator. This reduces coupling between the implementation and the
reference used to judge it.

### 4.4 Outcomes

The primary outcomes are:

- **False-ready decisions:** approvals when the reference decision is
  `review_required` or `blocked`.
- **Stale-claim detection:** identification of affected evidence before approval.
- **Detection latency:** decision steps between the change and the first
  stale-evidence or missing-evidence finding.
- **Correct escalation:** routing a case to `review_required` when the available
  evidence cannot safely resolve it.
- **Operational cost:** evaluation runs, review steps, blocked approvals, and
  synthetic time units.

Secondary outcomes include unsupported-claim rate, incorrect automatic closure,
rollback-evidence completeness, ownership completeness, unestablished cases, and
false-block rate.

### 4.5 Analysis and reporting

The study reports counts and exact proportions by condition and change family. It
does not use inferential statistics for the synthetic matrices. A confidence
interval is a range describing uncertainty around an estimate; it cannot turn a
small deterministic synthetic case set into population evidence.

The primary comparison is the pass/fail baseline versus full reauthorization on
false-ready decisions. The revision-aware condition is an intermediate comparison
that tests whether versioned evidence accounts for the result without the
organizational protocol.

The protocol was frozen before the pilot results were generated. Any extension must
be recorded as a new phase rather than added only because it improves the result.

## 5. Results

### 5.1 Original pilot

The original pilot used 18 synthetic cases.

| Condition | False-ready | Stale detected | Correct reference decisions | Evaluation runs | Review steps | Time units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pass/fail reporting | 12/18 | 0/12 | 6/18 | 18 | 0 | 18 |
| Revision-aware evidence | 0/18 | 12/12 | 12/18 | 30 | 12 | 42 |
| Revision-aware reauthorization | 0/18 | 12/12 | 18/18 | 24 | 24 | 60 |

The baseline falsely approved every affected case in the fixed matrix. Revision-aware
evidence detected every affected case, but it did not classify missing ownership and
rollback controls in the negative controls. Full reauthorization blocked all six
negative controls and matched every reference decision.

The full condition used 60 relative time units versus 18 for the baseline. These are
bounded study counters, not financial estimates. The result shows a controlled
tradeoff: stronger decision controls reduced unsupported approvals while requiring
more review and evaluation work.

### 5.2 Held-out robustness matrix

The robustness run added 12 compound-change cases, for 30 cases total.

| Condition | False-ready | Stale detected | Correct reference decisions | Evaluation runs | Review steps | Time units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pass/fail reporting | 24/30 | 0/24 | 6/30 | 30 | 0 | 30 |
| Revision-aware evidence | 0/30 | 24/24 | 18/30 | 54 | 24 | 78 |
| Revision-aware reauthorization | 0/30 | 24/24 | 30/30 | 42 | 42 | 108 |

The full condition retained zero false-ready decisions and matched all 30 reference
decisions. This is a robustness observation, not population-level evidence: the
cases remain synthetic and deterministic.

### 5.3 Independent reproduction

The robustness run was reproduced on 2026-10-23 from newly cloned repositories.
The harness `main` revision was
`026e3e902c121ee334551b539879f4e835afe9b5`, and the validity-analysis `main`
revision was `bcb83112361d22a2bcc03b4767cc7a51b04b1eeb`.

The fresh run matched the checked-in compact fixture's case count, case-set hash,
condition counts, false-ready counts, stale-claim detection counts, correct
escalation counts, and bounded time counters. The executable also emits detailed
case-level fields that are intentionally omitted from the public compact fixture.
That representation difference is expected because the public fixture is
metadata-only.

### 5.4 Phase-4 split-aware matrix

Phase 4 used 210 new synthetic cases. The base matrix was balanced across six
families and three variants, with ten cases per family/variant cell. The remaining
compound cases were held out from development.

| condition | false-ready | stale detected | correct reference decisions | evaluation runs | review steps | time units |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Pass/fail reporting | 150/210 | 0/150 | 60/210 | 210 | 0 | 210 |
| Revision-aware evidence | 0/210 | 150/150 | 138/210 | 360 | 150 | 510 |
| Revision-aware reauthorization | 0/210 | 150/150 | 210/210 | 288 | 282 | 720 |

The full reauthorization condition retained zero false-ready decisions and matched
all 210 reference decisions. The revision-aware intermediate condition detected all
affected cases but did not classify the negative controls as `blocked`; that
difference is why the third condition remains analytically useful.

The Phase-4 split counts were 72 development, 54 robustness, 54 locked holdout,
and 30 locked compound holdout. The case-set digest was
`13c040f1d4ce779576230d4fce512ee1c6fadf3b2f8042317cc500afbfb377b5`, and the
structured reference-manifest digest was
`768babbb0442153e026783ede141d00ae8200d1befce0f1ed024cec70ec10925`.

## 6. Discussion

### 6.1 A passing current result did not preserve the old claim

The baseline condition could report a current pass while ignoring that the evidence
was tied to a different system revision. The issue was not that the stored result
was mathematically changed. The issue was that the result no longer covered the
decision being made.

Revision identity and evidence invalidation removed the false-ready decisions in
both matrices, but they did not resolve every decision. The negative controls still
required ownership, rollback, and escalation information. This is why the
intermediate condition matters: it shows that provenance alone is not the same as
organizational authorization.

### 6.2 Reauthorization added a measurable cost

The full condition required 60 versus 18 time units in the original pilot and 108
versus 30 in the robustness matrix. The study does not convert those units into
money or claim that the ratio will hold in production. It does show why a useful
release protocol must report its operational cost alongside its safety-relevant
outcomes.

### 6.3 What the study supports

Within the synthetic protocol, the implemented conditions produced the
pre-specified differences. The full condition exposed missing organizational controls
that the revision-aware evidence condition could not classify. The independent
reproduction confirms that the public merged artifacts produce the reported compact
outcomes from a clean checkout.

### 6.4 What the study does not support

The results do not establish that the protocol improves real production decisions,
that the reference oracle is universally correct, that the cases cover all agent
changes, or that the controls establish model safety. The study does not measure
hidden model state, live provider behavior, business impact, or human reviewer
agreement.

## 7. Limitations, ethics, and broader impacts

### 7.1 Limitations

The first limitation is external validity: all cases are synthetic and deterministic,
so the results may not transfer to real organizations without further validation.

The larger Phase-4 matrix improves coverage but does not change that limitation.
Its cases are varied metadata records rather than independent observations sampled
from deployed agents. The structured reference manifest is still a declared study
oracle, not an independent organizational review panel.

The reference decision is an explicit study oracle, not an independent organizational
decision-maker. A later reviewer study is needed to measure how different reviewers
interpret the same evidence.

The protocol tests bounded workflow changes. It does not cover every possible change
to model weights, hidden model state, external services, data distributions, or
organizational practice.

The cost counters are relative units. They allow conditions to be compared inside the
protocol but are not financial, latency, or staffing estimates.

### 7.2 Ethics and privacy

The completed phases use no human participants, private production data, provider
credentials, live model calls, or content-bearing payloads. The public artifacts
contain identifiers, classifications, counts, hashes, and synthetic decisions.

The next reviewer phase must be treated as a new study. A volunteer reviewer could be
recruited through a public LinkedIn call, but the study would need reviewer
instructions, consent language, privacy handling, sampling rules, and an agreement
analysis before responses are treated as research evidence.

### 7.3 Broader impacts

A reauthorization checklist can create false confidence if teams treat completion as
certification rather than as structured evidence for a decision. A protocol can also
over-block useful changes, delay releases, or shift responsibility without improving
the underlying system. These risks are why the study reports cost, preserves
`review_required`, and does not claim that a green report proves safety.

## 8. Reproducibility and artifact availability

The public artifact is split across two repositories by responsibility:

- [Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness)
  contains the executable synthetic scenarios, evaluator, reference manifest, and
  pilot commands.
- [LLM Eval Validity](https://github.com/julie-elkins/llm-eval-validity) contains the
  research question, protocol, compact result fixtures, analysis, paper, checklist,
  and research log.

The pilot and robustness commands run offline. The completed clean-checkout
reproduction used an isolated `uv` environment with Python 3.14.4. Historical phase
runs used `uv 0.11.8` and Python 3.11.15. No provider calls were made.

The original pilot is bound to harness source commit
`e75b35c41097efa550f7b23f4d6f1348af4696d9` and artifact merge commit
`fb3e004b4bdc27db777f1b3c8d23f2e76ec3ad17`. Its case-set hash is
`cf2a5661240cef17452bfb7217b9c91469f7590bd999490b99d648e6368c4ee3`.

The robustness result is bound to harness source commit
`f260b3a34df7b2ca3717af1225c79f99aeba7921` and artifact merge commit
`026e3e902c121ee334551b539879f4e835afe9b5`. Its case-set hash is
`bae8a87462aadb05ee1d6ade23d7e6e839be580cad5f8f29bf042d19b95740f2`.

The exact commands and compact outputs are recorded in
[RESULTS.md](RESULTS.md). The reporting checklist records the protocol, data
boundary, environment, limitations, and reproduction status.

The Phase-4 result is bound to harness source commit
`a6de7b03aaa516696978a656cbc651971cbc43bd` before merge. Its case-set digest is
`13c040f1d4ce779576230d4fce512ee1c6fadf3b2f8042317cc500afbfb377b5`, and its
reference-manifest digest is
`768babbb0442153e026783ede141d00ae8200d1befce0f1ed024cec70ec10925`.

## 9. Conclusion

A pass/fail result can remain technically correct while becoming insufficient
evidence for a changed agent workflow. In this deterministic synthetic study,
revision-aware evidence detected affected claims, and the full reauthorization
protocol additionally classified missing ownership, rollback, and escalation
controls. The full condition eliminated false-ready decisions on both the original
and held-out matrices, at the cost of additional bounded review and evaluation work.

The result is evidence for a protocol behavior, not a production-safety claim. Phase
4 makes the synthetic evaluation broader and more defensible, but the paper still
requires a system-level validation phase and, separately, a human-reviewer phase
before claims about real-world effectiveness or reviewer usability are appropriate.

## References

1. Measuring Agents in Production. arXiv:2512.04123.
   https://arxiv.org/abs/2512.04123
2. Provenance Integrity in Agentic Workflows. arXiv:2608.12761.
   https://arxiv.org/html/2608.12761
3. Are You Still the Agent I Authorized? arXiv:2607.23586.
   https://arxiv.org/abs/2607.23586
4. NeurIPS Paper Checklist.
   https://neurips.cc/public/guides/paper-checklist
5. ACM Artifact Review and Badging.
   https://www.acm.org/publications/policies/artifact-review-and-badging-current
6. Nature Reporting Summary.
   https://www.nature.com/documents/nr-reporting-summary.pdf
