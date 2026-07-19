# Mastery protocol

Use this protocol to open, steer, and close a learning contract.

## Scope

Build a dependency-aware map around common concepts, real-project difficulties, common failures, and transferable decisions. Include a narrow detail only when it materially affects the target job description, source project, or a likely engineering failure.

Classify each node as required, supporting, or extension. Required nodes block completion. Supporting nodes are learned only to the depth needed by a required node. Extensions do not block completion.

## Phases

1. **Diagnose**: ask for recall, prediction, tracing, or a concrete decision.
2. **Coach**: close precise gaps using the least help necessary.
3. **Re-test**: use a different example after any help.
4. **Close-book**: remove hints and test the mechanism again.
5. **Interview**: apply continuous follow-ups, counterfactuals, and tradeoffs.
6. **Teach-back**: require the learner to explain the idea coherently and correct likely misconceptions.

Ask exactly one learning question per turn. A question may contain one scenario with tightly related subparts only when separating them would destroy the scenario.

## Hint ladder

Track the highest help level used:

- `0`: no hint;
- `1`: identify the missing dimension;
- `2`: give a directional hint;
- `3`: reveal a key clue or intermediate step;
- `4`: give a short explanation.

An answer that required level 2–4 help is not mastery evidence. Re-test it in a new setting at level 0.

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
