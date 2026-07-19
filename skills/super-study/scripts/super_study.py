#!/usr/bin/env python3
"""Deterministic Vault operations for the super-study skill.

Uses only the Python standard library. Markdown notes remain authoritative;
JSONL files under .super-study are disposable indexes.
"""

from __future__ import annotations

import argparse
import datetime as dt
import difflib
import json
import os
import re
import sys
import tempfile
import unicodedata
import uuid
from pathlib import Path
from typing import Any, Iterable


SCHEMA_VERSION = 1
CONFIG_ENV = "SUPER_STUDY_CONFIG"
INDEX_DIR = ".super-study"
MARKER_START = "<!-- super-study:index:start -->"
MARKER_END = "<!-- super-study:index:end -->"

DOMAINS = {
    "frontend": "Frontend",
    "backend": "Backend",
    "data": "Data",
    "ai": "AI",
    "agents": "Agents",
    "security": "Security",
}

MANAGED_DIRS = [
    "00 Home",
    "10 Topics",
    "20 Concepts",
    "30 Sessions",
    "40 Sources",
    "50 Reviews",
    "60 Targets",
    "90 Templates",
    INDEX_DIR,
]

KIND_REQUIRED = {
    "concept": ("concept-id", "canonical-name"),
    "topic": ("topic-id", "canonical-name"),
    "session": ("session-id", "track", "topic"),
    "source": ("source-id", "source-type"),
    "target": ("target-id", "role"),
}


class SuperStudyError(RuntimeError):
    pass


def now_iso() -> str:
    return dt.datetime.now().astimezone().replace(microsecond=0).isoformat()


def today_iso() -> str:
    return dt.date.today().isoformat()


def default_config_path() -> Path:
    override = os.environ.get(CONFIG_ENV)
    if override:
        return Path(override).expanduser().resolve()
    return Path.home() / ".codex" / "super-study" / "config.json"


def atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=str(path.parent))
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(tmp_name, path)
    except Exception:
        try:
            os.unlink(tmp_name)
        except OSError:
            pass
        raise


def write_json(path: Path, value: Any) -> None:
    atomic_write_text(path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def emit(value: Any) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2))


def load_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def load_config(path: Path, required: bool = True) -> dict[str, Any]:
    data = load_json(path)
    if data is None:
        if required:
            raise SuperStudyError(
                f"No configuration at {path}. Run configure --vault PATH first."
            )
        return {}
    if not isinstance(data, dict):
        raise SuperStudyError(f"Configuration is not a JSON object: {path}")
    return data


def resolve_vault(args: argparse.Namespace, require_initialized: bool = False) -> Path:
    if getattr(args, "vault", None):
        vault = Path(args.vault).expanduser().resolve()
    else:
        config_path = Path(getattr(args, "config", None) or default_config_path())
        config = load_config(config_path)
        raw = config.get("vault")
        if not raw:
            raise SuperStudyError(f"Configuration has no vault path: {config_path}")
        vault = Path(raw).expanduser().resolve()
    if not vault.exists() or not vault.is_dir():
        raise SuperStudyError(f"Vault does not exist or is not a directory: {vault}")
    if require_initialized and not (vault / INDEX_DIR / "manifest.json").exists():
        raise SuperStudyError(f"Vault is not initialized for super-study: {vault}")
    return vault


def ensure_within(root: Path, path: Path) -> Path:
    resolved_root = root.resolve()
    resolved_path = path.resolve()
    try:
        resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise SuperStudyError(f"Path is outside the configured Vault: {path}") from exc
    return resolved_path


def normalize(value: str) -> str:
    text = unicodedata.normalize("NFKC", value).casefold()
    text = re.sub(r"[_\-–—/\\]+", " ", text)
    text = re.sub(r"[^\w\s]+", "", text, flags=re.UNICODE)
    return " ".join(text.split())


def slugify(value: str, fallback: str = "item") -> str:
    text = unicodedata.normalize("NFKD", value)
    text = text.encode("ascii", "ignore").decode("ascii").casefold()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text or fallback)[:48]


def safe_filename(value: str) -> str:
    name = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "-", value).strip(" .")
    name = re.sub(r"\s+", " ", name)
    if not name:
        raise SuperStudyError("A note filename cannot be empty")
    reserved = {"con", "prn", "aux", "nul"} | {
        f"com{i}" for i in range(1, 10)
    } | {f"lpt{i}" for i in range(1, 10)}
    if name.casefold() in reserved:
        name += " Note"
    return name[:120]


def scalar(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] and text[0] in {'"', "'"}:
        text = text[1:-1]
    if text in {"null", "~"}:
        return ""
    return text


def parse_inline_list(value: str) -> list[str] | None:
    stripped = value.strip()
    if not (stripped.startswith("[") and stripped.endswith("]")):
        return None
    if stripped == "[]":
        return []
    try:
        parsed = json.loads(stripped)
        if isinstance(parsed, list):
            return [str(item) for item in parsed]
    except json.JSONDecodeError:
        pass
    inner = stripped[1:-1]
    return [scalar(item) for item in inner.split(",") if scalar(item)]


def parse_frontmatter(text: str) -> dict[str, Any]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}
    end = None
    for index in range(1, len(lines)):
        if lines[index].strip() == "---":
            end = index
            break
    if end is None:
        return {}

    data: dict[str, Any] = {}
    current_list: str | None = None
    for raw in lines[1:end]:
        line = raw.rstrip()
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith("  - ") or line.startswith("- "):
            if current_list:
                data.setdefault(current_list, []).append(scalar(line.split("-", 1)[1]))
            continue
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", line)
        if not match:
            current_list = None
            continue
        key, raw_value = match.group(1), (match.group(2) or "")
        inline = parse_inline_list(raw_value)
        if inline is not None:
            data[key] = inline
            current_list = key
        elif raw_value.strip() == "":
            data[key] = []
            current_list = key
        else:
            value = scalar(raw_value)
            if value.casefold() == "true":
                data[key] = True
            elif value.casefold() == "false":
                data[key] = False
            elif re.fullmatch(r"-?\d+", value):
                data[key] = int(value)
            else:
                data[key] = value
            current_list = None
    return data


