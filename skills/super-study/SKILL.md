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

Ask one question at a time. For workflow or preference decisions, give a recommended answer. For knowledge checks, do not reveal the answer before the learner attempts it.

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

1. Diagnose with recall or a concrete scenario.
2. If the learner is correct, probe mechanism, boundary, counterexample, tradeoff, failure, or transfer.
3. If incomplete, identify the precise gap without giving the answer.
4. Escalate help gradually: directional hint, key clue, short explanation.
5. After any explanation, test again with a different scenario.
6. Detour only into prerequisites that block the current branch; return immediately after the prerequisite reaches the needed level.
7. Move from coached learning to closed-book questioning and finally to an unhinted interview simulation.

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
