"""Tests for check-call-summary's check set grader: the saved run passes, and a missed or invented failure fails."""

from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "tests" / "check-call-summary"
spec = importlib.util.spec_from_file_location("call_summary_grader", HERE / "grade_check_set.py")
assert spec and spec.loader
grader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = grader
spec.loader.exec_module(grader)
transcript = grader.transcript

RUN = HERE / "check-set" / "runs" / "2026-11-04-run-1"


class CallSummaryGraderTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        folder = Path(self.tmp.name)
        self.lines_path = folder / "transcript-lines.md"
        rendered = transcript.number((HERE / "check-set" / "call.vtt").read_text(encoding="utf-8"))
        self.lines_path.write_text("\n".join(line.render() for line in rendered) + "\n", encoding="utf-8")
        self.key = json.loads((HERE / "check-set" / "answer-key.json").read_text(encoding="utf-8"))
        self.summary = (HERE / "check-set" / "summary.md").read_text(encoding="utf-8")
        self.check_text = (RUN / "check-1-notetaker.md").read_text(encoding="utf-8")

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def grade(self, check_text: str, run: Path = RUN) -> tuple[bool, list[str]]:
        path = Path(self.tmp.name) / "check.md"
        path.write_text(check_text, encoding="utf-8")
        facts, doubts = transcript.read_facts(run / "key-facts.md")
        lines = transcript.read_lines(self.lines_path)
        return grader.grade(lines, facts, doubts, self.summary, transcript.read_check(path), self.key)

    def test_the_saved_runs_pass_against_the_current_key(self) -> None:
        for run in sorted((HERE / "check-set" / "runs").iterdir()):
            with self.subTest(run.name):
                passed, lines = self.grade((run / "check-1-notetaker.md").read_text(encoding="utf-8"), run)
                self.assertTrue(passed, "\n".join(lines))

    def test_a_missed_plant_fails(self) -> None:
        passed, lines = self.grade(self.check_text.replace("- Failures: wrong-speaker", "- Failures: none", 1))
        self.assertFalse(passed)
        self.assertTrue(any(l.startswith("FAIL wrong-speaker") for l in lines))

    def test_an_invented_failure_on_a_clean_line_fails(self) -> None:
        clean = "## C2. Ostlund runs 140 vehicles  [said]"
        start = self.check_text.index(clean)
        end = self.check_text.index("- Failures: none", start)
        broken = self.check_text[:end] + "- Failures: made-up-detail" + self.check_text[end + len("- Failures: none") :]
        passed, lines = self.grade(broken)
        self.assertFalse(passed)
        self.assertTrue(any(l.startswith("FAIL clean: Ostlund runs 140 vehicles") for l in lines))

    def test_calling_the_doubtful_line_wrong_speaker_fails(self) -> None:
        header = "## C9. Tom signs off up to £25k a year  [said]"
        start = self.check_text.index(header)
        end = self.check_text.index("- Failures: none", start)
        broken = self.check_text[:end] + "- Failures: wrong-speaker" + self.check_text[end + len("- Failures: none") :]
        passed, lines = self.grade(broken)
        self.assertFalse(passed)
        self.assertTrue(any("failures: C9 wrong-speaker" in l for l in lines))

    def test_any_failure_on_the_mislabelled_line_fails(self) -> None:
        header = "## C10. Board signs off above £25k  [said]"
        start = self.check_text.index(header)
        end = self.check_text.index("- Failures: none", start)
        broken = self.check_text[:end] + "- Failures: made-up-detail" + self.check_text[end + len("- Failures: none") :]
        passed, lines = self.grade(broken)
        self.assertFalse(passed)
        self.assertTrue(any("failures: C10 made-up-detail" in l for l in lines))


if __name__ == "__main__":
    unittest.main()
