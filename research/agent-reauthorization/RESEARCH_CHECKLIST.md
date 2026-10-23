# Research reporting and artifact checklist

This checklist keeps the pilot aligned with current computational-research reporting
practice. It remains with the public pilot paper so a reader can see which claims
are established, which are limited to the pilot, and which work remains.

The checklist is informed by the [NeurIPS paper checklist](https://neurips.cc/public/guides/paper-checklist),
the [ACM artifact review and badging guidance](https://www.acm.org/publications/policies/artifact-review-and-badging-current),
and the [Nature reporting summary](https://www.nature.com/documents/nr-reporting-summary.pdf).

## Status

| area | status | evidence or remaining work |
|---|---|---|
| Research question | complete | One primary question is stated in `RESEARCH_QUESTION.md`. |
| Hypotheses | complete | H1--H4 are written before the pilot result. |
| Scope boundary | complete | Synthetic, offline, metadata-only, no production-safety claim. |
| Baseline and intervention | complete | Three conditions are defined in `PROTOCOL.md`. |
| Case construction | complete for phases 1--4 | 18 pilot cases, 12 held-out compound-change cases, and 210 varied Phase-4 cases across six change families. |
| Decision reference | complete | The deterministic oracle is defined before condition outputs. |
| Randomness and seeds | not applicable to phases 1--4 | The study is deterministic. A future stochastic or LLM-backed phase must report seeds, model revisions, repetitions, and variance. |
| Primary outcomes | complete | False-ready decisions and stale-claim detection are defined before the run. |
| Statistical claims | complete for phases 1--4 | All synthetic phases report exact counts and do not use inferential statistics for synthetic cases. |
| Artifact availability | Phase 4 source committed; merge/reproduction pending | The Phase-4 harness implementation and structured reference manifest are committed on the feature branch; the validity fixture records the source commit and both case-set and manifest hashes. |
| Reproduction command | complete | The harness command is recorded in `RESULTS.md`. |
| Environment | complete for phases 1--4 locally | Historical runs used `uv 0.11.8` and Python 3.11.15; Phase 4 currently runs in the repository virtual environment with no provider calls. |
| Data availability | complete | Synthetic case definitions are public; no private traces or content-bearing payloads are used. |
| Limitations | complete | The paper states what the fixed synthetic matrix cannot establish. |
| Ethics and privacy | complete for phases 1--4 | No human participants, private data, or live provider interaction; a future volunteer study requires a new consent and privacy protocol. |
| Human reviewer study | not started | Requires a new protocol, consent and privacy review, reviewer sampling, and agreement analysis. |
| Broader impacts | complete for pilot paper | The paper addresses false confidence, over-blocking, release delay, and responsibility-shifting risks. |
| Robustness matrix | complete for phases 1--3; Phase 4 complete locally | Earlier held-out cases and the Phase-4 split-aware matrix pass their pre-specified controls. |
| Independent reproduction | complete for phases 1--3; pending for Phase 4 | Fresh clones reproduced the earlier matrices. Phase 4 requires a clean-checkout run after the harness change is merged. |
| LLM-backed system validation | not started | Requires a bounded agent, model or deterministic model substitute, tools, traces, independent evaluator, cost/latency ceilings, and a locked scenario set. |

## Claim discipline

The manuscript will keep these claims separate:

- **Observed:** the three implemented conditions produced the reported decisions on
  the fixed 18-case matrix.
- **Inferred within scope:** the additional controls changed the decision outcomes in
  this controlled pilot and exposed a measurable cost tradeoff.
- **Not established:** that the protocol improves real production decisions, generalizes
  to all organizations, or establishes model safety.

## Final pilot-paper requirements

The current paper package has:

1. a merged harness implementation;
2. a clean-checkout reproduction command;
3. matching case-set hash and source revision;
4. analysis output generated from the checked-in compact fixture;
5. a robustness phase and a larger Phase-4 matrix;
6. an updated limitations, ethics, and broader-impacts section; and
7. a final check that no content-bearing or private data entered the public artifact.

The LLM-backed and human reviewer studies are not required to validate the synthetic
protocol mechanics, but they are required before making claims about real-system
effectiveness or reviewer usability.
