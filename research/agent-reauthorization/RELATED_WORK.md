# Related work and positioning

This is a bounded positioning note, not a claim to have completed a systematic
literature review. The references below identify adjacent research areas that the
pilot must distinguish from its contribution.

## Current research areas

### Agent evaluation in production

Recent practitioner research reports that reliability is a leading development
challenge for deployed agents and that human evaluation remains common in production
practice. This supports the importance of the problem, but it does not by itself
specify how evidence should be maintained after a system change.

Reference: [Measuring Agents in Production](https://arxiv.org/abs/2512.04123).

### Continuous and evolving-agent evaluation

Recent work evaluates agents across changing software environments, skill revisions,
or long-running tasks. These studies are close to the proposed change-triggered
evaluation question.

The pilot differs by treating the output as an organizational decision record:
whether a prior claim may still authorize release or continued operation.

### Provenance and invalidation

Provenance means the traceable history behind a result. Recent work on provenance
integrity in agentic workflows records authority and fact dependencies and can
invalidate work affected by later changes.

Reference: [Provenance Integrity in Agentic Workflows](https://arxiv.org/html/2608.12761).

The pilot is adjacent but narrower in a different direction. It tests the decision
protocol that follows from stale or incomplete evidence, including ownership,
rollback, escalation, and human approval.

### Evidence and claim validity

Evaluation-validity research asks whether a score supports the conclusion drawn from
it. That is the conceptual foundation for this study.

The proposed study adds a temporal question: whether the evidentiary warrant survives
a defined revision to the system.

### Authorization under agent evolution

Research on evolving agents asks whether an agent remains within the authority it was
originally granted after it acquires tools, skills, or new workflows.

Reference: [Are You Still the Agent I Authorized?](https://arxiv.org/abs/2607.23586).

That work focuses on authority continuity. This pilot includes authorization as one
change family, but studies the broader release-evidence decision across prompts,
tools, data, evaluators, and deployment changes.

### Collective-state inference

Edward D. Clark's Collective-State Inference work asks how evidence can justify
inferences about a bounded collective state. That is a construct- and level-validity
question: whether the evidence supports interpreting observations as a claim about
the right kind of entity.

This pilot does not infer hidden collective or model state. It asks whether a
previously supported operational claim remains supported after the system revision.
Collective-state inference is therefore a conceptual neighbor, not the object of
this study.

## Contribution boundary

The paper should not claim novelty for any of these ideas in isolation:

- agent reliability evaluation;
- continuous evaluation;
- provenance;
- stale evidence;
- human approval;
- release gates; or
- measurement validity.

The proposed contribution is their tested connection:

> a revision-aware evidence record plus an explicit reauthorization protocol for
> deciding whether an AI-agent release or continued-operation claim remains
> supported after change.

## Claims the first pilot may support

If the protocol and implementation behave as designed, the paper may support claims
about:

- whether the three conditions produce different decisions on the synthetic case set;
- which change families the protocol catches;
- the cost of the additional controls;
- whether the negative controls are detected; and
- which parts of the protocol merit a larger study.

It may not support claims about all agents, all organizations, production safety, or
vendor-specific systems.
