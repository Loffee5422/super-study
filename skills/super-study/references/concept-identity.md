# Concept identity and naming

Read this before creating, renaming, merging, or splitting Concept notes.

## Identity

Give every Concept a stable `concept-id`. Never change the ID during rename, move, or domain reassignment. Treat `canonical-name`, filename, aliases, domains, and path as mutable metadata.

Use the industry-standard English term for `canonical-name` and filename. Put Chinese translations, expansions, abbreviations, legacy names, and common variants in `aliases`. Write explanations in Chinese while preserving code, API, protocol, and interview terms in English.

Avoid prefixes such as `Concept -`, dates, and mastery states in filenames. Prefer singular terms unless the established term is plural. Add a parenthetical qualifier only to disambiguate a meaningful variant, such as `Event Loop (Browser)` and `Event Loop (Node.js)`.

## Resolution

Before creation, run `resolve-concept` against canonical names and aliases. Review only the top candidates. Compare scope and learning objective, not spelling alone.

Choose one action:

- reuse the existing Concept;
- add an alias to the existing Concept;
- create a narrower or platform-specific variant linked through `broader`;
- create a genuinely new Concept.

Do not merge related concepts merely because their names overlap. Do not duplicate a shared concept for each domain or job description; use the `domains` list and links from several Topic notes.

## Collisions

Treat duplicate IDs and duplicate normalized canonical names as validation errors. Treat alias collisions and strong fuzzy matches as warnings requiring review. Preserve redirects or aliases when a well-used Concept is renamed.
