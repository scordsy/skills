"""Tests for the check set grader: it must fail a missed plant and an invented correction."""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("grader", ROOT / "tests" / "find-events" / "grade_check_set.py")
assert spec and spec.loader
grader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = grader
spec.loader.exec_module(grader)

KEY = {
    "records": {
        "1": {"name": "Clean", "planted": None, "verdicts": ["confirmed"]},
        "2": {"name": "Old date", "planted": "date-wrong", "verdicts": ["confirmed"]},
        "3": {"name": "Gone", "planted": "dead-not-caught", "verdicts": ["dead"]},
    }
}


def checked(*blocks: str) -> list:
    return grader.records.parse("\n\n".join(blocks))


CLEAN_OK = "## 1. Clean  [confirmed]  (lane: a)\n- Corrections: none"
DATE_OK = "## 2. Old date  [confirmed]  (lane: a)\n- Corrections: date-wrong, price-wrong"
DEAD_OK = "## 3. Gone  [dead]  (lane: a)\n- Corrections: dead-not-caught"


class GraderTest(unittest.TestCase):
    def test_all_caught_passes_and_reports_extras(self) -> None:
        passed, lines = grader.grade(KEY, checked(CLEAN_OK, DATE_OK, DEAD_OK))
        self.assertTrue(passed)
        self.assertIn("also flagged: price-wrong", lines[1])

    def test_a_missed_plant_fails(self) -> None:
        missed = "## 2. Old date  [confirmed]  (lane: a)\n- Corrections: none"
        passed, lines = grader.grade(KEY, checked(CLEAN_OK, missed, DEAD_OK))
        self.assertFalse(passed)
        self.assertIn("missed date-wrong", lines[1])

    def test_an_invented_correction_fails(self) -> None:
        invented = "## 1. Clean  [confirmed]  (lane: a)\n- Corrections: room-overstated"
        passed, lines = grader.grade(KEY, checked(invented, DATE_OK, DEAD_OK))
        self.assertFalse(passed)
        self.assertIn("invented room-overstated", lines[0])

    def test_a_wrong_verdict_or_missing_record_fails(self) -> None:
        alive = "## 3. Gone  [confirmed]  (lane: a)\n- Corrections: dead-not-caught"
        passed, lines = grader.grade(KEY, checked(CLEAN_OK, alive))
        self.assertFalse(passed)
        self.assertIn("missing", lines[1])
        self.assertIn("verdict confirmed, expected dead", lines[2])

    def test_the_saved_run_passes_against_the_current_key(self) -> None:
        key = grader.json.loads((ROOT / "tests" / "find-events" / "check-set" / "answer-key.json").read_text(encoding="utf-8"))
        run = ROOT / "tests" / "find-events" / "check-set" / "runs" / "2026-11-04-run-7-checked.md"
        passed, lines = grader.grade(key, grader.records.read(run))
        self.assertTrue(passed, "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
