"""Tests for find-events' records.py: the strip, merge and tally the skill relies on."""

from __future__ import annotations

import contextlib
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "find-events" / "scripts" / "records.py"
spec = importlib.util.spec_from_file_location("records", SCRIPT)
assert spec and spec.loader
records = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = records
spec.loader.exec_module(records)

LANE_FILE = """\
## 1. Northern Ops Meetup  [confirmed]  (lane: uk-meetups)
- Where: Leeds, UK
- When: 4 Mar 2027
- URL: https://northernops.example/events/march

## 2. Big Expo  [pattern-estimate]  (lane: uk-meetups)
- Where: London, UK
- When: 2026 edition ran 9 May, no 2027 date published
- URL: https://bigexpo.example

## Belongs to another lane
- Some Paris thing

## Lane notes
- Searched user groups first
"""

CHECKED_A = """\
## 1. Northern Ops Meetup  [confirmed]  (lane: uk-meetups)
- URL: https://northernops.example/events/march
- Check notes: Dates match the organiser's page.
- Corrections: none

## 2. Big Expo  [dead]  (lane: uk-meetups)
- URL: https://bigexpo.example
- Check notes: Organiser announced the last edition was 2025.
- Corrections: dead-not-caught, date-wrong
"""

CHECKED_B = """\
## 1. Big Expo  [dead]  (lane: flagships)
- URL: http://www.bigexpo.example/
- Corrections: dead-not-caught

## 2. Unknown Summit  [unverifiable]  (lane: flagships)
- URL: https://unknown.example
- Corrections: price-wrong, room-overstated
"""


