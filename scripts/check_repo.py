"""Structure and house-style checks for this repo. Run before every commit; CI runs it too.

    python3 scripts/check_repo.py

Exits 1 and lists every problem found, or prints "ok".
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# CLAUDE.md keeps frontmatter to these three. Claude.ai rejects most other keys on upload.
ALLOWED_KEYS = {"name", "description", "license"}
NAME = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
# The Agent Skills spec allows 1,024 characters. Claude.ai's upload has been reported to cap
# descriptions at 200, so stay under that until an upload proves otherwise.
DESCRIPTION_MAX = 200
SKILL_LINES_MAX = 500

# Built from code points so this file never contains the characters it bans.
BANNED_CHARACTERS = {
    chr(0x2014): "em dash",
    chr(0x2013): "en dash",
    chr(0x2018): "curly quote",
    chr(0x2019): "curly quote",
    chr(0x201C): "curly quote",
    chr(0x201D): "curly quote",
    chr(0x00A0): "non-breaking space",
    chr(0xFEFF): "byte-order mark",
    chr(0x200B): "zero-width space",
    chr(0x200C): "zero-width character",
    chr(0x200D): "zero-width character",
}
EMAIL = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}")
HEDGED_NUMBER = re.compile(r"\b(about|around)\s+[0-9]", re.IGNORECASE)
REFERENCED_FILE = re.compile(r"\b((?:references|scripts)/[A-Za-z0-9_./-]+\.(?:md|py))\b")
BARE_MD = re.compile(r"`([a-z0-9-]+\.md)`")
# Files a run writes, named in each skill's instructions but never part of the skill itself.
RUN_FILES = {
    "find-events": {"brief.md", "records.md", "shortlist.md"},
    "check-call-summary": {"transcript-lines.md", "key-facts.md", "check.md", "corrected.md"},
    "check-account-list": {"companies.md", "web.md", "checks.md"},
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".yml", ".yaml", ".txt", ""}


def tracked_files() -> list[Path]:
    """Every file git would publish: tracked plus untracked, minus ignored."""
    try:
        out = subprocess.run(
            ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            cwd=ROOT,
            capture_output=True,
            check=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return [p for p in ROOT.rglob("*") if p.is_file() and ".git" not in p.parts]
    return [ROOT / name for name in out.decode().split("\0") if name and (ROOT / name).is_file()]


def frontmatter(text: str) -> dict[str, str] | None:
    if not text.startswith("---\n"):
        return None
    end = text.find("\n---\n", 4)
    if end == -1:
        return None
    fields: dict[str, str] = {}
    for line in text[4:end].splitlines():
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def check_manifests(problems: list[str]) -> None:
    try:
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        market = json.loads((ROOT / ".claude-plugin/marketplace.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        problems.append(f"manifest: {error}")
        return
    for key in ("name", "version", "description", "author"):
        if not plugin.get(key):
            problems.append(f"plugin.json: missing {key}")
    if not re.fullmatch(r"\d+\.\d+\.\d+", str(plugin.get("version", ""))):
        problems.append("plugin.json: version must look like 1.2.3")
    entries = market.get("plugins") or []
    if [e.get("name") for e in entries] != [plugin.get("name")]:
        problems.append("marketplace.json: must list exactly the one plugin, named as in plugin.json")
    if any(e.get("source") != "./" for e in entries):
        problems.append('marketplace.json: the plugin source must be "./"')


def check_skill(skill: Path, readme: str, problems: list[str]) -> None:
    where = f"skills/{skill.name}"
    path = skill / "SKILL.md"
    if not path.is_file():
        problems.append(f"{where}: no SKILL.md")
        return
    text = path.read_text(encoding="utf-8")
    fields = frontmatter(text)
    if fields is None:
        problems.append(f"{where}/SKILL.md: no frontmatter")
        return
    for key in sorted(set(fields) - ALLOWED_KEYS):
        problems.append(f"{where}/SKILL.md: frontmatter key '{key}' breaks Claude.ai uploads")
    name = fields.get("name", "")
    if name != skill.name:
        problems.append(f"{where}/SKILL.md: name '{name}' must equal the folder name")
    if not NAME.match(name) or len(name) > 64:
        problems.append(f"{where}/SKILL.md: name must be lower case words joined by single hyphens")
    description = fields.get("description", "")
    if not 1 <= len(description) <= DESCRIPTION_MAX:
        problems.append(f"{where}/SKILL.md: description is {len(description)} characters, max {DESCRIPTION_MAX}")
    if len(text.splitlines()) > SKILL_LINES_MAX:
        problems.append(f"{where}/SKILL.md: over {SKILL_LINES_MAX} lines")
    for source in [path, *sorted((skill / "references").glob("*.md"))]:
        for ref in sorted(set(REFERENCED_FILE.findall(source.read_text(encoding="utf-8")))):
            if not (skill / ref).is_file():
                problems.append(f"{source.relative_to(ROOT)}: points to {ref}, which does not exist")
        for name in sorted(set(BARE_MD.findall(source.read_text(encoding="utf-8"))) - RUN_FILES.get(skill.name, set())):
            if not (skill / "references" / name).is_file() and not (skill / name).is_file():
                problems.append(f"{source.relative_to(ROOT)}: names {name}, which is not in the skill")
    if f"skills/{skill.name}/" not in readme:
        problems.append(f"README.md: no link to {where}/")


QUOTED = re.compile(r'"[^"]*"')

# Test inputs and evidence kept exactly as they are, so the house style cannot apply to them. Only
# the email check runs on these. Each entry says why it is exempt.
KEPT_VERBATIM = {
    "tests/check-call-summary/check-set-2/notetaker-2.md": (
        "a planted summary: its 'Around 25 users' line is the made-up detail the check set tests"
    ),
    "tests/check-call-summary/check-set-2/runs/2026-11-19-claude-ai/corrected.md": (
        "the skill's own output from a Claude.ai run, kept exactly as downloaded"
    ),
}


def saved_output(rel: Path) -> bool:
    """A real run kept as evidence: a check set's runs and a skill's example. Their quotes are copied
    exactly from web pages, as the skills require, so the house style applies outside the quotes only."""
    parts = rel.parts
    in_runs = len(parts) > 3 and parts[0] == "tests" and parts[2].startswith("check-set") and parts[3] == "runs"
    in_example = len(parts) > 2 and parts[:2] == ("docs", "examples") and rel.name != "README.md"
    return in_runs or in_example


def check_text(problems: list[str]) -> None:
    for name in sorted(KEPT_VERBATIM):
        if not (ROOT / name).is_file():
            problems.append(f"check_repo.py: KEPT_VERBATIM names {name}, which does not exist")
    for path in tracked_files():
        if path.suffix not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        rel = path.relative_to(ROOT)
        quoted_ok = saved_output(rel)
        for number, line in enumerate(text.splitlines(), start=1):
            if EMAIL.search(line):
                problems.append(f"{rel}:{number}: email address")
            if rel.as_posix() in KEPT_VERBATIM:
                continue
            if quoted_ok:
                line = QUOTED.sub('""', line)
            for char, label in BANNED_CHARACTERS.items():
                if char in line:
                    problems.append(f"{rel}:{number}: {label}")
            # Saved check-set runs are a checker's own words, kept verbatim as evidence.
            if path.suffix == ".md" and "runs" not in rel.parts and HEDGED_NUMBER.search(line):
                problems.append(f"{rel}:{number}: 'about' or 'around' before a number")


def main() -> int:
    problems: list[str] = []
    check_manifests(problems)
    readme_path = ROOT / "README.md"
    readme = readme_path.read_text(encoding="utf-8") if readme_path.is_file() else ""
    if not readme:
        problems.append("README.md: missing")
    skills = sorted(p for p in (ROOT / "skills").iterdir() if p.is_dir())
    if not skills:
        problems.append("skills/: no skills")
    for skill in skills:
        check_skill(skill, readme, problems)
    check_text(problems)
    if problems:
        print("\n".join(problems))
        return 1
    print("ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
