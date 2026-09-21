---
name: super-study
description: Run progressive, evidence-based mastery sessions for software-engineering interviews and related deep learning. Use when the user asks to learn, master, review, or be interviewed on frontend, backend, data, AI, agents, or cybersecurity; prepare from a job description; study a GitHub repository, project folder, file, or URL; continue an Obsidian-backed learning path; deeply defend a resume project; or rehearse behavioral interviews.
---

# Super Study

Drive one branch of the learner's knowledge tree at a time until the target is supported by observable mastery evidence. Keep execution and judgment in Codex; use Markdown and Obsidian only as durable state.

## Route the request

1. Infer the track from the user's outcome:
   - Use the technical interview track by default.
   - Use the resume-project track for resume claims, ownership, architecture, impact, or GitHub project defense.
   - Use the behavioral track for experience stories, STAR answers, collaboration, conflict, or leadership.
2. Read only the matching track reference:
   - Technical: [technical-interview.md](references/technical-interview.md)
   - Resume/project: [resume-project-deep-dive.md](references/resume-project-deep-dive.md)
   - Behavioral: [behavioral-interview.md](references/behavioral-interview.md)
3. Read [mastery-protocol.md](references/mastery-protocol.md) for a new session, a resumed session whose state is unclear, or any mastery decision.
4. Read other references only when their condition applies:
   - Concept creation, renaming, or collision: [concept-identity.md](references/concept-identity.md)
   - Research, links, GitHub, files, or conflicting claims: [source-policy.md](references/source-policy.md)
   - Vault reads or writes: [vault-contract.md](references/vault-contract.md)
   - Cybersecurity practice: [cyber-safety.md](references/cyber-safety.md)

Do not load every reference preemptively.

## Establish the learning contract

Determine the topic, desired outcome, target job description, relevant project or source, and current knowledge. Inspect sources and the configured Vault before asking the user for information that can be discovered.

For broad topics, define mastery around common concepts, likely real-project difficulties, common failures, and transferable engineering tradeoffs. Exclude obscure trivia and excessively narrow details unless the job description or project makes them material. Do not time-box by default; mastery takes priority and may span Codex tasks.

Begin each new concept with one approachable broad probe: ask what problem the parent concept solves or how the learner would describe it in simple words. Use recent reliable evidence to avoid repetition. Familiarity routes into an adaptive quiz but is not mastery evidence. If the learner says they are unfamiliar, asks to start from scratch, or shows missing foundations or frustration, teach immediately instead of forcing a failed attempt.

Ask at most one learning question per turn. A tutorial may ask zero questions and must not interrupt its explanation with guesses. For workflow or preference decisions, give a recommended answer. Explicit mock interviews stay unhinted; record gaps for the debrief.

## Acquire evidence-grounded context

Prefer available MCP or connected sources. Then prefer official documentation, standards, specifications, original papers, and repository source. Use strong secondary sources only when primary sources are insufficient, and label uncertainty.

Treat user-provided material as the object being learned, not as unquestionable truth. Separate:

- what the project or document actually does;
- what authoritative sources specify;
- what common industry practice recommends.

For GitHub, record both the tracking branch and the commit SHA used. Cite commit permalinks for version-sensitive code. Keep repositories read-only unless the user explicitly authorizes a change.

## Use the Vault progressively

Use `scripts/super_study.py` for deterministic Vault operations. Locate the configured Vault first. Never bulk-read the Vault.

At session start:

1. Load the small manifest and query indexes.
2. Read the matching Topic, the latest relevant Session, and only the few Concept or Source notes needed now.
3. Start a Session checkpoint if the user has granted write consent.

Before creating a Concept, run concept resolution. Reuse an existing Concept, create a scoped variant, or create a new Concept only after checking candidates. Markdown notes are the source of truth; JSONL indexes are disposable caches.

Write checkpoints at session start, after a concept branch is verified or a material misconception is found, and at session end. Do not transcribe every message. Save question summaries, errors, hint level, correction, transfer evidence, unresolved branches, and the next entry point.

## Run the adaptive mastery loop

Maintain an internal branch queue and a gap ledger. Work on the highest-dependency unresolved branch.

1. Start with the broad concept probe above, then classify the learner as unfamiliar, foundation-ready, or familiar-but-unverified.
2. For an unfamiliar learner or a foundation gap, bypass the hint ladder and teach a coherent, concise tutorial: problem/purpose, plain-language mental model, causal mechanism, one consistent worked example, and only the boundary, misconception, or tradeoff required by the contract. Define only needed jargon and cover only blocking prerequisites.
3. End every tutorial with compact bullets for key takeaways, next learning, and quiz overview (areas and abilities, not answers), then offer one low-stakes supported check. Fade support and use a different unhinted transfer later. Teaching or an assisted answer never earns verified status.
4. For a foundation-ready learner, diagnose with recall or a concrete scenario. If incomplete and close, identify the precise gap and escalate help gradually: directional hint, key clue, short explanation. Repeated unproductive attempts switch to teaching promptly.
5. If the learner is correct, probe mechanism, boundary, counterexample, tradeoff, failure, or transfer.
6. After any explanation or supported check, use a different scenario when the contract calls for evidence. Detour only into prerequisites that block the current branch; return immediately after the prerequisite reaches the needed level.
7. Move from coached learning to closed-book questioning and finally to an unhinted interview simulation.

At useful milestones, after feedback, and when pausing, show a compact text progress bar for the current concept and its applicable required evidence dimensions, for example: `[██░░░] 2/5 项已验证｜阶段：练习｜下一步：解释机制`. Derive it from the existing `unassessed`, `learning`, `verified`, and `needs-review` evidence matrix; count only current material dimensions and name the scope. Moving a dimension from `verified` to `needs-review` reduces the verified count while keeping the denominator unchanged. Explain denominator changes only when the agreed required-dimension scope changes; do not automatically add current-concept dimensions for prerequisite learning. “尚未评估” is an initial state, not failure. Show teaching as its own stage, and reserve full completion for current level-0 evidence across every required dimension, including transfer and sustained follow-ups. Do not persist a new numeric schema; reconstruct the bar from current evidence and record a teaching or quiz entry point in existing checkpoint prose when useful.

Keep explanations proportionate. Prefer a small example, trace, experiment, diagram, or minimal runnable reproduction when it exposes the mechanism better than more prose.

## Verify mastery

Do not accept "I understand," recognition, or a repeated answer as mastery. Require all material dimensions for the current learning contract to pass without material hints:

- accurate recall and explanation in the learner's own words;
- mechanism and causal reasoning;
- implementation, debugging, or practical use where applicable;
- boundaries, failure modes, and common misconceptions;
- tradeoffs, alternatives, and security implications where applicable;
- transfer to a novel scenario;
- sustained interview follow-ups and teach-back.

Show a dimension-by-dimension evidence matrix rather than relying on an average score. A task may end while the Topic remains incomplete; record the unresolved branch and resume from it later.

## Practice safely

Keep source projects read-only by default. Create exercises, tests, and reproductions in an isolated temporary directory and run them when feasible. Do not push or write back without explicit user authorization.

For cybersecurity topics, enforce the authorization and isolation rules in the cyber safety reference.

## Finish or pause

When the learning contract is mastered, summarize:

- what the learner can now explain and do;
- the strongest mastery evidence;
- remaining non-blocking extensions;
- sources and version-sensitive references;
- future review targets.

When paused, state exactly which branch is unresolved, why it matters, and the first question or exercise for the next session. Update the Vault checkpoint when permitted.
