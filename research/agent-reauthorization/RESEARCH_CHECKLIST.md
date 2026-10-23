# Research reporting and artifact checklist

This checklist keeps the pilot aligned with current computational-research reporting
practice. It remains with the public working paper so a reader can see which claims
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
| Case construction | complete | 18 fixed cases across six change families and three variants. |
| Decision reference | complete | The deterministic oracle is defined before condition outputs. |
| Randomness and seeds | not applicable to phases 1--3 | The study is deterministic. A future stochastic phase must report seeds and repetitions. |
| Primary outcomes | complete | False-ready decisions and stale-claim detection are defined before the run. |
| Statistical claims | complete for phase 1 | The pilot reports exact counts and does not use inferential statistics for synthetic cases. |
| Artifact availability | complete for phase 3 | The harness implementation and held-out reference manifest are merged on `main`; each result records its source commit and case-set hash. |
| Reproduction command | complete | The harness command is recorded in `RESULTS.md`. |
| Environment | complete for phases 1--3 and reproduction | Historical runs used `uv 0.11.8` and Python 3.11.15; the clean-checkout reproduction used an isolated `uv` environment with Python 3.14.4. No provider calls. |
| Data availability | complete | Synthetic case definitions are public; no private traces or content-bearing payloads are used. |
| Limitations | complete | The paper states what the fixed synthetic matrix cannot establish. |
| Ethics and privacy | complete for phases 1--3 | No human participants, private data, or live provider interaction. |
| Human reviewer study | not started | Requires a new protocol, consent and privacy review, reviewer sampling, and agreement analysis. |
| Broader impacts | next paper revision | Add the risk that a checklist can create false confidence if treated as certification. |
| Robustness matrix | complete for phase 3 | Twelve held-out compound-change cases pass the pre-specified controls. |
| Independent reproduction | complete for phase 3 | Fresh clones of harness `026e3e9` and validity `bcb8311` reproduced the case-set hash and all compact outcome fields. |

## Claim discipline

The manuscript will keep these claims separate:

- **Observed:** the three implemented conditions produced the reported decisions on
  the fixed 18-case matrix.
- **Inferred within scope:** the additional controls changed the decision outcomes in
  this controlled pilot and exposed a measurable cost tradeoff.
- **Not established:** that the protocol improves real production decisions, generalizes
  to all organizations, or establishes model safety.

## Artifact requirements before a final paper

Before calling the paper a completed study, the project must have:

1. a merged harness implementation;
2. a clean-checkout reproduction command;
3. matching case-set hash and source revision;
4. analysis output generated from the checked-in compact fixture;
5. a robustness phase or an explicit reason not to run one;
6. an updated limitations and broader-impacts section; and
7. a final check that no content-bearing or private data entered the public artifact.
