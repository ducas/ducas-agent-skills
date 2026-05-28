#!/usr/bin/env python3
"""Build .skill ZIP archives for all valid skill directories."""

import sys
import zipfile
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
SKIP_DIRS = {"_template", "scripts", ".git", "dist"}
DIST_DIR = REPO_ROOT / "dist"


def build_skill(skill_dir: Path, dist_dir: Path) -> list[str]:
    errors = []
    out_path = dist_dir / f"{skill_dir.name}.skill"
    try:
        with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
            for file_path in sorted(skill_dir.rglob("*")):
                if file_path.is_file():
                    zf.write(file_path, arcname=file_path.relative_to(skill_dir))
    except Exception as e:
        errors.append(f"failed to build archive: {e}")
        if out_path.exists():
            out_path.unlink()
    return errors


def main():
    DIST_DIR.mkdir(exist_ok=True)
    skill_dirs = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and d.name not in SKIP_DIRS and not d.name.startswith(".")
    )
    total = len(skill_dirs)
    failed = 0
    for skill_dir in skill_dirs:
        errors = build_skill(skill_dir, DIST_DIR)
        if errors:
            for err in errors:
                print(f"[FAIL] {skill_dir.name}: {err}")
            failed += 1
        else:
            print(f"[OK]   {skill_dir.name} -> dist/{skill_dir.name}.skill")
    if failed:
        print(f"\n{total} skill(s) processed, {failed} failed.")
        sys.exit(1)
    else:
        print(f"\nBuilt {total} skill(s) into dist/.")


if __name__ == "__main__":
    main()
