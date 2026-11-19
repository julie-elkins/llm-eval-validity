# From Correct Answers to Learning Evidence: Designing AI-Assisted Assessment Around Independent Transfer

## Abstract

Generative AI makes final-answer correctness an incomplete basis for assessing
learning. A learner and an AI system can produce a correct or fluent response
without showing that the learner can justify the answer, evaluate evidence, or
apply the target skill independently. This paper asks whether an
evidence-aware assessment view can distinguish those cases more defensibly
than a final-answer-only view.

We present a controlled, metadata-only synthetic study that operationalizes
independent transfer as performance on a matched task completed without AI
assistance. The executable phase contains 30 cases repeated across seven
failure classes: correct answers with wrong justifications, fluent but
unsupported claims, stale or contradictory evidence, missed uncertainty
boundaries, missing constraints, and polished negative controls, alongside
evidence-supported cases. Each case is evaluated under two matched views. The
final-answer-only view sees the task and answer. The evidence-aware view also
sees declared evidence fields, verification signals, and bounded workflow
metadata. A private reference disposition identifies whether the constructed
case supports an independent-learning inference.

The final-answer-only view agreed with the synthetic reference on 5 of 30
cases (16.7%; 95% Wilson interval [7.3%, 33.6%]). The evidence-aware view
agreed on 30 of 30 cases (100.0%; [88.6%, 100.0%]). These are controlled
measurement results, not learner outcomes: no participants, learner records,
or live provider calls were used. The contribution is a reproducible design
for testing whether assessment evidence supports a learning interpretation
before a human-validation phase. We identify the ethics, privacy, transfer,
and missing-data gates required before such a phase can begin.

## 1. Introduction

Generative AI changes what an assessment response can mean. A correct answer
may reflect a learner's understanding, an AI-generated solution, a partially
understood explanation, or a response assembled from evidence the learner
cannot independently evaluate. Fluency increases the risk because a polished
response can appear more defensible than the evidence warrants.

The central problem is interpretive. An evaluator may be asked to infer
independent competence from an AI-assisted performance, even though the
observed response only establishes that a learner and an AI system produced a
plausible result together. The evidence needed for the first interpretation is
stronger than the evidence needed for the second.

This paper studies a narrower question before attempting a human-participant
study:

> Can an evidence-aware assessment view detect constructed cases where a
> correct-looking or fluent response is insufficient to support an inference
> of independent learning?

We operationalize independent learning evidence as success on a matched
transfer task completed without AI assistance. This is an operational
definition, meaning a measurable rule used for the study, not a claim that
one transfer task fully captures durable learning.

The study makes four contributions:

1. It separates final-answer correctness from evidence sufficiency.
2. It defines a matched comparison between final-answer-only and
   evidence-aware assessment views.
3. It provides a 30-case, metadata-only synthetic protocol covering seven
   planted failure classes.
4. It records the ethics and privacy boundary required before human validation.

The study does not claim that AI assistance improves learning, that synthetic
cases equal learners, or that the evidence-aware view is validated for a
student population.

## 2. Background and research gap

Assessment validity concerns whether the evidence supports the interpretation
made from an assessment result. A correct answer can support a narrow
interpretation of task correctness while failing to support a stronger
interpretation of durable understanding or independent competence.

Generative AI makes that distinction more important. When AI assistance is
available, a final product may be a joint human-AI artifact. Assessment
designs therefore need to consider process evidence, learner reflection,
verification, and transfer rather than treating the final answer as a complete
measurement of learning.

The linked special collection, *Reimagining Assessment for Learning in the Age
of Generative AI*, emphasizes evidence beyond final products, construct
validity, learner agency, self-regulation, and the temporal dimension of
durable learning. This study addresses the evidence problem directly while
remaining intentionally smaller than a human learning study.

Relevant foundations include evidence-centered assessment, metacognitive
support, learning analytics, and human-centered educational AI. The related
work map is maintained in
[`RELATED_WORK.md`](RELATED_WORK.md), including the collection call, UNESCO
guidance, and recent work on metacognitive requirements and assessment under
generative AI.

The gap is not simply a lack of another answer benchmark. It is the need to
test whether an assessment workflow preserves enough evidence to justify the
interpretation it makes. This study connects that question to independent
transfer without claiming that the current synthetic phase observes learning.

## 3. Research questions and claim boundary

### 3.1 Primary research question

Can an evidence-aware assessment view detect planted cases where a
final-answer-only view would incorrectly support an inference of independent
learning?

### 3.2 Secondary questions

1. Which evidence failures are most likely to be hidden by final-answer
   correctness or fluency?
2. Does evidence-aware evaluation identify uncertainty and escalation
   boundaries that answer-only evaluation misses?
3. Can the protocol produce a reproducible basis for later human validation?

