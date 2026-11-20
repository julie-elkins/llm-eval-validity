# Related work and positioning

## Agentic Benchmark Checklist

The [Agent Evaluation Reliability paper](https://arxiv.org/abs/2610.00651)
introduces a checklist-oriented view of benchmark reliability, including task
validity, outcome validity, reporting quality, reproducibility, and controls
against misleading benchmark conclusions.

This study does not propose another checklist. It tests a layered review
protocol on matched cases and measures where each evidence layer changes the
decision.

## AgentDojo

[AgentDojo](https://github.com/ethz-spylab/agentdojo) provides dynamic
environments for evaluating attacks and defenses for tool-using agents. It
motivates realistic tool interactions, permission boundaries, and adversarial
cases.

This study uses those ideas as case-design inputs but focuses on claim support,
executable verification, and review validity rather than prompt-injection
defense performance.

## τ-bench

[τ-bench](https://arxiv.org/abs/2406.12045) evaluates tool-agent-user
interaction using policy following, tool use, database state, and repeated
success. Its repository also demonstrates why benchmark versioning and task
maintenance must be explicit.

This study carries forward the importance of final state, repeated trials, and
versioned cases while adding an evidence-provenance and human-adjudication
layer.

## Agent-generated research

[A Society of AI Scientists](https://www.alphaxiv.org/abs/2611.society-ai-scientists)
motivates the distinction between textual review, executable checks, and human
scientific judgment. Its reported executable checks do not by themselves prove
that a method, design, or interpretation is valid.

This study does not treat that report as ground truth. It uses the problem as
motivation for a controlled protocol whose defects and reference dispositions
are defined before execution.

## First-party evaluation guidance

The protocol is consistent with the task-specific evaluation and grading
guidance in:

- [Anthropic empirical performance evaluations](https://docs.anthropic.com/claude/docs/empirical-performance-evaluations)
- [OpenAI working with evals](https://platform.openai.com/docs/guides/evals)
- [OpenAI graders](https://platform.openai.com/docs/guides/graders)

The implementation remains provider-neutral. Provider APIs may be used only in
a separately approved arm; the offline protocol and analysis must not depend on
one vendor's evaluation service.