def yaml_quote(value: str) -> str:
    return json.dumps(value, ensure_ascii=False)


def yaml_list(key: str, values: Iterable[str]) -> str:
    items = [str(item) for item in values if str(item).strip()]
    if not items:
        return f"{key}: []"
    return "\n".join([f"{key}:"] + [f"  - {yaml_quote(item)}" for item in items])


def read_note(path: Path) -> tuple[dict[str, Any], str]:
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    return parse_frontmatter(text), text


def managed_markdown_files(vault: Path) -> Iterable[Path]:
    for path in vault.rglob("*.md"):
        rel_parts = path.relative_to(vault).parts
        if not rel_parts:
            continue
        if rel_parts[0] in {".obsidian", INDEX_DIR, "90 Templates"}:
            continue
        if any(part.startswith(".") for part in rel_parts):
            continue
        yield path


def as_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, list):
        return [str(item) for item in value if str(item).strip()]
    return [str(value)]


def record_for(path: Path, vault: Path, meta: dict[str, Any]) -> dict[str, Any]:
    kind = str(meta.get("kind", "")).strip()
    record: dict[str, Any] = {
        "kind": kind,
        "path": path.relative_to(vault).as_posix(),
        "modified": dt.datetime.fromtimestamp(path.stat().st_mtime).astimezone().replace(
            microsecond=0
        ).isoformat(),
    }
    if kind == "concept":
        record.update(
            {
                "id": str(meta.get("concept-id", "")),
                "name": str(meta.get("canonical-name", path.stem)),
                "aliases": as_list(meta.get("aliases")),
                "domains": as_list(meta.get("domains")),
                "status": str(meta.get("status", "")),
                "summary": str(meta.get("summary", "")),
                "broader": as_list(meta.get("broader")),
                "next_review": str(meta.get("next-review", "")),
            }
        )
    elif kind == "topic":
        record.update(
            {
                "id": str(meta.get("topic-id", "")),
                "name": str(meta.get("canonical-name", path.stem)),
                "aliases": as_list(meta.get("aliases")),
                "domains": as_list(meta.get("domains")),
                "status": str(meta.get("status", "")),
                "summary": str(meta.get("summary", "")),
                "next_review": str(meta.get("next-review", "")),
            }
        )
        for key, value in meta.items():
            if key.startswith("mastery-"):
                record[key.replace("-", "_")] = value
    elif kind == "source":
        record.update(
            {
                "id": str(meta.get("source-id", "")),
                "source_type": str(meta.get("source-type", "")),
                "title": str(meta.get("title", path.stem)),
                "url": str(meta.get("url", "")),
                "repository": str(meta.get("repository", "")),
                "resolved_commit": str(meta.get("resolved-commit", "")),
                "authority": str(meta.get("authority", "")),
            }
        )
    elif kind == "session":
        record.update(
            {
                "id": str(meta.get("session-id", "")),
                "track": str(meta.get("track", "")),
                "topic": str(meta.get("topic", "")),
                "target": str(meta.get("target", "")),
                "status": str(meta.get("status", "")),
                "created": str(meta.get("created", "")),
                "updated": str(meta.get("updated", "")),
            }
        )
    elif kind == "target":
        record.update(
            {
                "id": str(meta.get("target-id", "")),
                "company": str(meta.get("company", "")),
                "role": str(meta.get("role", path.stem)),
                "status": str(meta.get("status", "")),
                "source": str(meta.get("source", "")),
            }
        )
    return record


def write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> None:
    content = "".join(
        json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n"
        for record in records
    )
    atomic_write_text(path, content)


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8-sig") as handle:
        for number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise SuperStudyError(f"Invalid JSONL at {path}:{number}: {exc}") from exc
            if isinstance(value, dict):
                records.append(value)
    return records


def replace_marked(path: Path, generated: str, initial: str) -> None:
    if path.exists():
        text = path.read_text(encoding="utf-8-sig", errors="replace")
        pattern = re.compile(
            re.escape(MARKER_START) + r".*?" + re.escape(MARKER_END), re.DOTALL
        )
        block = f"{MARKER_START}\n{generated.rstrip()}\n{MARKER_END}"
        if pattern.search(text):
            new_text = pattern.sub(lambda _: block, text, count=1)
        else:
            new_text = text.rstrip() + "\n\n" + block + "\n"
    else:
        new_text = initial.rstrip() + "\n\n" + MARKER_START + "\n"
        new_text += generated.rstrip() + "\n" + MARKER_END + "\n"
    atomic_write_text(path, new_text)


def wiki(path: str, label: str | None = None) -> str:
    target = path[:-3] if path.casefold().endswith(".md") else path
    return f"[[{target}|{label}]]" if label else f"[[{target}]]"


