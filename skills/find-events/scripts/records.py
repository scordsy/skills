"""Read, strip, merge, drop and tally find-events records.

Standard library only, so it runs wherever Python 3.10 or later does.

    python3 records.py strip <lane file> <out file>
    python3 records.py merge <out file> <check file> [<check file> ...]
    python3 records.py drop <records file> <number> [<number> ...]
    python3 records.py tally <records file>
"""

from __future__ import annotations

import re
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

VERDICTS = ("confirmed", "pattern-estimate", "dead", "unverifiable")
CORRECTIONS = (
    "date-wrong",
    "price-wrong",
    "dead-not-caught",
    "gate-missed",
    "room-overstated",
    "name-wrong",
    "detail-wrong",
)

HEADER = re.compile(r"^## (\d+)\. (.+?)\s+\[([^\]]+)\]\s+\(lane: ([^)]+)\)\s*$")
LOOKS_LIKE_HEADER = re.compile(r"^#{1,6}\s*\d+\.")
FIELD = re.compile(r"^- ([^:]+):\s*(.*)$")


class RecordError(ValueError):
    """A file that does not follow the record format."""


@dataclass
class Record:
    number: int
    name: str
    verdict: str
    lane: str
    lines: list[str] = field(default_factory=list)

    def get(self, key: str) -> str | None:
        for line in self.lines:
            match = FIELD.match(line)
            if match and match.group(1).strip().lower() == key.lower():
                return match.group(2).strip()
        return None

    @property
    def corrections(self) -> list[str] | None:
        """The correction types, an empty list for "none", or None if unchecked."""
        value = self.get("Corrections")
        if value is None:
            return None
        if value.strip().lower() in ("none", ""):
            return []
        return [part.strip().lower() for part in value.split(",") if part.strip()]

    def render(self, number: int | None = None) -> str:
        shown = self.number if number is None else number
        header = f"## {shown}. {self.name}  [{self.verdict}]  (lane: {self.lane})"
        body = "\n".join(self.lines).rstrip()
        return f"{header}\n{body}" if body else header


def parse(text: str, source: str = "<text>") -> list[Record]:
    """Every record in a file. Anything that is not a record is ignored."""
    records: list[Record] = []
    current: Record | None = None
    for raw in text.splitlines():
        line = raw.rstrip()
        match = HEADER.match(line)
        if not match and LOOKS_LIKE_HEADER.match(line):
            raise RecordError(
                f"{source}: this record header is not in the record format, so the record would be lost: {line!r}"
            )
        if match:
            verdict = match.group(3).strip().lower()
            if verdict not in VERDICTS:
                raise RecordError(
                    f"{source}: record {match.group(1)} has verdict [{verdict}], "
                    f"expected one of {', '.join(VERDICTS)}"
                )
            current = Record(int(match.group(1)), match.group(2).strip(), verdict, match.group(4).strip())
            records.append(current)
        elif line.startswith("#"):
            current = None
        elif current is not None:
            current.lines.append(line)
    for record in records:
        while record.lines and not record.lines[-1].strip():
            record.lines.pop()
    return records


def read(path: Path) -> list[Record]:
    try:
        text = path.read_text(encoding="utf-8-sig")
    except UnicodeDecodeError as error:
        raise RecordError(f"{path}: not a UTF-8 text file ({error.reason})") from error
    return parse(text, str(path))


def strip(source: Path, out: Path) -> int:
    """Copy only the records, leaving out lane notes and anything else."""
    records = read(source)
    if not records:
        raise RecordError(f"{source}: no records found")
    out.write_text("\n\n".join(r.render() for r in records) + "\n", encoding="utf-8")
    return len(records)


def _url_key(url: str | None) -> str | None:
    if not url or not url.strip().lower().startswith(("http://", "https://")):
        return None
    key = re.sub(r"^https?://(www\.)?", "", url.strip().lower())
    return key.rstrip("/") or None


