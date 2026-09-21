# Contributing to Super Study

Contributions should improve observable learning outcomes while keeping the core Skill compact, safe, and maintainable.

## Good contributions

- reproducible failures in routing, questioning, mastery decisions, or Vault operations;
- clearer evidence requirements and interview follow-ups;
- high-frequency software engineering scenarios grounded in authoritative sources;
- accessibility, documentation, and onboarding improvements;
- small, backward-compatible CLI fixes;
- focused learning tracks that can be loaded conditionally.

Avoid adding large encyclopedic knowledge dumps, vendor marketing, obscure trivia, private interview banks, copyrighted course content, or instructions that require loading the entire Vault.

## Workflow

1. Open an Issue or Discussion for substantial changes.
2. Fork the repository and create a focused branch.
3. Make the smallest coherent change.
4. Run `python scripts/validate_repo.py`.
5. Update documentation and the Changelog when behavior changes.
6. Open a pull request using the provided checklist.

## Skill design rules

- Keep execution and judgment in Codex; Markdown is durable state.
- Begin concepts with one approachable broad probe; ask at most one learning question per turn. Teach missing foundations directly, and reserve hints for foundation-ready learners who are close to an answer.
- End tutorials with key takeaways, next learning, and a quiz overview; treat teaching and assisted answers as learning evidence, not verified mastery.
- Keep the scoped progress bar derived from the existing evidence matrix; do not add persisted numeric progress fields.
- Require new-scenario transfer after explanations.
- Preserve canonical Concept IDs and aliases.
- Prefer official documentation, standards, specifications, papers, and repository source.
- Keep source projects read-only unless the user explicitly authorizes changes.
- Enforce authorization and isolation for cybersecurity practice.

## Privacy

Use synthetic or public test data. Never submit personal Vault notes, resumes, private job descriptions, credentials, employer-confidential material, or proprietary source code.

By participating, you agree to follow the [Code of Conduct](CODE_OF_CONDUCT.md).
