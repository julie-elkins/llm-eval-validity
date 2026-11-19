# Response Quality Is Not Usable Evidence

## Evaluating Provider-Constrained Agent Workflows

**Status:** research manuscript draft. The study is descriptive and synthetic.
An anonymized ACL-formatted submission artifact exists separately; this
Markdown file is the source record for the protocol, analysis, and claims.

## Abstract

Provider-enforced structured output is often treated as a reliability
intervention for language-model agents. A response that satisfies a provider's
format, however, may still omit required evidence, claim completion without
support, or fail to handle uncertainty safely. This paper studies that gap
through a controlled comparison of prompt instructions plus local validation
against provider-enforced structured output plus the same local validation.

We evaluate a fixed 30-case synthetic matrix under six frozen conditions:
Claude Sonnet 5.5, Claude Haiku 5.5, and OpenAI `gpt-5.6`, each with a
prompt-only arm and, where run, a provider-structured arm. We separate protocol
acceptance from evidence-contract satisfaction and report both accepted-trace
and all-attempt denominators. Across the Claude configurations, structured
output reduced protocol acceptance and did not improve usable evidence. In the
OpenAI comparison, structured output slightly increased acceptance but reduced
evidence-contract satisfaction over all attempted cases.

We also conducted a separate blinded human calibration of the language-grounded
rubric. Two eligible reviewers judged the same 30-case packet, producing 60
response-level judgments. Decision and handling agreement were 100%; evidence
label agreement was 85%, with disagreements concentrated in empty-evidence
labeling and scope-sensitive wording. The results support a narrow conclusion:
provider-valid structure is not equivalent to usable assurance evidence, and
the evaluation instrument itself requires calibration. They do not establish
production safety, general model quality, provider-wide behavior, or user
outcomes.

## 1. Introduction

Language-model agents increasingly combine model responses, tool calls,
retrieved evidence, authorization checks, and bounded execution rules. In
these systems, a response can be syntactically valid while remaining
operationally unusable. It may contain the required JSON fields but fail to
show that the requested evidence was retrieved, that a side effect was
authorized, or that a claimed result actually occurred.

This paper examines one practical version of that problem: whether
provider-enforced structured output improves the end-to-end reliability of a
bounded agent workflow. Structured output means that the provider is asked to
constrain the response to a declared schema. Local validation means that the
application checks the returned trace against a separate evidence contract
after the provider interaction.

The distinction matters because the provider and the application answer
different questions. Provider validation asks whether the response can be
represented in the requested format. The local evidence contract asks whether
the trace contains the identifiers, operation state, and bounded metadata
needed to treat the result as usable evidence.

We ask:

> On a fixed set of evidence-grounded language tasks, does provider-enforced
> structured output improve usable end-to-end evidence compared with prompt
> instructions plus local validation, when the model, task, tools, budget,
> stopping rules, and evaluator scope are held constant?

The paper makes five contributions:

1. It separates protocol acceptance from evidence-contract satisfaction.
2. It reports both accepted-trace and all-attempt denominators.
3. It compares prompt-only and provider-structured conditions under matched
   task, tool, budget, and validation controls.
4. It reports a cross-model and cross-provider replication without turning the
   results into a provider ranking.
5. It treats human reviewer agreement as calibration evidence about the
   measurement instrument, not as automatic ground truth.

## 2. Scope and claim boundary

The study measures evidence-grounded response quality: whether a response
answers the declared task, uses the approved evidence, handles uncertainty
appropriately, and respects the declared refusal or escalation boundary.

It does not measure positive alignment, meaning whether an AI system promotes
human flourishing across broader social and value-sensitive settings. It does
not measure long-term user outcomes, real-user autonomy, pluralistic value
conflict, or user satisfaction. It also does not establish production safety,
general model quality, provider-wide performance, or causal superiority of
either implementation pattern.

The study's conclusions are therefore bounded by the declared models,
providers, schemas, prompts, task matrix, local validator, tool loop, and
synthetic evidence contract.

## 3. Related work

Prior work shows that agent evaluation is a measurement problem as well as a
modeling problem. Validity-centered evaluation frameworks distinguish a
construct from the decision made from its measurement. Work on agentic
benchmark construction shows that task setup, environment, reward design, and
reporting choices can over- or under-estimate performance. Studies of
LLM-as-a-judge identify position, verbosity, and preference biases, while
other work argues that model-based judgments require human grounding rather
than being treated as free ground truth.

