# Source policy

Use sources to ground teaching while keeping retrieval proportional to the current branch.

## Priority

1. User-provided project or material as the object being explained.
2. Installed MCP tools or authorized connectors.
3. Official documentation, standards, specifications, original papers, and repository source.
4. High-quality secondary explanations when primary sources are insufficient.

Label source type, authority, retrieval date, version or commit, and uncertainty. For conflicts, state what the supplied material says, what the primary authority says, and the practical implication.

## GitHub

Store repository, tracking branch, resolved commit SHA, optional subpath, visibility, and last-checked date. Use commit permalinks for claims about specific code. A branch URL is for freshness checks, not reproducibility.

Do not copy a whole repository into the Vault. Use an authorized GitHub connector or API for orientation and targeted reads. Clone a fixed commit into a temporary cache only when execution or broader code navigation is necessary. Keep the source read-only unless modification is explicitly requested.

Do not store authentication tokens in the Vault. For private repositories, verify that the active GitHub connection has access.

## URLs and files

For a URL that may change or expire, store the URL, retrieval date, title, source type, and a concise claims summary. For local files or folders, store their resolved path and relevant version marker. Do not paste large copyrighted or source documents into notes.

## Citations

Keep chat citations light: cite version-sensitive, disputed, surprising, or foundational claims. At branch completion, give a compact source list. Persist the fuller claim-to-source relationship in Source and Topic notes.
