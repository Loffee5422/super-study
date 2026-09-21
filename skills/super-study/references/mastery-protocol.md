# Mastery protocol

Use this protocol to open, steer, and close a learning contract.

## Scope

Build a dependency-aware map around common concepts, real-project difficulties, common failures, and transferable decisions. Include a narrow detail only when it materially affects the target job description, source project, or a likely engineering failure.

Classify each node as required, supporting, or extension. Required nodes block completion. Supporting nodes are learned only to the depth needed by a required node. Extensions do not block completion.

## Phases

1. **Broad probe**: ask one approachable question about the parent concept's problem or purpose in simple words. Recent reliable evidence can avoid repetition. Explicit unfamiliarity or a missing foundation routes directly to teaching.
2. **Teach**: give a connected, low-cognitive-load tutorial: problem/purpose, plain-language abstraction, causal mechanism, one consistent worked example, and only contract-required boundaries, misconceptions, or tradeoffs. Define only needed jargon and cover only blocking prerequisites.
3. **Supported check**: finish teaching with bullets for key takeaways, next learning, and quiz overview, then use one low-stakes supported check. Teaching or an assisted answer is learning evidence, not verified evidence.
4. **Diagnose**: for foundation-ready or familiar learners, ask for recall, prediction, tracing, or a concrete decision.
5. **Coach**: close a precise gap with the least help necessary; use the hint ladder only when foundations exist and the learner is close. Repeated unproductive attempts switch to teaching.
6. **Re-test**: use a different example after help or a supported check.
7. **Close-book**: remove hints and test the mechanism again.
8. **Interview**: apply continuous follow-ups, counterfactuals, and tradeoffs. Explicit mock interviews remain unhinted; record gaps for debrief.
9. **Teach-back**: require a coherent explanation and correction of likely misconceptions.

Ask at most one learning question per turn. Tutorials may ask zero questions and must not interrupt an explanation with guessing questions.

## Hint ladder

Track the highest help level used:

- `0`: no hint;
- `1`: identify the missing dimension;
- `2`: give a directional hint;
- `3`: reveal a key clue or intermediate step;
- `4`: give a short explanation.

An answer that required level 2–4 help is not mastery evidence. Re-test it in a new setting at level 0.

## Foundation and progress

Missing foundations, an explicit “I don't know,” or frustration bypass the hint ladder. A broad topic begins with the single broad probe above, then teaches when needed instead of creating a demotivating chain of failed questions.

Show a compact text bar at useful milestones, feedback, and pauses for the current concept's applicable required dimensions, using the existing evidence states. Example: `[██░░░] 2/5 项已验证｜阶段：练习｜下一步：解释机制`. Count only current material dimensions and exclude irrelevant extensions. Moving a dimension from `verified` to `needs-review` reduces the verified count while keeping the denominator unchanged. Explain denominator changes only when the agreed required-dimension scope changes; do not automatically add current-concept dimensions for prerequisite learning. “尚未评估” is not failure, and teaching is a distinct stage from mastery. A full bar requires current level-0 evidence for every required dimension, including transfer and sustained follow-ups. Reconstruct it from the evidence matrix; do not add a persisted numeric field.

## Evidence dimensions

Use only dimensions material to the contract, but default technical work to:

- recall and terminology;
- mechanism and causality;
- implementation or practical use;
- debugging and failure modes;
- alternatives and tradeoffs;
- security and operational consequences;
- communication and teach-back;
- novel transfer.

Store status as `unassessed`, `learning`, `verified`, or `needs-review`. Never average away a required weak dimension.

## Prerequisite detours

Open a prerequisite branch only when the learner cannot progress without it. Define the minimum exit test before entering the detour, satisfy that test, then return to the parent branch. Put valuable but non-blocking topics into the extension queue.

## Completion

Complete a contract only when every required node has current level-0 evidence across its material dimensions, including a novel transfer and sustained follow-ups. Recognition, repetition of a supplied answer, and learner confidence are not sufficient.

If the task pauses first, persist the unresolved node, current evidence, misconception or blocker, and the exact first test for resumption.