Interactive agent benchmarks motivate evaluating tool calls, state changes,
authorization, and repeated interaction rather than scoring a final answer
alone. Work on variance and reliability motivates repeated conditions,
explicit refusal counts, and separation of protocol success from task success.
Research on simulated users and unreliable tool environments further supports
keeping synthetic interaction, human review, and real user outcomes distinct.

This paper builds on those lessons without claiming to implement a universal
benchmark checklist or a complete alignment evaluation. Its narrower
contribution is an end-to-end measurement design in which provider-valid
structure and evidence-backed task completion are separate outcomes.

Key references and the design connection for each are maintained in
[RELATED_WORK.md](RELATED_WORK.md).

## 4. Method

### 4.1 Evaluation unit

The evaluation unit is a bounded agent workflow consisting of a synthetic
task, approved evidence, a constrained tool interaction, a model response, and
local validation.

The task matrix contains ten synthetic scenarios with three replicates per
scenario. Scenarios include evidence-grounded summaries, conflicting or stale
sources, empty context, inappropriate answers, unauthorized side effects,
misleading tool output, tool misuse, and ambiguous side-effect retries.

The task content, raw responses, tool arguments, and answer key remain local.
The public artifact contains identifiers, aggregate counts, statuses, refusal
codes, and protocol metadata only.

### 4.2 Conditions

The primary comparison is:

| Condition | Description |
|---|---|
| Prompt plus local validation | Prompt instructions produce the response; the local adapter parses and validates the result. |
| Provider structured output plus local validation | The same workflow adds a provider-facing JSON Schema while retaining the same local parser and evidence validator. |

The intervention is the provider-facing output constraint. The local
validator is present in both conditions because a provider-valid response is
not by itself sufficient evidence.

The frozen provider conditions are:

- Claude Sonnet 5.5, prompt plus local validation;
- Claude Sonnet 5.5, provider structured output plus local validation;
- Claude Haiku 5.5, prompt plus local validation;
- Claude Haiku 5.5, provider structured output plus local validation;
- OpenAI `gpt-5.6`, prompt plus local validation; and
- OpenAI `gpt-5.6`, provider structured output plus local validation.

The OpenAI arms are reported separately from the Claude arms. They are not
pooled into a provider ranking.

### 4.3 Matched controls

Each condition attempted the same 30-case matrix with three replicates per
scenario. Conditions used the same bounded tool interaction, local validator,
refusal policy, and five-dollar planning ceiling per run. The OpenAI arms also
used the same three-turn ceiling.

No response-based reruns, prompt changes, schema changes, or case deletions
were selected after inspecting a result. Refusals and incomplete outcomes
remain part of the observed protocol behavior.

The pilot is descriptive. Thirty attempts per condition are sufficient to
expose protocol behavior in this fixture but are not sufficient to estimate a
production failure rate precisely or support population-level significance
claims. We report 95% Wilson score intervals, meaning bounded descriptive
uncertainty ranges for the observed proportions. Because the three replicates
within each scenario are related, a matched comparison must resample complete
scenarios rather than treat all 30 rows as independent.

### 4.4 Outcomes

The primary outcomes are:

1. **Protocol acceptance:** the local adapter completes the bounded provider
   interaction and records the required metadata without a refusal.
2. **Provider refusal:** the adapter cannot accept the provider response under
   the frozen interaction protocol.
3. **Evidence-contract satisfaction among accepted traces:** an accepted trace
   passes the local validator for the scenario's required classification,
   identifier, bounded operation state, and cost or retry fields.

We also report evidence-contract satisfaction over all attempted cases,
counting a refusal as not producing usable evidence. This denominator prevents
an accepted-trace comparison from hiding a condition that fails to produce a
usable result in the first place.

### 4.5 Human calibration

Phase 5 added a separate blinded review of the language-grounded rubric. Two
eligible human reviewers independently assessed the same 30-case synthetic
packet, producing 60 response-level judgments. The reviewers assessed
decision correctness, evidence support, and handling behavior without being
told which provider condition produced response A or B. Both reviewers
reported no AI assistance.

The human review is calibration, meaning a check of whether people apply the
rubric consistently. It is not a replacement for the local evidence contract,
and reviewer agreement does not create ground truth automatically.

The private intake recorded the packet version, form completeness, return
date, same-packet confirmation, and reviewer-reported provenance. The public
record contains only aggregate agreement and disagreement categories.

## 5. Results

### 5.1 Claude Sonnet 5.5

