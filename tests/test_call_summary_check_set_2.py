"""Checks check-call-summary's second check set against its saved run, as far as the saved files allow.

The 19 November 2026 run on Claude.ai saved only its report (check.md) and corrected draft, not its key
facts or per-summary check files, so the full grader cannot run on it. The report still holds every
claim with its quotes and verdict, and the key facts table, so this test re-verifies every claim quote
against the call and reads each rule in the hand-written answer key off the report. It cannot check
the key facts' own quotes, which the report does not carry.
"""

from __future__ import annotations

import importlib.util
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "check-call-summary" / "scripts" / "transcript.py"
spec = importlib.util.spec_from_file_location("transcript_set_2", SCRIPT)
assert spec and spec.loader
transcript = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = transcript
spec.loader.exec_module(transcript)

SET = ROOT / "tests" / "check-call-summary" / "check-set-2"
RUN = SET / "runs" / "2026-11-19-claude-ai"


def claims_by_summary(report: str) -> dict[str, list]:
    """The report's claims, per summary. Its claim headings are one level deeper than a check file's."""
    parts = re.split(r"^## Summary: (.+)$", report, flags=re.M)
    out = {}
    for i in range(1, len(parts), 2):
        body = parts[i + 1].split("\n## Key facts")[0].replace("\n### C", "\n## C")
        out[parts[i].strip()] = [b for b in transcript.parse_blocks(body, parts[i].strip()) if b.kind == "C"]
    return out


def from_line(claims: list, line: str) -> list:
    target = transcript.plain(line)
    return [c for c in claims if any(target == transcript.plain(transcript.unquote(v)) for v in c.get("From"))]


class CheckSetTwoTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.lines = {line.number: line for line in transcript.number((SET / "halvercombe-follow-up.txt").read_text(encoding="utf-8"))}
        cls.report = (RUN / "check.md").read_text(encoding="utf-8")
        cls.claims = claims_by_summary(cls.report)
        cls.key = json.loads((SET / "answer-key.json").read_text(encoding="utf-8"))

    def test_the_call_numbers_as_the_key_expects(self) -> None:
        self.assertEqual(len(self.lines), 48)
        self.assertEqual(self.lines[7].speaker, "Dana Whitlock")
        self.assertIn("Halvercombe Homes", self.lines[7].text)

    def test_every_claim_quote_is_on_its_line(self) -> None:
        quotes = [(name, c.ident, q) for name, cs in self.claims.items() for c in cs for q in c.quotes]
        self.assertEqual(len(quotes), 54)
        for name, ident, quote in quotes:
            with self.subTest(f"{name} {ident} {quote.cite()}"):
                self.assertIsNone(transcript.check_quote(quote, self.lines))

    def test_every_line_of_each_summary_was_checked(self) -> None:
        for name, file in (("notetaker-2", "notetaker-2.md"), ("rep-note", "rep-note.md")):
            fragments = [transcript.unquote(v) for c in self.claims[name] for v in c.get("From")]
            text = (SET / file).read_text(encoding="utf-8")
            with self.subTest(name):
                self.assertEqual([l for l in transcript.summary_lines(text) if transcript.covered(l, fragments) < 1], [])

    def test_every_planted_failure_is_caught_with_the_right_type(self) -> None:
        for planted in self.key["summaries"]["notetaker-2"]["planted"]:
            with self.subTest(planted["failure"]):
                found = from_line(self.claims["notetaker-2"], planted["line"])
                self.assertTrue(found)
                self.assertIn(planted["failure"], {f for c in found for f in transcript.failures_of(c)})

    def test_no_clean_line_and_no_line_of_the_accurate_note_gets_a_failure(self) -> None:
        for line in self.key["summaries"]["notetaker-2"]["clean"]:
            with self.subTest(line):
                found = from_line(self.claims["notetaker-2"], line)
                self.assertTrue(found)
                self.assertEqual([c.ident for c in found if transcript.failures_of(c) or c.tag not in ("said", "inferred")], [])
        self.assertEqual([c.ident for c in self.claims["rep-note"] if transcript.failures_of(c) or c.tag not in ("said", "inferred")], [])

    def test_the_audit_committee_rule_is_missing_or_carried_wrongly(self) -> None:
        table = self.report.split("## Key facts", 1)[1].splitlines()
        header = [cell.strip() for cell in next(l for l in table if l.startswith("|")).split("|")]
        rows = [[cell.strip() for cell in l.split("|")] for l in table if l.startswith("| K") and "audit committee" in l]
        self.assertEqual(len(rows), 1)
        kind, notetaker = rows[0][header.index("Kind")], rows[0][header.index("notetaker-2")]
        self.assertEqual(kind, "who-decides")
        self.assertTrue(notetaker == "missing" or notetaker.startswith("carried wrongly"), notetaker)

    def test_no_line_is_flagged_as_a_doubtful_label(self) -> None:
        self.assertEqual(self.key["doubtful_labels"], {})
        section = self.report.split("## Doubtful labels", 1)[1].split("\n## ", 1)[0]
        self.assertEqual(section.strip(), "None found.")


if __name__ == "__main__":
    unittest.main()