def render_navigation(vault: Path, grouped: dict[str, list[dict[str, Any]]]) -> None:
    concepts = grouped.get("concept", [])
    topics = grouped.get("topic", [])
    sessions = grouped.get("session", [])
    sources = grouped.get("source", [])
    targets = grouped.get("target", [])

    counts = (
        f"- Topics: **{len(topics)}**\n"
        f"- Concepts: **{len(concepts)}**\n"
        f"- Sessions: **{len(sessions)}**\n"
        f"- Sources: **{len(sources)}**\n"
        f"- Job targets: **{len(targets)}**\n"
        f"- Index updated: `{now_iso()}`"
    )
    start_initial = """---
kind: dashboard
canonical-name: Start Here
---

# Start Here

Use this page as the human entry point. Generated sections are maintained by `super-study`; text outside the markers is yours.

## Guide

- [[00 Home/Super Study 使用说明|Super Study 使用说明]]

## Domains

- [[00 Home/Frontend MOC|Frontend]]
- [[00 Home/Backend MOC|Backend]]
- [[00 Home/Data MOC|Data]]
- [[00 Home/AI MOC|AI]]
- [[00 Home/Agents MOC|Agents]]
- [[00 Home/Security MOC|Security]]

## Queues

- [[00 Home/Current Learning]]
- [[00 Home/Review Queue]]

## Library status"""
    replace_marked(vault / "00 Home" / "Start Here.md", counts, start_initial)

    active = [
        item
        for item in topics
        if item.get("status") in {"learning", "needs-review", "planned"}
    ]
    active_lines = ["| Topic | Domain | Status | Next review |", "|---|---|---|---|"]
    for item in sorted(active, key=lambda x: (str(x.get("status")), str(x.get("name")))):
        active_lines.append(
            f"| {wiki(item['path'], str(item.get('name') or 'Untitled'))} | "
            f"{', '.join(item.get('domains') or [])} | {item.get('status', '')} | "
            f"{item.get('next_review', '')} |"
        )
    if len(active_lines) == 2:
        active_lines.append("| _No active Topics_ |  |  |  |")
    current_initial = """---
kind: dashboard
canonical-name: Current Learning
---

# Current Learning

Topics that are planned, active, or need review."""
    replace_marked(
        vault / "00 Home" / "Current Learning.md",
        "\n".join(active_lines),
        current_initial,
    )

    due: list[dict[str, Any]] = []
    today = today_iso()
    for item in topics + concepts:
        next_review = str(item.get("next_review") or "")
        if next_review and next_review <= today:
            due.append(item)
    due_lines = ["| Item | Kind | Due | Status |", "|---|---|---|---|"]
    for item in sorted(due, key=lambda x: (str(x.get("next_review")), str(x.get("name")))):
        due_lines.append(
            f"| {wiki(item['path'], str(item.get('name') or 'Untitled'))} | "
            f"{item.get('kind', '')} | {item.get('next_review', '')} | {item.get('status', '')} |"
        )
    if len(due_lines) == 2:
        due_lines.append("| _Nothing due_ |  |  |  |")
    review_initial = """---
kind: dashboard
canonical-name: Review Queue
---

# Review Queue

Due dates are evidence-driven. A review is complete only after a new level-0 test."""
    replace_marked(
        vault / "00 Home" / "Review Queue.md",
        "\n".join(due_lines),
        review_initial,
    )

    for domain, title in DOMAINS.items():
        domain_topics = [item for item in topics if domain in item.get("domains", [])]
        domain_concepts = [item for item in concepts if domain in item.get("domains", [])]
        lines = ["## Topics"]
        if domain_topics:
            lines.extend(
                f"- {wiki(item['path'], str(item.get('name') or 'Untitled'))} — {item.get('status', '')}"
                for item in sorted(domain_topics, key=lambda x: str(x.get("name")))
            )
        else:
            lines.append("- _None yet_")
        lines.extend(["", "## Concepts"])
        if domain_concepts:
            lines.extend(
                f"- {wiki(item['path'], str(item.get('name') or 'Untitled'))} — {item.get('status', '')}"
                for item in sorted(domain_concepts, key=lambda x: str(x.get("name")))
            )
        else:
            lines.append("- _None yet_")
        initial = f"""---
kind: domain-map
domain: {domain}
canonical-name: {title} MOC
---

# {title}

This map exposes only the current {title} Topics and Concepts. Cross-domain Concepts remain single global notes."""
        replace_marked(
            vault / "00 Home" / f"{title} MOC.md", "\n".join(lines), initial
        )


def build_indexes(vault: Path, render: bool = True) -> dict[str, list[dict[str, Any]]]:
    grouped: dict[str, list[dict[str, Any]]] = {
        "concept": [],
        "topic": [],
        "source": [],
        "session": [],
        "target": [],
    }
    scanned = 0
    for path in managed_markdown_files(vault):
        scanned += 1
        meta, _ = read_note(path)
        kind = str(meta.get("kind", ""))
        if kind in grouped:
            grouped[kind].append(record_for(path, vault, meta))

    index_root = vault / INDEX_DIR
    index_root.mkdir(parents=True, exist_ok=True)
    for kind, records in grouped.items():
        records.sort(key=lambda item: (normalize(str(item.get("name") or item.get("title") or item.get("topic") or "")), item["path"]))
        write_jsonl(index_root / f"{kind}s.jsonl", records)

    state = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": now_iso(),
        "markdown_files_scanned": scanned,
        "counts": {kind: len(records) for kind, records in grouped.items()},
    }
    write_json(index_root / "index-state.json", state)
    if render:
        render_navigation(vault, grouped)
    return grouped


def similarity(query: str, candidate: str) -> float:
    q = normalize(query)
    c = normalize(candidate)
    if not q or not c:
        return 0.0
    if q == c:
        return 1.0
    q_tokens, c_tokens = set(q.split()), set(c.split())
    union = q_tokens | c_tokens
    jaccard = len(q_tokens & c_tokens) / len(union) if union else 0.0
    sequence = difflib.SequenceMatcher(None, q, c).ratio()
    containment = 0.88 if min(len(q), len(c)) >= 4 and (q in c or c in q) else 0.0
    return max(sequence * 0.82, jaccard * 0.92, containment)