| Measure | Prompt plus local validation | Provider structured output |
|---|---:|---:|
| Attempted cases | 30 | 30 |
| Accepted traces | 28 (93.3%) | 22 (73.3%) |
| Provider refusals | 2 (6.7%) | 8 (26.7%) |
| Contract-satisfying accepted traces | 15/28 (53.6%) | 12/22 (54.5%) |
| Contract satisfaction over all attempts | 15/30 (50.0%) | 12/30 (40.0%) |

Structured output reduced protocol acceptance by 20.0 percentage points. Among
accepted traces, contract satisfaction was effectively unchanged (+0.9 points);
over all attempted cases, usable evidence fell by 10.0 points.

### 5.2 Claude Haiku 5.5 replication

| Measure | Prompt plus local validation | Provider structured output |
|---|---:|---:|
| Attempted cases | 30 | 30 |
| Accepted traces | 18 (60.0%) | 9 (30.0%) |
| Provider refusals | 12 (40.0%) | 21 (70.0%) |
| Contract-satisfying accepted traces | 9/18 (50.0%) | 3/9 (33.3%) |
| Contract satisfaction over all attempts | 9/30 (30.0%) | 3/30 (10.0%) |

The direction of the acceptance result replicated. Structured output reduced
acceptance by 30.0 percentage points and reduced contract satisfaction over all
attempts by 20.0 points. This is a within-provider replication, not a general
cross-model claim.

### 5.3 OpenAI cross-provider comparison

| Measure | Prompt plus local validation | Provider structured output |
|---|---:|---:|
| Attempted cases | 30 | 30 |
| Accepted traces | 26 (86.7%) | 27 (90.0%) |
| Provider refusals | 4 (13.3%) | 3 (10.0%) |
| Contract-satisfying accepted traces | 15/26 (57.7%) | 14/27 (51.9%) |
| Contract satisfaction over all attempts | 15/30 (50.0%) | 14/30 (46.7%) |

In this provider comparison, structured output increased protocol acceptance by
3.3 points but reduced contract satisfaction over all attempts by 3.3 points.
The result shows why protocol acceptance and usable evidence must be reported
separately. It is specific to the fixed model, schema, prompt, tool loop, and
synthetic matrix.

### 5.4 Descriptive uncertainty

The frozen aggregate counts are accompanied by 95% Wilson score intervals in
the statistical supplement. For example, Sonnet prompt-plus-local-validation
acceptance was 28/30, or 93.3% [78.7%, 98.2%], while structured-output
acceptance was 22/30, or 73.3% [55.6%, 85.8%]. Haiku
evidence-contract satisfaction over all attempts was 9/30, or 30.0%
[16.7%, 47.9%], compared with 3/30, or 10.0% [3.5%, 25.6%], under structured
output.

These intervals describe uncertainty in this fixed synthetic fixture. They do
not estimate a production rate or establish a population-level effect.

The study design is paired at the scenario/replicate level, but the public
artifact contains aggregate counts rather than the private case-level outcomes.
The paper therefore does not infer paired wins, losses, or ties from totals.
The required private-input contract is documented in
`PAIRED_ANALYSIS_SPEC.md`.

### 5.5 Human calibration result

| Field | Exact reviewer agreement |
|---|---:|
| Decision | 60/60 (100.0%) |
| Evidence | 51/60 (85.0%) |
| Handling | 60/60 (100.0%) |

After applying the pre-specified clarification rules, the evidence labels were
51 supported, 3 partially supported, and 6 not applicable. The nine evidence
disagreements were classified as:

- six empty-evidence label differences;
- two unsupported upper-bound differences; and
- one approval-versus-deployment paraphrase.

The reviewer result supports a measurement claim rather than a model claim:
the decision and handling fields were consistently applied on this packet,
while evidence-label interpretation still varied in scope-sensitive cases.

## 6. Discussion

The central result is that provider-valid structure did not guarantee usable
assurance evidence. Across the two Claude configurations, structured output
reduced acceptance and did not improve the usable-evidence rate among all
attempted cases. The OpenAI comparison shows the complementary case: acceptance
can improve slightly while end-to-end evidence satisfaction declines.

This pattern is operationally important. A system that counts parseable output
as success can report a healthy protocol while missing an unsupported
completion claim, a missing operation identifier, an unauthorized action, or
an unresolved evidence conflict. The local evidence contract catches a
different failure class from the provider schema.

The human calibration result adds a second caution. Even when two reviewers
agree on whether the decision and handling were appropriate, they can differ
on whether a response is fully supported, partially supported, or not
applicable. That disagreement is not noise to hide; it identifies where the
rubric needs sharper scope rules.