### 3.3 Claim boundary

The synthetic phase may support:

- a documented comparison of two assessment views;
- a taxonomy of constructed evidence failures;
- a feasibility result for the proposed evidence contract; and
- a protocol for a later human-validation study.

It may not support:

- a claim that real learners learned or failed to learn;
- a claim that AI assistance improves learning;
- a population estimate or treatment effect;
- a claim that the rubric is valid for students generally; or
- a ranking of AI systems, tutors, or educational architectures.

## 4. Method

### 4.1 Study design

The current phase is non-participant and offline. It uses 30 public
metadata-only cases and a private reference disposition for each case. The
cases are repeated across seven planted failure classes. Five cases represent
supported evidence; five represent correct answers with wrong justifications;
and four cases represent each of five additional failure classes.

The repetitions are controlled robustness checks. They are not independent
learner observations, and the study does not treat the resulting intervals as
population estimates.

### 4.2 Synthetic assessment unit

Each case contains only metadata:

- task identifier and task family;
- planted case class;
- replicate number;
- answer signal;
- evidence signal;
- public reason code; and
- the observed disposition under each evaluator view.

The public artifact contains no learner answer, raw prompt, raw provider
response, answer key, reviewer identity, or participant data. The private
reference disposition is the expected classification for the constructed case.
It is ground-truth-like within the fixture, not a human learning outcome.

### 4.3 Task families and failure classes

The task manifest covers concept application, evidence interpretation, and
procedure or troubleshooting. The cases cover:

1. evidence-supported performance;
2. correct answer with wrong justification;
3. fluent but unsupported performance;
4. stale or contradictory evidence;
5. ambiguity requiring uncertainty or escalation;
6. a missing required boundary or constraint; and
7. a polished negative control.

These classes are deliberately selected to separate correctness, evidence
alignment, verification, uncertainty handling, and independent-transfer
interpretation.

### 4.4 Matched evaluator views

Both views receive the same case set and the same evaluation target.

The final-answer-only view has access to the task and submitted answer. It
cannot inspect declared evidence fields or workflow metadata.

The evidence-aware view has access to the same task and answer plus declared
evidence fields, verification signals, and bounded workflow metadata. It is
not allowed to infer missing evidence from fluent wording.

The difference between the views is the evidence available to the evaluator,
not a change in the case, task family, or reference disposition.

### 4.5 Independent transfer criterion

In the future human phase, independent transfer means solving a matched task
without AI assistance after the assisted task. The transfer task must test the
same target skill while changing surface form, values, context, or required
application. It must not be a memory test that rewards repeating the original
answer.

The current synthetic phase does not run that task with a person. Its private
reference disposition only represents what the constructed case says about the
transfer inference.

### 4.6 Analysis

The primary outcome is agreement between each evaluator view and the private
synthetic reference disposition. We report:

- agreement and disagreement counts;
- disposition counts;
- agreement by case class;
- false-supported cases;
- uncertainty or not-assessable cases; and
- 95% Wilson intervals, which are bounded descriptive uncertainty ranges for
  proportions.

The analysis does not pool repeated cases as if they were learners. It reports
the repeated classes explicitly and treats the result as a controlled
measurement demonstration.

## 5. Results

### 5.1 Overall agreement

| Evaluator view | Cases | Agreement | 95% Wilson interval |
|---|---:|---:|---:|
| Final-answer-only | 30 | 5/30 (16.7%) | [7.3%, 33.6%] |
| Evidence-aware | 30 | 30/30 (100.0%) | [88.6%, 100.0%] |

The final-answer-only view marked 26 cases as supported and four as unclear.
It agreed with the reference on the five evidence-supported cases but failed
to support the reference disposition for all 25 constructed cases whose
evidence was insufficient, contradictory, or required escalation.

The evidence-aware view marked five cases as supported and 25 as not
supported. It matched the private reference disposition on every case in this
controlled fixture.

### 5.2 Case-class results

| Case class | Cases | Final-answer-only agreement | Evidence-aware agreement |
|---|---:|---:|---:|
| Evidence supported | 5 | 5/5 | 5/5 |
| Correct answer, wrong justification | 5 | 0/5 | 5/5 |
| Fluent but unsupported | 4 | 0/4 | 4/4 |
| Stale or contradictory evidence | 4 | 0/4 | 4/4 |
| Ambiguous; requires uncertainty | 4 | 0/4 | 4/4 |
| Missing required boundary | 4 | 0/4 | 4/4 |
| Polished negative control | 4 | 0/4 | 4/4 |

### 5.3 What the result demonstrates

The result demonstrates that a final answer can be correct or fluent while
still failing the evidence contract needed for a stronger interpretation.
Making evidence fields and verification signals visible allowed the
evidence-aware view to reject every planted unsupported inference in this
fixture.

