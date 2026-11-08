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
| [Measuring AI Ability to Complete Long Software Tasks](https://arxiv.org/abs/2503.14499) | Long-horizon capability should be reported with a task-duration baseline and more than one reliability threshold. | Provides the framework for a future extension that measures completion duration, 50% versus 80% reliability, recovery, and failure location. | The present pilot uses a fixed bounded interaction and does not estimate a task-time horizon. |
| [A Live Benchmark and Automated Evaluation for Generative Research Synthesis](https://arxiv.org/abs/2508.20033) | Research synthesis can be evaluated through knowledge synthesis, retrieval quality, and citation verifiability. | Supports treating evidence completeness and claim support as separate from parseable or provider-valid output. | The present study does not evaluate literature retrieval or generated research reports. |
| [Do Agent Benchmarks Measure Capability? Protocol Validity in the Age of Agentic AI](https://arxiv.org/abs/2607.22368) | A benchmark can overstate capability when the protocol or scoring rule permits shortcuts around the intended task. | Directly supports the local evidence contract, negative controls, explicit failure states, and the distinction between a passing event and the declared construct. | The present study tests one bounded protocol; it does not estimate validity across agent benchmarks. |
| [Towards a Science of AI Agent Reliability](https://arxiv.org/abs/2602.16666) | Reliability includes distinct properties such as consistency, robustness, predictability, and safety rather than one undifferentiated score. | Supports reporting protocol acceptance, evidence satisfaction, refusal, and limitations as separate measures. | The pilot does not estimate the full reliability profile of an agent or model. |
| [GDPval: Evaluating AI Model Performance on Real-World Tasks](https://openai.com/index/gdpval/) | Professional-task evaluation can compare model outputs with work from domain experts and expose context and subjectivity effects. | Provides a contrast class for future work: expert-rated task quality is different from protocol acceptance and evidence-contract satisfaction. | This study uses synthetic assurance cases, not economically valuable professional tasks or expert win rates. |
| [WildClawBench: A Benchmark for Real-World, Long-Horizon Agent Evaluation](https://arxiv.org/abs/2605.10912) | Native-runtime, multimodal, long-horizon environments expose failure surfaces that bounded synthetic cases cannot represent. | Supports stating the synthetic environment boundary and naming real-runtime replication as future work. | The present artifact intentionally does not claim native-runtime or multimodal coverage. |
| [DEER: A Benchmark for Evaluating Deep Research Agents on Expert Report Generation](https://arxiv.org/abs/2512.17776) | Deep-research evaluation can combine expert rubrics with claim-level verification. | Offers a possible future comparison if the project expands from workflow evidence to research-report quality. | It is not needed to interpret the current provider-output experiment. |
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

## Scope map for the next phase

The lecture and newer literature identify adjacent measurement surfaces that
should remain separate from the frozen provider comparison:

| Measurement surface | What it would add | Status here |
| --- | --- | --- |
| Protocol validity | Whether the test and scoring rule require the capability they claim to measure. | Partially represented by the evidence contract and negative controls; not a benchmark-wide validity study. |
| Long-horizon reliability | How task duration changes as the required reliability threshold rises. | Future study; not measured by the 30-case provider arms. |
| Trajectory failure analysis | Where planning, tool choice, reasoning, abandonment, looping, recovery, or final-state verification failed. | Some bounded failure states are present; raw trajectories are intentionally not public. |
| Professional-task quality | Whether expert reviewers consider an output good enough for real work. | Out of scope for this paper. |
| Research synthesis quality | Whether retrieved sources are relevant and whether citations support claims. | Out of scope for this paper; a possible separate lab. |
| User outcomes | Whether real users achieve better results with the system. | Not measured; synthetic cases and independent reviewers are not user-outcome evidence. |

## Adjacent future directions from self-improving-agent research

The [Stanford CS329A Part 9 lecture on future research areas](https://www.youtube.com/watch?v=AyO6wyu4DEg&list=PLangBM27OtEA&index=9)
identifies several useful extensions without changing this paper's research
question:

- **Diversity:** measure whether generated reasoning or candidate trajectories
  remain meaningfully diverse rather than repeating one failure mode.
- **Verifier validity:** test whether a verifier catches real errors and whether
  a meta-verifier can detect fabricated or unsupported verifier findings.
- **Synthetic curriculum quality:** record task difficulty, validity,
  deduplication, held-out separation, and reward-hacking controls when an agent
  proposes its own evaluation tasks.
- **Resource-normalized evaluation:** keep quality, safety, latency, cost,
  energy, and privacy separate when comparing local, cloud, or hybrid execution.
- **Continual-learning boundaries:** distinguish memory retrieval, in-context
  learning, and weight updates, then test stale, contradictory, and unsafe
  carry-forward state.

These directions belong in a future study or teaching extension. They should
not be folded into the frozen provider comparison, because doing so would
change the construct being measured.
