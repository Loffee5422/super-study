# Architecture

Super Study separates adaptive execution from durable state. Codex performs retrieval, questioning, judgment, and teaching. Markdown stores compact evidence that can survive across tasks and remain readable in Obsidian or any text editor.

## Design goals

1. Keep the always-loaded Skill instructions small.
2. Load only the learning track and policies required by the active request.
3. Prevent duplicate concepts without scanning the full Vault into context.
4. Preserve resumable evidence instead of full conversation transcripts.
5. Keep user projects read-only and local learning data private by default.

## Runtime layers

| Layer | Responsibility | Source of truth |
| --- | --- | --- |
| Codex | reasoning, retrieval, questioning, evaluation, adaptation | current task context |
| `SKILL.md` | routing, core learning loop, safety and completion behavior | installed Skill |
| `references/` | track-specific and conditional protocols | installed Skill |
| `super_study.py` | deterministic Vault reads, writes, IDs, indexes, and validation | installed Skill |
| Obsidian Vault | durable learning targets, concepts, sessions, sources, and evidence | Markdown notes |
| JSONL indexes | fast candidate lookup and compact navigation | disposable cache |

## Progressive reference loading

The base `SKILL.md` routes requests into one of three tracks:

- technical interview;
- resume/project deep-dive;
- behavioral interview.

Conditional references are loaded only when needed. Concept identity is consulted for creation or collision; source policy is consulted when research or user material is involved; the Vault contract is consulted only for durable state operations; cyber safety is consulted for security practice.

This routing prevents the complete protocol library and Vault from being imported on every use.

## Adaptive mastery loop

Codex maintains an internal branch queue and a gap ledger. The highest-dependency unresolved branch is tested first. A correct answer increases depth rather than ending the branch: mechanism, counterexample, failure, tradeoff, implementation, security, or transfer is probed next.

Help escalates through directional hints, key clues, and short explanations. Any explanation is followed by a new test in a different scenario. Mastery requires unhinted evidence across every material dimension of the learning contract.

## Durable data model

- **Target:** job description or interview outcome.
- **Topic:** bounded learning map connected to a Target and Sources.
- **Concept:** reusable canonical knowledge unit with aliases and a stable ID.
- **Session:** append-only checkpoints containing questions, misconceptions, hint level, evidence, unresolved branches, and the next test.
- **Source:** versioned evidence such as a URL, document, repository branch, or Git commit.

Concepts are not nested folders. Relationships such as broader concepts, prerequisites, topics, and aliases live in structured frontmatter and links. This allows a concept to serve multiple topics without duplication.

## Concept identity and deduplication

Before creation, the CLI resolves candidates from a compact index using normalized names, aliases, domains, and summaries. The decision is explicit:

1. reuse an existing canonical concept;
2. create a scoped variant when the same term has distinct meanings;
3. create a new stable identity only when no existing concept matches.

Markdown remains authoritative. Indexes can be deleted and rebuilt with `reindex`, so a cache failure cannot corrupt the learning record.

## Context budget

At resume time, the CLI returns paths to a small manifest, the relevant Topic, the latest Session, and a limited number of matching Concepts or Sources. Codex reads only those files. The Vault can grow across domains without making every task expensive.

## Repository and Vault boundary

This public repository contains reusable Skill logic, protocols, scripts, and blank templates. It deliberately excludes:

- the user's Vault;
- learning history and interview targets;
- local configuration and consent state;
- private repositories or source snapshots;
- credentials and connector tokens.

## Extension model

New learning modes should usually be added as a focused reference routed from `SKILL.md`, not by expanding the always-loaded core. A new track should define its diagnostic dimensions, evidence requirements, failure modes, and completion criteria while reusing the shared mastery and source protocols.