def concept_candidates(vault: Path, query: str, limit: int = 5) -> list[dict[str, Any]]:
    index = vault / INDEX_DIR / "concepts.jsonl"
    if not index.exists():
        build_indexes(vault)
    candidates: list[dict[str, Any]] = []
    for record in load_jsonl(index):
        fields = [(str(record.get("name", "")), "canonical-name")]
        fields.extend((str(alias), "alias") for alias in record.get("aliases", []))
        best_score, matched, match_type = 0.0, "", ""
        for value, field_type in fields:
            score = similarity(query, value)
            if score > best_score:
                best_score, matched, match_type = score, value, field_type
        if best_score > 0.20:
            candidates.append(
                {
                    "score": round(best_score, 4),
                    "matched": matched,
                    "match_type": match_type,
                    **record,
                }
            )
    candidates.sort(key=lambda item: (-float(item["score"]), str(item.get("name"))))
    return candidates[: max(1, limit)]


def asset_root() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "vault-templates"


def copy_if_missing(source: Path, target: Path) -> bool:
    if target.exists():
        return False
    target.parent.mkdir(parents=True, exist_ok=True)
    atomic_write_text(target, source.read_text(encoding="utf-8-sig"))
    return True


def manifest(vault: Path) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "vault_id": "software-engineering-learning",
        "canonical_terms": "en",
        "teaching_language": "zh-CN",
        "notes_are_source_of_truth": True,
        "paths": {
            "home": "00 Home",
            "topics": "10 Topics",
            "concepts": "20 Concepts",
            "sessions": "30 Sessions",
            "sources": "40 Sources",
            "reviews": "50 Reviews",
            "targets": "60 Targets",
            "templates": "90 Templates",
        },
        "indexes": {
            "concepts": ".super-study/concepts.jsonl",
            "topics": ".super-study/topics.jsonl",
            "sources": ".super-study/sources.jsonl",
            "sessions": ".super-study/sessions.jsonl",
            "targets": ".super-study/targets.jsonl",
        },
        "domains": list(DOMAINS),
        "updated_at": now_iso(),
    }


def command_configure(args: argparse.Namespace) -> int:
    vault = Path(args.vault).expanduser().resolve()
    if args.create:
        vault.mkdir(parents=True, exist_ok=True)
    if not vault.exists() or not vault.is_dir():
        raise SuperStudyError(f"Vault does not exist or is not a directory: {vault}")
    config_path = Path(args.config or default_config_path()).expanduser().resolve()
    config = {
        "schema_version": SCHEMA_VERSION,
        "vault": str(vault),
        "write_consent": bool(args.consent),
        "updated_at": now_iso(),
    }
    write_json(config_path, config)
    emit({"status": "configured", "config": str(config_path), **config})
    return 0


def command_init(args: argparse.Namespace) -> int:
    vault = resolve_vault(args)
    created: list[str] = []
    for rel in MANAGED_DIRS:
        path = vault / rel
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path.relative_to(vault).as_posix() + "/")
    for domain in DOMAINS:
        for root in ("10 Topics", "20 Concepts"):
            path = vault / root / domain
            if not path.exists():
                path.mkdir(parents=True, exist_ok=True)
                created.append(path.relative_to(vault).as_posix() + "/")
    shared = vault / "20 Concepts" / "shared"
    if not shared.exists():
        shared.mkdir(parents=True, exist_ok=True)
        created.append(shared.relative_to(vault).as_posix() + "/")

    assets = asset_root()
    if not assets.exists():
        raise SuperStudyError(f"Bundled Vault templates are missing: {assets}")
    if copy_if_missing(assets / "AGENTS.md", vault / "AGENTS.md"):
        created.append("AGENTS.md")
    usage_target = vault / "00 Home" / "Super Study 使用说明.md"
    if copy_if_missing(assets / "Usage Guide.md", usage_target):
        created.append(usage_target.relative_to(vault).as_posix())
    for template in assets.glob("*.template.md"):
        target_name = template.name.replace(".template", "")
        target = vault / "90 Templates" / target_name
        if copy_if_missing(template, target):
            created.append(target.relative_to(vault).as_posix())

    write_json(vault / INDEX_DIR / "manifest.json", manifest(vault))
    grouped = build_indexes(vault)
    emit(
        {
            "status": "initialized",
            "vault": str(vault),
            "created": created,
            "preserved_existing_files": True,
            "counts": {kind: len(records) for kind, records in grouped.items()},
        }
    )
    return 0


