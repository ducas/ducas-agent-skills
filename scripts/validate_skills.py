#!/usr/bin/env python3
"""Validate all skill directories in the repo."""

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {"_template", "scripts", ".git"}
PLACEHOLDER = "<PLACEHOLDER>"


def parse_frontmatter(text):
    """Return (fields_dict, body) or raise ValueError."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("file must start with ---")
    try:
        close = next(i for i, l in enumerate(lines[1:], 1) if l.strip() == "---")
    except StopIteration:
        raise ValueError("frontmatter closing --- not found")
    fm_lines = lines[1:close]
    body = "\n".join(lines[close + 1 :])
    fields = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        m = re.match(r"^(\w+):\s*(>)?\s*(.*)$", line)
        if m:
            key, folded, rest = m.group(1), m.group(2), m.group(3)
            if folded:
                parts = []
                i += 1
                while i < len(fm_lines) and fm_lines[i].startswith("  "):
                    parts.append(fm_lines[i].strip())
                i -= 1
                fields[key] = " ".join(parts)
            else:
                fields[key] = rest.strip()
        i += 1
    return fields, body


def validate_skill(skill_dir):
    errors = []
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        return [f"missing SKILL.md"]
    text = skill_md.read_text()
    if PLACEHOLDER in text:
        errors.append(f"contains {PLACEHOLDER} markers")
    try:
        fields, body = parse_frontmatter(text)
    except ValueError as e:
        errors.append(f"frontmatter parse error: {e}")
        return errors
    name = fields.get("name", "").strip()
    if not name:
        errors.append("frontmatter missing 'name'")
    elif name != skill_dir.name:
        errors.append(f"'name' ({name!r}) does not match directory name ({skill_dir.name!r})")
    if not fields.get("description", "").strip():
        errors.append("frontmatter missing 'description'")
    if not any(line.startswith("## ") for line in body.splitlines()):
        errors.append("body has no ## sections")
    return errors


def main():
    skill_dirs = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")
    )
    total = len(skill_dirs)
    failed = 0
    for skill_dir in skill_dirs:
        errors = validate_skill(skill_dir)
        for err in errors:
            print(f"[FAIL] {skill_dir.name}: {err}")
            failed += 1
    if failed:
        print(f"\n{total} skill(s) checked, {failed} error(s) found.")
        sys.exit(1)
    else:
        print(f"All {total} skill(s) valid.")


if __name__ == "__main__":
    main()
