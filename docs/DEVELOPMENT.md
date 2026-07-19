# Development

Super Study is intentionally lightweight. Its deterministic Vault CLI uses the Python standard library and supports Python 3.10 or newer.

## Local validation

From the repository root:

```bash
python scripts/validate_repo.py
```

The validator checks repository structure, Skill frontmatter, interface metadata, accidental personal paths, Python syntax, CLI startup, isolated Vault initialization, and Vault validation.

## Test the CLI manually

Use an isolated temporary directory and a separate config file. Never point development commands at a personal Vault unless that is the intended test target.

```bash
python skills/super-study/scripts/super_study.py \
  --config /tmp/super-study-config.json \
  configure --vault /tmp/super-study-vault --consent --create
python skills/super-study/scripts/super_study.py \
  --config /tmp/super-study-config.json init
python skills/super-study/scripts/super_study.py \
  --config /tmp/super-study-config.json validate
```

PowerShell equivalent:

```powershell
$configPath = Join-Path $env:TEMP "super-study-config.json"
$vaultPath = Join-Path $env:TEMP "super-study-vault"
python .\skills\super-study\scripts\super_study.py --config $configPath `
  configure --vault $vaultPath --consent --create
python .\skills\super-study\scripts\super_study.py --config $configPath init
python .\skills\super-study\scripts\super_study.py --config $configPath validate
```

## Change guidelines

- Keep `SKILL.md` focused on routing and behavior shared by most sessions.
- Put specialized workflows in `references/` and load them conditionally.
- Preserve backward-compatible Concept IDs and aliases.
- Treat Markdown as the durable source of truth and indexes as disposable.
- Do not add personal Vault data, machine paths, credentials, or proprietary learning material.
- Add a Changelog entry for user-visible changes.
- Update both English and Chinese user-facing documentation when behavior changes.

## Release checklist

1. Run `python scripts/validate_repo.py`.
2. Confirm GitHub Actions succeeds on the release commit.
3. Review the diff for local paths, credentials, Vault data, and private sources.
4. Update `CHANGELOG.md` and `CITATION.cff`.
5. Create a signed or annotated semantic-version tag.
6. Publish release notes that explain migration or compatibility changes.
