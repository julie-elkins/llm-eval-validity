# ACL Rolling Review scope memo

## Status

**Decision: do not submit yet.**

The current `agent-reauthorization` manuscript is a strong synthetic governance
paper, but it is not the best ACL Rolling Review (ARR) candidate. ARR is the
review process for ACL-family computational language-processing research. The
current manuscript studies revision-aware release decisions over deterministic
metadata cases; it does not yet measure a language task or language-agent
behavior.

This memo selects the separate response-quality study as the ARR candidate and
defines the evidence required before submission.

## Candidate paper

**Working title:** Response Quality Is Not Usable Evidence: Evaluating
Provider-Constrained Agent Workflows

**Candidate repository:** `llm-eval-validity/research/response-quality/`

**Not the candidate:** `research/agent-reauthorization/paper.md` remains a
separate synthetic governance paper. It should not be broadened by inserting a
language experiment only to satisfy venue scope.

## Proposed contribution

The paper will study whether provider-enforced output structure improves the
end-to-end reliability of a language-producing agent workflow.

The contribution is not that structured output is good or bad in general. The
contribution is a measurement design that separates:

1. protocol acceptance, meaning whether the adapter can parse and complete the
   provider interaction;
2. evidence-contract satisfaction, meaning whether the trace contains the
   evidence required by the declared task;
3. language-task correctness and grounding, meaning whether the response
   answers the task and is supported by the allowed evidence;
4. repeated-run reliability, meaning whether the same task succeeds
   consistently rather than only on the best attempt; and
5. cost, latency, refusal, and escalation behavior.

The paper must show why a provider-valid response can still be an incorrect,
ungrounded, incomplete, or unusable answer.

## Research question

On a fixed set of evidence-grounded language tasks, does provider-enforced
structured output improve usable end-to-end evidence compared with prompt
instructions plus local validation, when model, task, tools, budget, stopping
rules, and evaluator scope are held constant?

## Required evidence before submission

The current frozen provider results are background evidence. The ARR candidate
needs a separately labelled language-grounded phase with:

- natural-language task inputs and responses;
- an explicit approved-evidence or grounding requirement;
- a task-level reference decision;
- an independent human review sample;
- a held-out set not used to tune the rubric or prompt;
- repeated runs on a stratified subset;
- task-level failure attribution;
- separate reporting for correctness, grounding, protocol acceptance, refusal,
  evidence completeness, cost, and latency;
- a public-safe artifact with no credentials, private traces, or reviewer
  identities.

The existing six provider conditions remain frozen. The new phase must not
replace, retune, or pool those results silently.

## Claim boundary

The paper may claim only what the language-grounded phase supports on its
declared tasks, models, conditions, and evidence contract.

It must not claim:

- general model quality;
- that structured output is universally better or worse;
- production safety;
- user satisfaction;
- provider-wide performance;
- that a deterministic harness result proves live-agent reliability; or
- that reviewer agreement creates ground truth automatically.

The paper should also state that evidence-grounded response quality is not a
complete positive-alignment evaluation. It does not measure human flourishing,
real-user autonomy, pluralistic value conflict, long-term user outcomes, or
the full governance conditions required for those claims. These are future
research surfaces rather than outcomes inferred from the frozen pilot.

## Submission-readiness gate

Do not submit until all of these are true:

- the language-grounded protocol is frozen before its results are inspected;
- the language task and reference standard are described in the main paper;
- the independent review process is complete or clearly labelled as a pilot;
- the paper is in the official ACL format;
- the paper and supplementary artifacts are anonymized;
- the related work is expanded beyond practitioner guidance;
- the Responsible NLP Checklist and AI-use disclosure are complete;
- author profiles and ORCID information are ready;
- the artifact can be reviewed without private repository access; and
- Ankit or another qualified researcher confirms that the contribution is
  substantively about language processing rather than only release governance.

## Recommended venue decision

If the language-grounded phase produces a clear, defensible result, prepare the
response-quality paper for ARR.

If the result remains primarily about deterministic release governance, keep
the reauthorization paper for an AI systems, software engineering, or AI safety
venue instead of forcing it into an NLP venue.