class RecordsTest(unittest.TestCase):
    def setUp(self) -> None:
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)

    def write(self, name: str, text: str) -> Path:
        path = self.dir / name
        path.write_text(text, encoding="utf-8")
        return path

    def test_strip_keeps_records_and_drops_lane_notes(self) -> None:
        out = self.dir / "to-check.md"
        count = records.strip(self.write("lane.md", LANE_FILE), out)
        text = out.read_text()
        self.assertEqual(count, 2)
        self.assertIn("## 2. Big Expo  [pattern-estimate]  (lane: uk-meetups)", text)
        self.assertNotIn("Lane notes", text)
        self.assertNotIn("Searched user groups", text)
        self.assertNotIn("Paris", text)

    def test_merge_renumbers_in_file_order_and_flags_duplicates(self) -> None:
        out = self.dir / "records.md"
        counts, dupes = records.merge(out, [self.write("a.md", CHECKED_A), self.write("b.md", CHECKED_B)])
        merged = records.read(out)
        self.assertEqual([c for _, c in counts], [2, 2])
        self.assertEqual([r.number for r in merged], [1, 2, 3, 4])
        self.assertEqual(merged[2].lane, "flagships")
        self.assertEqual(dupes, [(2, 3, "same URL")])

    def test_drop_removes_a_record_and_renumbers(self) -> None:
        out = self.dir / "records.md"
        records.merge(out, [self.write("a.md", CHECKED_A), self.write("b.md", CHECKED_B)])
        dropped, left = records.drop(out, {3})
        kept = records.read(out)
        self.assertEqual(dropped, ["Big Expo"])
        self.assertEqual(left, 3)
        self.assertEqual([(r.number, r.name) for r in kept], [(1, "Northern Ops Meetup"), (2, "Big Expo"), (3, "Unknown Summit")])
        self.assertEqual(kept[1].lane, "uk-meetups")
        with self.assertRaises(records.RecordError):
            records.drop(out, {9})

    def test_tally_counts_verdicts_and_corrections(self) -> None:
        result = records.tally(records.parse(CHECKED_A + "\n" + CHECKED_B))
        self.assertEqual(result.total, 4)
        self.assertEqual(result.verdicts["dead"], 2)
        self.assertEqual(result.verdicts["confirmed"], 1)
        self.assertEqual(result.corrections["dead-not-caught"], 2)
        self.assertEqual(result.corrections["price-wrong"], 1)
        self.assertEqual(result.corrected, 3)
        self.assertEqual(result.unchecked, [])

    def test_tally_reports_unchecked_records_and_unknown_types(self) -> None:
        result = records.tally(records.parse(LANE_FILE + "\n" + "## 3. X  [dead]  (lane: a)\n- Corrections: typo\n"))
        self.assertEqual(result.unchecked, [1, 2])
        self.assertEqual(result.unknown, [(3, "typo")])
        rendered = records.render_tally(result)
        self.assertIn("Unchecked (no Corrections line): records 1, 2", rendered)
        self.assertIn("| dead | 1 |", rendered)

    def test_an_unknown_verdict_is_an_error(self) -> None:
        with self.assertRaises(records.RecordError):
            records.parse("## 1. X  [maybe]  (lane: a)\n")

    def test_a_malformed_header_is_an_error_not_a_lost_record(self) -> None:
        with self.assertRaises(records.RecordError):
            records.parse("## 1. X  [confirmed]\n- URL: https://x.example\n")

    def test_a_byte_order_mark_does_not_lose_the_first_record(self) -> None:
        path = self.dir / "bom.md"
        path.write_bytes(CHECKED_A.encode("utf-8-sig"))
        self.assertEqual([r.number for r in records.read(path)], [1, 2])

    def test_a_header_at_the_wrong_level_is_an_error(self) -> None:
        with self.assertRaises(records.RecordError):
            records.parse("### 1. X  [confirmed]  (lane: a)\n")

    def test_a_file_that_is_not_utf8_is_a_plain_error(self) -> None:
        path = self.dir / "latin.md"
        path.write_bytes("## 1. Caf\xe9  [confirmed]  (lane: a)\n".encode("latin-1"))
        with self.assertRaises(records.RecordError):
            records.read(path)

    def test_records_without_a_web_address_are_not_duplicates(self) -> None:
        text = "## 1. A  [dead]  (lane: a)\n- URL: none\n\n## 2. B  [dead]  (lane: a)\n- URL: none\n"
        self.assertEqual(records.duplicates(records.parse(text)), [])

    def test_the_same_name_is_flagged_as_a_duplicate(self) -> None:
        text = "## 1. Big Expo 2027  [confirmed]  (lane: a)\n\n## 2. Big Expo, 2027  [confirmed]  (lane: b)\n"
        self.assertEqual(records.duplicates(records.parse(text)), [(1, 2, "same name")])

    def test_windows_line_endings_parse(self) -> None:
        parsed = records.parse(CHECKED_A.replace("\n", "\r\n"))
        self.assertEqual([r.verdict for r in parsed], ["confirmed", "dead"])
        self.assertEqual(parsed[1].corrections, ["dead-not-caught", "date-wrong"])

    def test_command_line(self) -> None:
        checked = self.write("checked.md", CHECKED_A)
        with contextlib.redirect_stdout(io.StringIO()) as out, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(records.main(["tally", str(checked)]), 0)
            self.assertEqual(records.main(["tally"]), 2)
            self.assertEqual(records.main(["strip", str(self.dir / "missing.md"), str(self.dir / "o.md")]), 1)
        self.assertIn("| confirmed | 1 |", out.getvalue())

    def test_merge_and_drop_from_the_command_line(self) -> None:
        a, b, out = self.write("a.md", CHECKED_A), self.write("b.md", CHECKED_B), self.dir / "records.md"
        empty = self.write("empty.md", "## Lane notes\n- nothing found\n")
        with contextlib.redirect_stdout(io.StringIO()) as said, contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(records.main(["merge", str(out), str(a), str(b)]), 0)
            self.assertEqual(records.main(["drop", str(out), "3"]), 0)
            self.assertEqual(records.main(["drop", str(out), "x"]), 2)
            self.assertEqual(records.main(["tally", str(empty)]), 1)
        self.assertIn("2 records from a.md", said.getvalue())
        self.assertIn("Possible duplicate: records 2 and 3 (same URL)", said.getvalue())
        self.assertEqual(len(records.read(out)), 3)


if __name__ == "__main__":
    unittest.main()