The practical design implication is to treat formatting, evidence, task
correctness, refusal, escalation, latency, and cost as separate evaluation
dimensions. A single quality score would allow one improvement to conceal a
failure in another dimension.

## 7. Limitations, ethics, and broader impacts

### 7.1 Limitations

The study has a small fixed matrix of synthetic cases. It does not estimate
production failure rates precisely, and it cannot establish how the results
transfer to live users, proprietary tools, or different providers, models,
schemas, prompts, or turn limits.

The public aggregate artifact does not support a paired effect estimate because
it omits the private case-level outcome for each scenario and replicate.
Aggregate totals cannot identify which matched cases changed between
conditions. The paired analysis is specified separately and must be run only
if the private metadata is recovered.

The accepted-trace denominator is subject to selection: a condition may look
stable among the traces it accepts while producing less usable evidence over
all attempts. We report both denominators to make that tradeoff visible.

The public artifact does not retain raw prompts, model responses, tool
arguments, or private traces. That boundary protects the evaluation packet but
means the public study cannot explain every provider refusal by inspecting
response content.

The human review used two eligible reviewers and one synthetic packet. Reviewer
agreement is not a universal validation of the rubric, and self-reported
absence of AI assistance is provenance information rather than independently
verified behavior.

### 7.2 Ethics and privacy

The study uses synthetic cases and does not include customer data, production
traces, unpublished certification content, credentials, or private business
decisions. Reviewer identities, contact information, completed forms, raw
comments, and the answer key remain outside the public repository.

The results should not be used to approve or reject a production deployment
without a separate evaluation of the relevant system, users, policies,
authorization boundaries, and failure consequences.

### 7.3 Broader impacts

Separating protocol success from evidence-backed task success can reduce false
confidence in automated release or review workflows. It can also expose more
refusals and escalations, which may increase operational cost or delay. The
appropriate response is not to suppress those failures; it is to make the
tradeoff visible and assign final authority to an authorized human or
governance process.

## 8. Reproducibility and artifact boundary

The public repository contains:

- the metadata-only task manifest;
- protocol and design decisions;
- frozen aggregate results;
- descriptive uncertainty analysis and the guarded paired-analysis contract;
- the [reproducibility appendix](REPRODUCIBILITY_APPENDIX.md);
- validation and analysis code that does not emit private content;
- reviewer process templates; and
- this manuscript draft.

The private research workspace contains raw task wording, paired responses,
answer keys, completed reviewer forms, and the private reconciliation record.
The public manuscript reports the aggregate evidence without publishing those
materials.

The executable companion is the
[Agent Assurance Harness](https://github.com/julie-elkins/agent-assurance-harness),
which contains reusable assurance patterns. The research repository remains
the source of truth for the study protocol, frozen results, and paper
interpretation.

## 9. Conclusion

Provider-enforced structured output is a formatting and interaction control,
not a guarantee that an agent produced usable evidence. In the frozen Claude
conditions studied here, structured output reduced protocol acceptance and did
not improve end-to-end evidence satisfaction. In the OpenAI comparison, a
small acceptance improvement coexisted with lower evidence-contract
satisfaction.

The study therefore recommends a layered evaluation design: retain provider
and local structural checks, validate evidence and task outcomes separately,
count refusals, report both accepted and all-attempt denominators, and
calibrate human-facing rubrics before treating them as measurement standards.

The next research step is not to claim a universal winner. It is to extend the
human calibration to broader, clearly defined task families and, where
appropriate, real-system or expert-rated settings while preserving the same
claim discipline.

## References

The complete literature crosswalk, with links and study-specific boundaries,
is maintained in [RELATED_WORK.md](RELATED_WORK.md). The principal referenced
works include:

- Measurement to Meaning: A Validity-Centered Framework for AI Evaluation.
- Establishing Best Practices for Building Rigorous Agentic Benchmarks.
- No Free Labels: Limitations of LLM-as-a-Judge Without Human Grounding.
- Quantifying Variance in Evaluation Benchmarks.
- Agent Evaluation Reliability: More Tasks Won't (Always) Fix an Agent
  Leaderboard.
- Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena.
- G-Eval: NLG Evaluation Using GPT-4 with Better Human Alignment.
- AgentBench: Evaluating LLMs as Agents.
- τ-bench: A Benchmark for Tool-Agent-User Interaction in Real-World Domains.
- Lost in Simulation: LLM-Simulated Users are Unreliable Proxies for Human
  Users in Agentic Evaluations.
