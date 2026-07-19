# Vault contract

Use the bundled CLI for deterministic operations. Markdown notes are authoritative; `.super-study/*.jsonl` files are derived caches.

## Progressive reads

Never read every Vault file. Resolve the configured Vault, load `.super-study/manifest.json`, query the indexes, then read only:

- the current Topic;
- the latest relevant Session;
- a small set of Concept candidates;
- Source notes needed by the current branch;
- a matching job-description Target when applicable.

## CLI

Run `scripts/super_study.py` with an available Python 3 runtime.

Common commands:

```text
configure --vault PATH --consent
init
status
resolve-concept QUERY --limit 5
create-concept --name NAME --domain DOMAIN --summary SUMMARY
create-topic --name NAME --domain DOMAIN --summary SUMMARY
create-source --title TITLE --source-type TYPE
create-target --role ROLE --company COMPANY --source URL
start-session --track TRACK --topic TOPIC
checkpoint --session PATH --phase PHASE --summary SUMMARY
set-mastery --note PATH --dimension DIMENSION --state STATE
reindex
validate
```

Use `--vault PATH` or `--config PATH` to override configuration. Do not expose config contents if they could reveal unrelated filesystem information.

## Writes

Obtain first-use consent before writing a Vault. Checkpoint at session start, after a verified concept branch or material misconception, and at pause or completion. Do not write every chat message.

Store compact structured evidence: question summary, answer summary, misconception, highest hint level, correction, level-0 transfer evidence, unresolved branch, and next test. Do not store full transcripts.

Before creating a Concept, resolve candidates. After material changes, run `reindex` and `validate`. Never overwrite an existing note or user content during initialization. Do not edit `.obsidian` settings.

## Navigation

Human navigation lives in `00 Home` and domain maps. Codex navigation lives in the manifest and JSONL indexes. Regenerate marked index sections without replacing human-authored text outside the markers.