The result does not demonstrate that a learner would receive the same
classification, that the transfer disposition predicts durable learning, or
that the evidence-aware view would perform identically with real participant
data.

## 6. Failure cases and design implications

The correct-answer-wrong-justification class shows why answer correctness and
evidence alignment are different outcomes. The answer can be right while the
reason offered for it is irrelevant or unsupported.

The fluent-but-unsupported and polished-negative-control classes show why
presentation quality cannot substitute for evidence. A polished explanation
can increase confidence without increasing validity.

The stale-or-contradictory and ambiguity classes show why assessment needs
uncertainty handling. A safe evaluation should be able to say that the
evidence is insufficient or that escalation is required.

The missing-boundary class shows why process constraints matter. An answer may
appear correct while failing a declared condition that limits whether the
answer is usable.

Together, these failures support a design recommendation: assessment systems
should preserve the evidence needed for the interpretation they make and
should separate correctness, support, verification, uncertainty, and transfer.

## 7. Discussion

The narrow finding is that evidence-aware evaluation can be more discriminating
than final-answer-only evaluation in constructed cases designed to expose
unsupported inferences. This is a measurement result. It does not make the
evidence-aware view a validated educational instrument.

The result also shows why assessment design should not treat process traces as
automatic proof. Evidence fields can be missing, misleading, or incorrectly
interpreted. A future human study must therefore evaluate the evidence
contract itself, calibrate reviewers, preserve missingness, and compare the
assessment inference with an independently observed transfer outcome.

The study complements the companion workflow-reliability paper. That paper
asks whether a bounded AI workflow produces usable evidence after a provider
interaction. This paper asks whether the evidence is sufficient for an
educational interpretation about independent learning. The shared principle is
that a well-formed or plausible output is not automatically evidence for the
stronger claim a system may make from it.

## 8. Ethics, privacy, and future human validation

The current phase uses synthetic metadata only. It includes no participants,
learner records, private certification material, customer data, production
traces, credentials, or high-stakes decisions.

A human-validation phase must not begin until the protocol is reviewed for
consent and ethics requirements, task and transfer forms are frozen, the
primary analysis is locked, and an institution or qualified review body
determines whether review, exemption, or another approval route is required.

If approved, the future phase should recruit adults only, collect the minimum
data needed, separate identity from response records, preserve the AI-use
boundary, and make participation unrelated to employment, certification, or
academic consequences.

## 9. Limitations

The 30 cases are constructed and repeated across seven classes. They provide a
broader feasibility matrix than the original seven-case demonstration but are
not a sample of learners. The Wilson intervals describe the constructed
fixture and should not be read as population uncertainty.

The private reference disposition is designed by the study protocol. It is not
independent human ground truth. The evidence-aware view can match the reference
because the case was constructed to expose the evidence failure the rubric
defines.

The study does not measure delayed transfer, retention, learner agency,
metacognition, self-regulation, fairness across populations, or the effects of
AI assistance on learning. Those require a separately approved human study.

## 10. Reproducibility and artifact boundary

The public repository contains the protocol, task-family metadata, 30-case
synthetic fixture, evaluator views, analysis code, tests, aggregate results,
and claim boundary. The private workspace contains the reference disposition
file and any future participant materials.

The repository does not publish raw prompts, raw answers, answer keys,
participant identities, completed forms, provider traces, or credentials. The
offline run is reproducible with:

```bash
make validate-assessment-tasks
make run-synthetic-assessment
```

## 11. Conclusion

Assessment in the age of generative AI must distinguish a correct answer from
evidence that a learner can apply the target skill independently. In this
controlled synthetic phase, a final-answer-only view matched the reference on
5 of 30 cases, while an evidence-aware view matched it on all 30. The result
supports a limited measurement-design hypothesis: evidence preservation can
expose unsupported learning inferences that final-answer correctness hides.

The next step is not to claim that AI improves learning. It is to obtain the
appropriate ethics determination, freeze the human-validation protocol, and
test whether the same evidence boundary remains useful when real adults
complete bounded assisted and independent-transfer tasks.

## References and source map

- [Reimagining assessment for learning in the age of generative AI](https://link.springer.com/collections/eeigbjiafi)
- [How Adding Metacognitive Requirements in Support of AI Feedback in Practice Exams Transforms Student Learning Behaviors](https://arxiv.org/html/2505.13381)
- [Reimagining Assessment in the Age of Generative AI](https://arxiv.org/abs/2605.12363)
- [UNESCO Guidance for generative AI in education and research](https://www.unesco.org/en/digital-education/artificial-intelligence)
- [National Academies: Testing, Teaching, and Learning](https://nap.nationalacademies.org/read/9609/chapter/6)