def _name_key(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


def duplicates(records: list[Record]) -> list[tuple[int, int, str]]:
    """Pairs of positions (counted from 1) that look like the same event."""
    found: list[tuple[int, int, str]] = []
    seen_urls: dict[str, int] = {}
    seen_names: dict[str, int] = {}
    for position, record in enumerate(records, start=1):
        url = _url_key(record.get("URL"))
        name = _name_key(record.name)
        if url and url in seen_urls:
            found.append((seen_urls[url], position, "same URL"))
        elif name in seen_names:
            found.append((seen_names[name], position, "same name"))
        if url:
            seen_urls.setdefault(url, position)
        seen_names.setdefault(name, position)
    return found


def merge(out: Path, sources: list[Path]) -> tuple[list[tuple[Path, int]], list[tuple[int, int, str]]]:
    """Combine checked files into one, numbered from 1 in file order. Returns the count per file."""
    records: list[Record] = []
    counts: list[tuple[Path, int]] = []
    for source in sources:
        found = read(source)
        counts.append((source, len(found)))
        records.extend(found)
    if not records:
        raise RecordError("no records found in " + ", ".join(str(s) for s in sources))
    blocks = [r.render(number) for number, r in enumerate(records, start=1)]
    out.write_text("# Records\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")
    return counts, duplicates(records)


def drop(path: Path, numbers: set[int]) -> tuple[list[str], int]:
    """Remove records by number, such as the weaker copy of a duplicate, and renumber the rest."""
    records = read(path)
    known = {r.number for r in records}
    missing = sorted(numbers - known)
    if missing:
        raise RecordError(f"{path}: no record numbered {', '.join(str(n) for n in missing)}")
    dropped = [r.name for r in records if r.number in numbers]
    kept = [r for r in records if r.number not in numbers]
    blocks = [r.render(number) for number, r in enumerate(kept, start=1)]
    path.write_text("# Records\n\n" + "\n\n".join(blocks) + "\n", encoding="utf-8")
    return dropped, len(kept)


@dataclass
class Tally:
    total: int
    verdicts: Counter[str]
    corrections: Counter[str]
    corrected: int
    unchecked: list[int]
    unknown: list[tuple[int, str]]


def tally(records: list[Record]) -> Tally:
    verdicts: Counter[str] = Counter(r.verdict for r in records)
    corrections: Counter[str] = Counter()
    corrected = 0
    unchecked: list[int] = []
    unknown: list[tuple[int, str]] = []
    for record in records:
        types = record.corrections
        if types is None:
            unchecked.append(record.number)
            continue
        if types:
            corrected += 1
        for kind in types:
            if kind in CORRECTIONS:
                corrections[kind] += 1
            else:
                unknown.append((record.number, kind))
    return Tally(len(records), verdicts, corrections, corrected, unchecked, unknown)


def render_tally(result: Tally) -> str:
    lines = ["| Verdict | Count |", "|---|---|"]
    lines += [f"| {v} | {result.verdicts.get(v, 0)} |" for v in VERDICTS]
    lines += [
        "",
        f"{result.corrected} of {result.total} records needed at least one correction:",
        "",
        "| Correction | Count |",
        "|---|---|",
    ]
    lines += [f"| {c} | {result.corrections.get(c, 0)} |" for c in CORRECTIONS]
    if result.unchecked:
        numbers = ", ".join(str(n) for n in result.unchecked)
        lines += ["", f"Unchecked (no Corrections line): records {numbers}"]
    if result.unknown:
        listed = ", ".join(f"record {n}: {kind}" for n, kind in result.unknown)
        lines += ["", f"Unknown correction types, not counted: {listed}"]
    return "\n".join(lines)


def main(argv: list[str]) -> int:
    usage = __doc__.strip().splitlines()[-4:]
    if len(argv) < 2:
        print("\n".join(usage), file=sys.stderr)
        return 2
    command, raw = argv[0], argv[1:]
    args = [Path(a) for a in raw]
    try:
        if command == "strip" and len(args) == 2:
            count = strip(args[0], args[1])
            print(f"{count} records written to {args[1]}")
            return 0
        if command == "merge" and len(args) >= 2:
            counts, dupes = merge(args[0], args[1:])
            for source, count in counts:
                print(f"{count} records from {source.name}")
            print(f"{sum(c for _, c in counts)} records written to {args[0]}")
            for first, second, why in dupes:
                print(f"Possible duplicate: records {first} and {second} ({why})")
            return 0
        if command == "drop" and len(raw) >= 2 and all(a.isdigit() for a in raw[1:]):
            dropped, left = drop(args[0], {int(a) for a in raw[1:]})
            print(f"Dropped {', '.join(dropped)}. {left} records left, renumbered from 1")
            return 0
        if command == "tally" and len(args) == 1:
            found = read(args[0])
            if not found:
                raise RecordError(f"{args[0]}: no records found")
            print(render_tally(tally(found)))
            return 0
    except (RecordError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print("\n".join(usage), file=sys.stderr)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
