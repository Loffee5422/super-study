#!/usr/bin/env python3
"""Validate the public Super Study repository without external dependencies."""

from __future__ import annotations

import py_compile
import re
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "super-study"
CLI = SKILL / "scripts" / "super_study.py"

REQUIRED_FILES = (
    ROOT / "README.md",
    ROOT / "LICENSE",
    SKILL / "SKILL.md",
    SKILL / "agents" / "openai.yaml",
    SKILL / "references" / "mastery-protocol.md",
    SKILL / "references" / "concept-identity.md",
    SKILL / "references" / "source-policy.md",
    SKILL / "references" / "vault-contract.md",
    SKILL / "assets" / "vault-templates" / "Usage Guide.md",
    CLI,
)

TEXT_SUFFIXES = {".md", ".py", ".yml", ".yaml", ".json", ".toml", ".txt", ".svg"}
FORBIDDEN_PATTERNS = (
    re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+", re.IGNORECASE),
    re.compile(r"github_pat_[A-Za-z0-9_]+"),
    re.compile(r"gh[pousr]_[A-Za-z0-9]+"),
    re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----"),
)


def run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )


def validate_structure() -> None:
    missing = [str(path.relative_to(ROOT)) for path in REQUIRED_FILES if not path.is_file()]
    if missing:
        raise ValueError(f"Missing required files: {', '.join(missing)}")


def validate_skill_metadata() -> None:
    text = (SKILL / "SKILL.md").read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        raise ValueError("SKILL.md must start with YAML frontmatter")

    frontmatter = match.group(1)
    if not re.search(r"^name:\s*super-study\s*$", frontmatter, re.MULTILINE):
        raise ValueError("SKILL.md name must be super-study")
    description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
    if not description or len(description.group(1).strip()) < 80:
        raise ValueError("SKILL.md needs a specific trigger-oriented description")

    agent = (SKILL / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for required in ('display_name: "Super Study"', "$super-study"):
        if required not in agent:
            raise ValueError(f"agents/openai.yaml is missing {required!r}")


def validate_public_content() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".git" in path.parts or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(text):
                findings.append(f"{path.relative_to(ROOT)} matches {pattern.pattern!r}")
    if findings:
        raise ValueError("Potential private data found:\n" + "\n".join(findings))


def validate_cli() -> None:
    py_compile.compile(str(CLI), doraise=True)
    run(sys.executable, str(CLI), "--help")

    with tempfile.TemporaryDirectory(prefix="super-study-validation-") as temp:
        temp_root = Path(temp)
        config = temp_root / "config.json"
        vault = temp_root / "vault"
        common = (sys.executable, str(CLI), "--config", str(config))
        run(*common, "configure", "--vault", str(vault), "--consent", "--create")
        run(*common, "init")
        result = run(*common, "validate")
        if '"errors": []' not in result.stdout:
            raise ValueError(f"Generated Vault did not validate cleanly:\n{result.stdout}")


def main() -> int:
    checks = (
        ("repository structure", validate_structure),
        ("Skill metadata", validate_skill_metadata),
        ("public-content safety", validate_public_content),
        ("Python CLI and isolated Vault", validate_cli),
    )
    for label, check in checks:
        check()
        print(f"OK: {label}")
    print("Super Study repository validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
