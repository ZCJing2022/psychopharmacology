#!/usr/bin/env python3
"""Apply authored Explanation panels without rewriting questions or answer keys.

Python 3.9+; standard library only. Default: apply. --check: validate without writing.
The workflow invokes this AFTER materialize_site.py and BEFORE committing/rendering.
"""
from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path
import re
import sys
import tempfile
import unicodedata

DATA_PATH = "assessment/detailed-explanations.json"
HEADING = re.compile(r"(?m)^### (?P<title>(?:Question|Short Essay)\s+\d+[^\n]*)\n")
CALLOUT = re.compile(r'(?m)^:::[ \t]+\{(?P<attrs>[^\n]*)\}\r?\n(?P<body>[\s\S]*?)^:::[ \t]*(?=\r?$)')


def signature(text: str) -> str:
    """Ignore rendering-only Markdown, whitespace, typography, and punctuation.

    Retain the ordered letters/numbers, including Greek letters. Quarto can insert
    nonbreaking spaces or change quotes/dashes without changing source meaning.
    """
    text = html.unescape(text)
    text = re.sub(r"<[^>]*>", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text)
    text = unicodedata.normalize("NFKC", text).casefold()
    return hashlib.sha256("".join(c for c in text if c.isalnum()).encode("utf-8")).hexdigest()


def sections(text: str):
    hits = list(HEADING.finditer(text))
    return [(m, text[m.end():hits[i+1].start() if i+1 < len(hits) else len(text)])
            for i, m in enumerate(hits)]


def transform(text: str, entries: list, narratives: dict, filename: str) -> tuple[str, int]:
    """Validate every question first; replace only the Explanation body bytes."""
    blocks = sections(text)
    if len(blocks) != len(entries):
        raise ValueError(f"{filename}: expected {len(entries)} questions, found {len(blocks)}")
    edits = []
    for (heading, block), expected in zip(blocks, entries):
        label = f"{filename} / {expected['id']}"
        title = re.sub(r"\s*\{#[^}]+\}\s*$", "", heading.group("title"))
        if signature(title) != expected["heading_signature"]:
            raise ValueError(f"{label}: heading changed; refusing to apply an explanation to a different item")
        anchor = re.search(r"\{#([^}]+)\}", heading.group("title"))
        if anchor and anchor.group(1) != expected["id"]:
            raise ValueError(f"{label}: question anchor changed")
        found = list(CALLOUT.finditer(block))
        answers = [m for m in found if re.search(r'title=[\"\']Answer[\"\']', m.group("attrs"))]
        explains = [m for m in found if '.question-explanation' in m.group("attrs")]
        if len(answers) != 1 or len(explains) != 1:
            raise ValueError(f"{label}: expected exactly one Answer and one Explanation callout")
        ans, exp = answers[0], explains[0]
        if ans.start() >= exp.start():
            raise ValueError(f"{label}: unexpected callout order")
        for panel in (ans, exp):
            if not re.search(r'collapse=[\"\']true[\"\']', panel.group("attrs")):
                raise ValueError(f"{label}: panel is not initially collapsed")
        if signature(block[:ans.start()]) != expected["question_signature"]:
            raise ValueError(f"{label}: question wording/options changed; review before updating")
        if signature(ans.group("body")) != expected["answer_signature"]:
            raise ValueError(f"{label}: answer key/model answer changed; review before updating")
        sid = expected['source_id']
        if sid not in narratives:
            raise ValueError(f"{label}: no authored explanation for {sid}")
        narrative = narratives[sid]['markdown'].rstrip() + '\n'
        if re.search(r'(?m)^:::', narrative):
            raise ValueError(f"{label}: nested callout delimiter in explanation data")
        old = exp.group('body')
        if old != narrative:
            edits.append((heading.end() + exp.start('body'), heading.end() + exp.end('body'), narrative))
    result = text
    for start, end, replacement in reversed(edits):
        result = result[:start] + replacement + result[end:]
    return result, len(edits)


def plan(repo: Path, data: dict) -> tuple[dict[Path, bytes], dict]:
    if data.get('schema_version') != 1:
        raise ValueError("Unsupported explanation data schema")
    paths = data['pages']
    if len(paths) != 25 or sum(len(v) for v in paths.values()) != 749:
        raise ValueError("Data must describe all 25 pages and 749 appearances")
    if len(data['narratives']) != 410:
        raise ValueError("Data must contain all 410 unique narratives")
    changes = {}
    checked = replaced = 0
    for relative, entries in paths.items():
        rel = Path(relative)
        if rel.is_absolute() or '..' in rel.parts or rel.suffix != '.qmd' or rel.parts[0] != 'practice':
            raise ValueError(f"Unsafe or unexpected page path: {relative}")
        path = (repo / rel).resolve()
        if not path.is_relative_to(repo.resolve()):
            raise ValueError(f"Page resolves outside repository: {relative}")
        if not path.is_file():
            raise ValueError(f"Missing {relative}; first materialize the original site or pull the current repository")
        raw = path.read_bytes()
        before = raw.decode('utf-8')
        after, count = transform(before, entries, data['narratives'], relative)
        checked += len(entries)
        replaced += count
        if after != before:
            changes[path] = after.encode('utf-8')
    return changes, {"pages_checked": len(paths), "questions_checked": checked,
                     "pages_changed": len(changes), "explanations_changed": replaced}


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent, prefix='.'+path.name+'.', delete=False) as fh:
            temp = Path(fh.name)
            fh.write(content)
        if path.exists():
            temp.chmod(path.stat().st_mode & 0o777)
        temp.replace(path)
    finally:
        if temp is not None and temp.exists():
            temp.unlink()


def apply_changes(changes: dict[Path, bytes]) -> None:
    """Write the prevalidated plan; restore previous bytes on a write failure."""
    originals = {p: p.read_bytes() if p.exists() else None for p in changes}
    written = []
    try:
        for path, content in changes.items():
            atomic_write(path, content)
            written.append(path)
    except Exception:
        for path in reversed(written):
            if originals[path] is None:
                path.unlink(missing_ok=True)
            else:
                atomic_write(path, originals[path])
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--data', type=Path)
    parser.add_argument('--check', action='store_true', help='validate all items without writing')
    args = parser.parse_args()
    repo = args.repo.expanduser().resolve()
    data_path = args.data or repo / DATA_PATH
    try:
        data = json.loads(data_path.read_text(encoding='utf-8'))
        changes, report = plan(repo, data)
        if not args.check:
            apply_changes(changes)
        print(json.dumps({"mode": "check" if args.check else "apply", **report}, indent=2))
        return 0
    except (ValueError, OSError, KeyError) as exc:
        print(f"ERROR: {exc}\nNo partially validated update has been applied.", file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
