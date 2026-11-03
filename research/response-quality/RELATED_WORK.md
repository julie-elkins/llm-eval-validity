# Related work and positioning

This study sits at the intersection of evaluation validity, agent benchmark
design, judge reliability, and tool-environment evaluation. The papers below
inform the study's design, but none is treated as a universal production
standard.

## Literature crosswalk

| Work | Relevant lesson | Connection to this study | Boundary |
| --- | --- | --- | --- |
| [Measurement to Meaning: A Validity-Centered Framework for AI Evaluation](https://arxiv.org/abs/2505.10573) | Evaluation should connect a defined construct and decision to defensible evidence. | Supports treating the evidence contract and decision target as separate from provider-valid output. | This study measures a narrow synthetic workflow, not general construct validity for an organization. |
| [Establishing Best Practices for Building Rigorous Agentic Benchmarks](https://arxiv.org/abs/2507.02825) and its [Agentic Benchmark Checklist (ABC)](https://arxiv.org/abs/2507.02825) | Task setup, reward design, environment, and reporting errors can materially over- or under-estimate agent performance. | Supports fixed case matrices, explicit success conditions, bounded tool loops, declared denominators, and limitations. | The present matrix is a pilot, not a broad benchmark or leaderboard, and it does not claim the ABC or its CVE-Bench result. |
| [No Free Labels: Limitations of LLM-as-a-Judge Without Human Grounding](https://arxiv.org/abs/2503.05061) | Model-based grading needs human grounding and should not be treated as free ground truth. | Supports the independent reviewer calibration round and the separation of reviewer evidence from provider-condition results. | The study does not use an LLM judge as the sole reference standard. |
| [Quantifying Variance in Evaluation Benchmarks](https://arxiv.org/abs/2406.10229) | A reported difference is meaningful only relative to measurement variation. | Supports repeated conditions, explicit refusal counts, and cautious interpretation of small changes. | The frozen provider pilot is too small for broad inferential claims. |
| [Agent Evaluation Reliability: More Tasks Won't (Always) Fix an Agent Leaderboard](https://arxiv.org/abs/2610.00651) | More tasks do not automatically repair an unreliable measurement process. | Supports prioritizing evaluator and reviewer reliability before simply expanding the case count. | This study is not a leaderboard and does not estimate ranking stability. |
| [Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena](https://arxiv.org/abs/2306.05685) | LLM judges can show position, verbosity, and preference biases and should be compared with human preferences. | Supports explicit judge-bias probes and the independent reviewer round. | This study does not claim that a provider output constraint improves human preference. |
| [G-Eval: NLG Evaluation using GPT-4 with Better Human Alignment](https://arxiv.org/abs/2303.16634) | Rubric-guided model evaluation can align with human judgments while retaining evaluator-bias risks. | Supports treating rubric and judge behavior as part of the measurement instrument. | The present study does not use G-Eval or claim human-alignment equivalence. |
| [AgentBench: Evaluating LLMs as Agents](https://arxiv.org/abs/2308.03688) | Agent evaluation benefits from interactive environments rather than response-only scoring. | Supports treating tool loops and workflow evidence as part of the evaluation unit. | The current matrix is one bounded synthetic workflow, not a multi-environment benchmark. |
| [τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains](https://arxiv.org/abs/2406.12045) | Tool-using agents must be evaluated across interaction, policy, and state behavior. | Supports treating tool loops, authorization, operation state, and evidence as part of the evaluation unit. | The current study uses synthetic tool behavior and does not claim real-domain coverage. |
| [Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human Users in Agentic Evaluations](https://arxiv.org/abs/2601.17087) | Simulated interaction should not be silently treated as human-user evidence. | Supports the explicit distinction between synthetic cases, independent human review, and user-facing quality. | No simulated-user result in this study is presented as a user-outcome claim. |
| [Beyond Function Calling: Benchmarking Tool-Using Agents under Tool-Environment Unreliability](https://arxiv.org/abs/2606.25819v1) | Tool and environment unreliability can change agent behavior independently of model capability. | Supports recording environment and tool conditions as part of the evidence boundary. | The present pilot does not estimate behavior across a real tool-environment fault distribution. |

## Positioning

The contribution here is narrower than a new general benchmark. The study
tests whether provider-enforced structured output changes trace acceptance and
local evidence-contract satisfaction under a fixed synthetic workflow, with
accepted-trace and all-attempt denominators reported separately.

The independent reviewer study is a measurement-quality check, not a claim
that the provider arms are safe, accurate, or production-ready. The frozen
provider results remain unchanged while the reviewer instrument is versioned
and calibrated.

Public artifacts contain only sanitized concepts and synthetic evidence. The
research record does not depend on private implementation details.
