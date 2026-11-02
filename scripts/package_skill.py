"""Zip one skill for upload to Claude.ai or Claude Desktop.

    python3 scripts/package_skill.py find-events

Writes dist/<skill>.zip with the skill's folder at the top of the zip, which is the layout
Claude.ai expects. The folder's README.md is for people browsing GitHub, so it is left out.
"""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LEFT_OUT = {"README.md", ".DS_Store"}


def package(name: str) -> Path:
    skill = ROOT / "skills" / name
    if not (skill / "SKILL.md").is_file():
        raise SystemExit(f"error: no skill at skills/{name}")
    out = ROOT / "dist" / f"{name}.zip"
    out.parent.mkdir(exist_ok=True)
    files = sorted(
        p
        for p in skill.rglob("*")
        if p.is_file() and p.name not in LEFT_OUT and "__pycache__" not in p.parts
    )
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in files:
            archive.write(path, Path(name) / path.relative_to(skill))
    return out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    out = package(argv[0])
    with zipfile.ZipFile(out) as archive:
        names = archive.namelist()
    print(f"{out.relative_to(ROOT)}: {len(names)} files")
    for entry in names:
        print(f"  {entry}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