def command_reindex(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    grouped = build_indexes(vault)
    emit(
        {
            "status": "indexed",
            "vault": str(vault),
            "counts": {kind: len(records) for kind, records in grouped.items()},
        }
    )
    return 0


def command_status(args: argparse.Namespace) -> int:
    config_path = Path(args.config or default_config_path()).expanduser().resolve()
    config = load_config(config_path, required=not bool(args.vault))
    vault = resolve_vault(args)
    state = load_json(vault / INDEX_DIR / "index-state.json", {})
    sessions = load_jsonl(vault / INDEX_DIR / "sessions.jsonl")
    sessions.sort(key=lambda item: str(item.get("updated") or item.get("created") or ""), reverse=True)
    emit(
        {
            "status": "ready" if (vault / INDEX_DIR / "manifest.json").exists() else "not-initialized",
            "vault": str(vault),
            "write_consent": bool(config.get("write_consent", False)) if config else None,
            "index": state,
            "latest_sessions": sessions[:3],
        }
    )
    return 0


def command_resolve_concept(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    candidates = concept_candidates(vault, args.query, args.limit)
    emit({"query": args.query, "count": len(candidates), "candidates": candidates})
    return 0


def concept_note(
    concept_id: str,
    name: str,
    aliases: list[str],
    domains: list[str],
    summary: str,
    broader: list[str],
) -> str:
    properties = [
        "---",
        "kind: concept",
        f"concept-id: {yaml_quote(concept_id)}",
        f"canonical-name: {yaml_quote(name)}",
        yaml_list("aliases", aliases),
        yaml_list("domains", domains),
        "status: learning",
        f"summary: {yaml_quote(summary)}",
        yaml_list("broader", broader),
        f"created: {today_iso()}",
        f"last-reviewed: {today_iso()}",
        "next-review: null",
        "mastery-recall: unassessed",
        "mastery-mechanism: unassessed",
        "mastery-implementation: unassessed",
        "mastery-debugging: unassessed",
        "mastery-tradeoffs: unassessed",
        "mastery-security: unassessed",
        "mastery-communication: unassessed",
        "mastery-transfer: unassessed",
        "---",
        "",
        f"# {name}",
        "",
        "## Working definition",
        "",
        summary,
        "",
        "## Mental model and mechanism",
        "",
        "## Boundaries and comparisons",
        "",
        "## Implementation and examples",
        "",
        "## Failure modes and misconceptions",
        "",
        "## Tradeoffs and security",
        "",
        "## Mastery evidence",
        "",
        "## Sources",
        "",
    ]
    return "\n".join(properties)


def command_create_concept(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    domains = [domain.casefold() for domain in args.domain]
    invalid = [domain for domain in domains if domain not in set(DOMAINS) | {"shared"}]
    if invalid:
        raise SuperStudyError(f"Unknown domain(s): {', '.join(invalid)}")
    candidates = concept_candidates(vault, args.name, 5)
    if candidates and float(candidates[0]["score"]) >= args.duplicate_threshold:
        emit(
            {
                "status": "possible-duplicate",
                "message": "Review candidates before creating a Concept.",
                "candidates": candidates,
            }
        )
        return 2

    folder = "shared" if "shared" in domains or len(domains) > 1 else domains[0]
    filename = safe_filename(args.name) + ".md"
    path = vault / "20 Concepts" / folder / filename
    if path.exists():
        raise SuperStudyError(f"Concept file already exists: {path}")
    concept_id = f"c-{slugify(args.name, 'concept')}-{uuid.uuid4().hex[:6]}"
    content = concept_note(
        concept_id,
        args.name,
        args.alias or [],
        [domain for domain in domains if domain != "shared"],
        args.summary,
        args.broader or [],
    )
    atomic_write_text(path, content)
    build_indexes(vault)
    emit(
        {
            "status": "created",
            "concept_id": concept_id,
            "path": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def topic_note(
    topic_id: str,
    name: str,
    aliases: list[str],
    domains: list[str],
    summary: str,
    targets: list[str],
    sources: list[str],
    prerequisites: list[str],
) -> str:
    properties = [
        "---",
        "kind: topic",
        f"topic-id: {yaml_quote(topic_id)}",
        f"canonical-name: {yaml_quote(name)}",
        yaml_list("aliases", aliases),
        yaml_list("domains", domains),
        "status: learning",
        f"summary: {yaml_quote(summary)}",
        yaml_list("targets", targets),
        yaml_list("sources", sources),
        yaml_list("prerequisites", prerequisites),
        f"created: {today_iso()}",
        f"last-reviewed: {today_iso()}",
        "next-review: null",
        "mastery-recall: unassessed",
        "mastery-mechanism: unassessed",
        "mastery-implementation: unassessed",
        "mastery-debugging: unassessed",
        "mastery-tradeoffs: unassessed",
        "mastery-security: unassessed",
        "mastery-communication: unassessed",
        "mastery-transfer: unassessed",
        "---",
        "",
        f"# {name}",
        "",
        "## Learning contract",
        "",
        "### Required",
        "",
        "### Supporting",
        "",
        "### Extensions",
        "",
        "## Knowledge map",
        "",
        "## Common project difficulties",
        "",
        "## Gap ledger",
        "",
        "## Mastery evidence",
        "",
        "## Sources",
        "",
    ]
    return "\n".join(properties)


def command_create_topic(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    domains = [domain.casefold() for domain in args.domain]
    invalid = [domain for domain in domains if domain not in DOMAINS]
    if invalid:
        raise SuperStudyError(f"Unknown domain(s): {', '.join(invalid)}")
    grouped = build_indexes(vault)
    candidates = search_records(grouped["topic"], args.name, 5)
    if candidates and float(candidates[0]["score"]) >= args.duplicate_threshold:
        emit(
            {
                "status": "possible-duplicate",
                "message": "Review candidates before creating a Topic.",
                "candidates": candidates,
            }
        )
        return 2
    path = vault / "10 Topics" / domains[0] / (safe_filename(args.name) + ".md")
    if path.exists():
        raise SuperStudyError(f"Topic file already exists: {path}")
    topic_id = f"t-{slugify(args.name, 'topic')}-{uuid.uuid4().hex[:6]}"
    content = topic_note(
        topic_id,
        args.name,
        args.alias or [],
        domains,
        args.summary,
        args.target or [],
        args.source or [],
        args.prerequisite or [],
    )
    atomic_write_text(path, content)
    build_indexes(vault)
    emit(
        {
            "status": "created",
            "topic_id": topic_id,
            "path": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def source_note(args: argparse.Namespace, source_id: str) -> str:
    fields = [
        "---",
        "kind: source",
        f"source-id: {yaml_quote(source_id)}",
        f"source-type: {yaml_quote(args.source_type)}",
        f"title: {yaml_quote(args.title)}",
        f"url: {yaml_quote(args.url or '')}",
        f"repository: {yaml_quote(args.repository or '')}",
        f"tracking-ref: {yaml_quote(args.tracking_ref or '')}",
        f"resolved-commit: {yaml_quote(args.resolved_commit or '')}",
        f"subpath: {yaml_quote(args.subpath or '')}",
        f"visibility: {yaml_quote(args.visibility)}",
        f"authority: {yaml_quote(args.authority)}",
        f"retrieved: {today_iso()}",
        "---",
        "",
        f"# {args.title}",
        "",
        "## Supported claims",
        "",
    ]
    if args.claim:
        fields.extend(f"- {claim}" for claim in args.claim)
    fields.extend(
        [
            "",
            "## Version and scope",
            "",
            "## Conflicts or uncertainty",
            "",
            "## Related Topics and Concepts",
            "",
        ]
    )
    return "\n".join(fields)


def command_create_source(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    grouped = build_indexes(vault)
    for item in grouped["source"]:
        same_url = args.url and str(item.get("url", "")) == args.url
        same_repo = (
            args.repository
            and str(item.get("repository", "")) == args.repository
            and str(item.get("resolved_commit", "")) == (args.resolved_commit or "")
        )
        if same_url or same_repo:
            emit(
                {
                    "status": "possible-duplicate",
                    "message": "An equivalent Source already exists.",
                    "candidate": item,
                }
            )
            return 2
    path = vault / "40 Sources" / (safe_filename(args.title) + ".md")
    if path.exists():
        raise SuperStudyError(f"Source file already exists: {path}")
    source_id = f"src-{slugify(args.title, 'source')}-{uuid.uuid4().hex[:6]}"
    atomic_write_text(path, source_note(args, source_id))
    build_indexes(vault)
    emit(
        {
            "status": "created",
            "source_id": source_id,
            "path": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def target_note(args: argparse.Namespace, target_id: str) -> str:
    title = " — ".join(value for value in (args.company, args.role) if value)
    lines = [
        "---",
        "kind: target",
        f"target-id: {yaml_quote(target_id)}",
        f"company: {yaml_quote(args.company or '')}",
        f"role: {yaml_quote(args.role)}",
        f"source: {yaml_quote(args.source or '')}",
        f"captured: {today_iso()}",
        f"status: {yaml_quote(args.status)}",
        "---",
        "",
        f"# {title}",
        "",
        "## Explicit requirements",
        "",
    ]
    lines.extend(f"- {item}" for item in (args.requirement or []))
    lines.extend(
        [
            "",
            "## Implied capabilities and seniority signals",
            "",
            "## Competency mapping",
            "",
            "## Shared requirements with other Targets",
            "",
            "## Current gaps and priority",
            "",
            "## Evidence",
            "",
        ]
    )
    return "\n".join(lines)


def command_create_target(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    grouped = build_indexes(vault)
    key = normalize(f"{args.company or ''} {args.role}")
    for item in grouped["target"]:
        existing = normalize(f"{item.get('company', '')} {item.get('role', '')}")
        if key and key == existing:
            emit(
                {
                    "status": "possible-duplicate",
                    "message": "A Target for this company and role already exists.",
                    "candidate": item,
                }
            )
            return 2
    title = " — ".join(value for value in (args.company, args.role) if value)
    path = vault / "60 Targets" / (safe_filename(title) + ".md")
    if path.exists():
        raise SuperStudyError(f"Target file already exists: {path}")
    target_id = f"target-{slugify(title, 'role')}-{uuid.uuid4().hex[:6]}"
    atomic_write_text(path, target_note(args, target_id))
    build_indexes(vault)
    emit(
        {
            "status": "created",
            "target_id": target_id,
            "path": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def command_set_mastery(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    raw_path = Path(args.note)
    path = raw_path if raw_path.is_absolute() else vault / raw_path
    path = ensure_within(vault, path)
    if not path.exists():
        raise SuperStudyError(f"Managed note does not exist: {path}")
    meta, text = read_note(path)
    if meta.get("kind") not in {"topic", "concept"}:
        raise SuperStudyError("Mastery can be set only on Topic or Concept notes")
    updates = {
        f"mastery-{args.dimension}": args.state,
        "last-reviewed": today_iso(),
    }
    if args.status:
        updates["status"] = args.status
    if args.next_review is not None:
        updates["next-review"] = args.next_review or "null"
    text = update_frontmatter(text, updates)
    atomic_write_text(path, text)
    build_indexes(vault)
    emit(
        {
            "status": "updated",
            "note": path.relative_to(vault).as_posix(),
            "dimension": args.dimension,
            "state": args.state,
        }
    )
    return 0


def command_start_session(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    now = dt.datetime.now().astimezone()
    short = uuid.uuid4().hex[:6]
    session_id = f"s-{now.strftime('%Y%m%d')}-{short}"
    folder = vault / "30 Sessions" / now.strftime("%Y") / now.strftime("%m")
    path = folder / f"{now.strftime('%Y-%m-%d')} - {safe_filename(args.topic)} - {short}.md"
    target_value = args.target or ""
    content = f"""---
kind: session
session-id: {yaml_quote(session_id)}
track: {yaml_quote(args.track)}
topic: {yaml_quote(args.topic)}
target: {yaml_quote(target_value)}
status: active
created: {now_iso()}
updated: {now_iso()}
---

# {args.topic} — Learning Session

## Learning contract

{args.contract or '_To be established by Codex with the learner._'}

## Checkpoints

### Session start — {now_iso()}

- Track: `{args.track}`
- Target: {target_value or '_none_'}
- Initial state: {args.initial_state or '_not yet diagnosed_'}

## Session outcome

_Active._
"""
    atomic_write_text(path, content)
    build_indexes(vault)
    emit(
        {
            "status": "started",
            "session_id": session_id,
            "path": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def update_frontmatter(text: str, updates: dict[str, str]) -> str:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise SuperStudyError("Session note has no YAML frontmatter")
    end = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end is None:
        raise SuperStudyError("Session note has unterminated YAML frontmatter")
    for key, value in updates.items():
        pattern = re.compile(rf"^{re.escape(key)}:")
        replacement = f"{key}: {value}"
        for i in range(1, end):
            if pattern.match(lines[i]):
                lines[i] = replacement
                break
        else:
            lines.insert(end, replacement)
            end += 1
    return "\n".join(lines) + ("\n" if text.endswith("\n") else "")


def bullet(label: str, values: list[str] | None) -> list[str]:
    if not values:
        return []
    if len(values) == 1:
        return [f"- {label}: {values[0]}"]
    return [f"- {label}:"] + [f"  - {value}" for value in values]


def command_checkpoint(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    raw_path = Path(args.session)
    path = raw_path if raw_path.is_absolute() else vault / raw_path
    path = ensure_within(vault, path)
    if not path.exists():
        raise SuperStudyError(f"Session note does not exist: {path}")
    text = path.read_text(encoding="utf-8-sig", errors="replace")
    status = {"pause": "paused", "complete": "complete"}.get(args.phase, "active")
    text = update_frontmatter(
        text,
        {"updated": now_iso(), "status": status},
    )
    lines = ["", f"### {args.phase.title()} — {now_iso()}", "", f"- Summary: {args.summary}"]
    lines.extend(bullet("Question", args.question))
    lines.extend(bullet("Misconception", args.misconception))
    lines.extend(bullet("Evidence", args.evidence))
    if args.hint_level is not None:
        lines.append(f"- Highest hint level: `{args.hint_level}`")
    lines.extend(bullet("Unresolved branch", args.unresolved))
    lines.extend(bullet("Next test", args.next_test))
    atomic_write_text(path, text.rstrip() + "\n" + "\n".join(lines) + "\n")
    build_indexes(vault)
    emit(
        {
            "status": "checkpointed",
            "phase": args.phase,
            "session": path.relative_to(vault).as_posix(),
        }
    )
    return 0


def search_records(records: list[dict[str, Any]], query: str, limit: int) -> list[dict[str, Any]]:
    ranked: list[dict[str, Any]] = []
    for record in records:
        fields = [
            str(record.get("name") or record.get("topic") or record.get("role") or ""),
            *[str(value) for value in record.get("aliases", [])],
        ]
        score = max((similarity(query, field) for field in fields), default=0.0)
        if score > 0.2:
            ranked.append({"score": round(score, 4), **record})
    ranked.sort(key=lambda item: (-float(item["score"]), item["path"]))
    return ranked[:limit]


def command_context(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    grouped = build_indexes(vault)
    sessions = grouped["session"]
    sessions.sort(key=lambda item: str(item.get("updated") or item.get("created") or ""), reverse=True)
    result: dict[str, Any] = {
        "vault": str(vault),
        "manifest": ".super-study/manifest.json",
        "latest_sessions": sessions[: args.limit],
    }
    if args.topic:
        result["topics"] = search_records(grouped["topic"], args.topic, args.limit)
        result["concept_candidates"] = concept_candidates(vault, args.topic, args.limit)
        result["related_sessions"] = [
            item
            for item in sessions
            if normalize(args.topic) in normalize(str(item.get("topic", "")))
            or normalize(str(item.get("topic", ""))) in normalize(args.topic)
        ][: args.limit]
    emit(result)
    return 0


def link_targets(vault: Path) -> set[str]:
    targets: set[str] = set()
    for path in vault.rglob("*.md"):
        rel_parts = path.relative_to(vault).parts
        if rel_parts and rel_parts[0] in {".obsidian", INDEX_DIR}:
            continue
        rel = path.relative_to(vault).as_posix()
        no_ext = rel[:-3] if rel.casefold().endswith(".md") else rel
        targets.add(normalize(no_ext))
        targets.add(normalize(path.stem))
    return targets


def managed_links(text: str) -> list[str]:
    links = []
    for raw in re.findall(r"\[\[([^\]]+)\]\]", text):
        target = raw.split("|", 1)[0].split("#", 1)[0].strip()
        if target:
            links.append(target)
    return links


def validate_vault(vault: Path) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    records_by_kind: dict[str, list[tuple[Path, dict[str, Any], str]]] = {}

    for path in managed_markdown_files(vault):
        meta, text = read_note(path)
        kind = str(meta.get("kind", ""))
        if not kind:
            continue
        records_by_kind.setdefault(kind, []).append((path, meta, text))
        for field in KIND_REQUIRED.get(kind, ()):
            if not meta.get(field):
                errors.append(f"{path.relative_to(vault).as_posix()}: missing {field}")

    concepts = records_by_kind.get("concept", [])
    ids: dict[str, Path] = {}
    names: dict[str, Path] = {}
    aliases: dict[str, list[Path]] = {}
    for path, meta, _ in concepts:
        concept_id = normalize(str(meta.get("concept-id", "")))
        name = normalize(str(meta.get("canonical-name", "")))
        if concept_id:
            if concept_id in ids:
                errors.append(
                    f"duplicate concept-id in {ids[concept_id].relative_to(vault).as_posix()} and {path.relative_to(vault).as_posix()}"
                )
            ids[concept_id] = path
        if name:
            if name in names:
                errors.append(
                    f"duplicate canonical-name in {names[name].relative_to(vault).as_posix()} and {path.relative_to(vault).as_posix()}"
                )
            names[name] = path
        for alias in as_list(meta.get("aliases")):
            aliases.setdefault(normalize(alias), []).append(path)

    for alias, paths in aliases.items():
        unique = {str(path) for path in paths}
        if alias and len(unique) > 1:
            warnings.append(
                f"alias collision '{alias}' in "
                + ", ".join(sorted(path.relative_to(vault).as_posix() for path in paths))
            )
        if alias in names and all(path != names[alias] for path in paths):
            warnings.append(
                f"alias '{alias}' collides with canonical-name in {names[alias].relative_to(vault).as_posix()}"
            )

    targets = link_targets(vault)
    for kind, items in records_by_kind.items():
        for path, _, text in items:
            for target in managed_links(text):
                if normalize(target) not in targets:
                    warnings.append(
                        f"{path.relative_to(vault).as_posix()}: unresolved link [[{target}]]"
                    )

    required_files = [
        "AGENTS.md",
        "00 Home/Start Here.md",
        ".super-study/manifest.json",
        ".super-study/concepts.jsonl",
    ]
    for rel in required_files:
        if not (vault / rel).exists():
            errors.append(f"missing managed file: {rel}")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "managed_notes": sum(len(items) for items in records_by_kind.values()),
        "concepts": len(concepts),
    }


def command_validate(args: argparse.Namespace) -> int:
    vault = resolve_vault(args, require_initialized=True)
    build_indexes(vault)
    result = validate_vault(vault)
    emit(result)
    return 0 if result["valid"] else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Deterministic Vault operations for the super-study Codex skill."
    )
    parser.add_argument("--vault", help="Override the configured Vault path")
    parser.add_argument("--config", help="Override the user config path")
    sub = parser.add_subparsers(dest="command", required=True)

    configure = sub.add_parser("configure", help="Store the default Vault path")
    configure.add_argument("--vault", required=True, help="Obsidian Vault path")
    configure.add_argument(
        "--config",
        help="Override the user config path",
        default=argparse.SUPPRESS,
    )
    configure.add_argument("--consent", action="store_true", help="Record Vault write consent")
    configure.add_argument("--create", action="store_true", help="Create the Vault directory")
    configure.set_defaults(func=command_configure)

    init = sub.add_parser("init", help="Initialize a Vault without overwriting existing files")
    init.set_defaults(func=command_init)

    reindex = sub.add_parser("reindex", help="Rebuild machine indexes and human navigation")
    reindex.set_defaults(func=command_reindex)

    status = sub.add_parser("status", help="Return compact configuration and index status")
    status.set_defaults(func=command_status)

    resolve = sub.add_parser("resolve-concept", help="Find possible existing Concepts")
    resolve.add_argument("query")
    resolve.add_argument("--limit", type=int, default=5)
    resolve.set_defaults(func=command_resolve_concept)

    create = sub.add_parser("create-concept", help="Create a Concept after duplicate checks")
    create.add_argument("--name", required=True)
    create.add_argument("--domain", action="append", required=True)
    create.add_argument("--alias", action="append")
    create.add_argument("--summary", required=True)
    create.add_argument("--broader", action="append")
    create.add_argument("--duplicate-threshold", type=float, default=0.84)
    create.set_defaults(func=command_create_concept)

    topic = sub.add_parser("create-topic", help="Create a Topic after duplicate checks")
    topic.add_argument("--name", required=True)
    topic.add_argument("--domain", action="append", required=True)
    topic.add_argument("--alias", action="append")
    topic.add_argument("--summary", required=True)
    topic.add_argument("--target", action="append")
    topic.add_argument("--source", action="append")
    topic.add_argument("--prerequisite", action="append")
    topic.add_argument("--duplicate-threshold", type=float, default=0.84)
    topic.set_defaults(func=command_create_topic)

    source = sub.add_parser("create-source", help="Create a versioned Source note")
    source.add_argument("--title", required=True)
    source.add_argument("--source-type", required=True)
    source.add_argument("--url")
    source.add_argument("--repository")
    source.add_argument("--tracking-ref")
    source.add_argument("--resolved-commit")
    source.add_argument("--subpath")
    source.add_argument("--visibility", default="public")
    source.add_argument("--authority", default="primary")
    source.add_argument("--claim", action="append")
    source.set_defaults(func=command_create_source)

    target = sub.add_parser("create-target", help="Create a job-description Target note")
    target.add_argument("--company")
    target.add_argument("--role", required=True)
    target.add_argument("--source")
    target.add_argument("--status", default="active")
    target.add_argument("--requirement", action="append")
    target.set_defaults(func=command_create_target)

    mastery = sub.add_parser("set-mastery", help="Update one mastery dimension")
    mastery.add_argument("--note", required=True)
    mastery.add_argument(
        "--dimension",
        choices=(
            "recall",
            "mechanism",
            "implementation",
            "debugging",
            "tradeoffs",
            "security",
            "communication",
            "transfer",
        ),
        required=True,
    )
    mastery.add_argument(
        "--state",
        choices=("unassessed", "learning", "verified", "needs-review"),
        required=True,
    )
    mastery.add_argument(
        "--status", choices=("planned", "learning", "mastered", "needs-review")
    )
    mastery.add_argument("--next-review")
    mastery.set_defaults(func=command_set_mastery)

    session = sub.add_parser("start-session", help="Create an append-only Session note")
    session.add_argument(
        "--track",
        choices=(
            "technical-interview",
            "resume-project-deep-dive",
            "behavioral-interview",
        ),
        default="technical-interview",
    )
    session.add_argument("--topic", required=True)
    session.add_argument("--target")
    session.add_argument("--contract")
    session.add_argument("--initial-state")
    session.set_defaults(func=command_start_session)

    checkpoint = sub.add_parser("checkpoint", help="Append a structured Session checkpoint")
    checkpoint.add_argument("--session", required=True, help="Vault-relative or absolute Session path")
    checkpoint.add_argument("--phase", choices=("branch", "pause", "complete"), required=True)
    checkpoint.add_argument("--summary", required=True)
    checkpoint.add_argument("--question", action="append")
    checkpoint.add_argument("--misconception", action="append")
    checkpoint.add_argument("--evidence", action="append")
    checkpoint.add_argument("--hint-level", type=int, choices=range(0, 5))
    checkpoint.add_argument("--unresolved", action="append")
    checkpoint.add_argument("--next-test", action="append")
    checkpoint.set_defaults(func=command_checkpoint)

    context = sub.add_parser("context", help="Return compact paths for a resumed learning context")
    context.add_argument("--topic")
    context.add_argument("--limit", type=int, default=5)
    context.set_defaults(func=command_context)

    validate = sub.add_parser("validate", help="Validate managed notes, identities, and links")
    validate.set_defaults(func=command_validate)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args))
    except SuperStudyError as exc:
        emit({"status": "error", "error": str(exc)})
        return 1
    except KeyboardInterrupt:
        emit({"status": "error", "error": "Interrupted"})
        return 130


if __name__ == "__main__":
    sys.exit(main())
