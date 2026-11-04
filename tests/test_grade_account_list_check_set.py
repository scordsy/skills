"""Tests for check-account-list's check set grader: a right answer passes, and a missed plant, a dropped
clean company or a name trap marked closed fails. Every saved run that passed is graded again against
the current key."""

from __future__ import annotations

import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "tests" / "check-account-list"
spec = importlib.util.spec_from_file_location("account_list_grader", HERE / "grade_check_set.py")
assert spec and spec.loader
grader = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = grader
spec.loader.exec_module(grader)
accounts = grader.accounts

KEY = json.loads((HERE / "check-set" / "answer-key.json").read_text(encoding="utf-8"))
# Saved runs the README records as passed. CI fails if the key and the evidence drift apart.
PASSED_RUNS = ["2026-11-04-run-1-high", "2026-11-04-run-2-medium", "2026-11-04-run-2-high", "2026-11-04-run-3-medium", "2026-11-04-run-3-high"]


def record(ident: str, name: str, verdict: str, problems: list[str]) -> str:
    return "\n".join(
        [
            f"## {ident} | {name}",
            f"- Verdict: {verdict}",
            f"- Problems: {', '.join(problems) or 'none'}",
            "- Reason: test",
        ]
    )


def right_answer() -> dict[str, tuple[str, list[str]]]:
    out = {}
    for ident, want in KEY["companies"].items():
        out[ident] = ("drop", list(want["required"])) if want["expect"] == "planted" else ("keep", [])
    return out


def grade(answers: dict[str, tuple[str, list[str]]]) -> tuple[bool, list[str]]:
    text = "\n\n".join(record(i, KEY["companies"][i]["name"], v, p) for i, (v, p) in answers.items())
    records = {r.id: r for r in accounts.parse_records(text, "test.md")}
    return grader.grade(records, KEY)


class AccountListGraderTest(unittest.TestCase):
    def test_the_right_answer_passes(self) -> None:
        passed, lines = grade(right_answer())
        self.assertTrue(passed, "\n".join(lines))

    def test_a_clean_company_sent_to_check_by_hand_passes_with_a_note(self) -> None:
        answers = right_answer()
        answers["A01"] = ("check-by-hand", [])
        passed, lines = grade(answers)
        self.assertTrue(passed)
        self.assertTrue(any(l.startswith("note A01") for l in lines))

    def test_a_dropped_clean_company_fails(self) -> None:
        answers = right_answer()
        answers["A12"] = ("drop", ["wrong-fit"])
        passed, lines = grade(answers)
        self.assertFalse(passed)
        self.assertTrue(any(l.startswith("FAIL A12") for l in lines))

    def test_a_missing_required_problem_fails(self) -> None:
        answers = right_answer()
        answers["A02"] = ("drop", ["bought"])
        passed, lines = grade(answers)
        self.assertFalse(passed)
        self.assertTrue(any(l.startswith("FAIL A02") and "missing customer" in l for l in lines))

    def test_a_planted_company_kept_or_sent_to_check_by_hand_fails(self) -> None:
        for verdict in ("keep", "check-by-hand"):
            with self.subTest(verdict):
                answers = right_answer()
                answers["A10"] = (verdict, [])
                passed, _ = grade(answers)
                self.assertFalse(passed)

    def test_a_name_trap_marked_closed_fails(self) -> None:
        answers = right_answer()
        answers["A14"] = ("drop", ["bought", "wrong-size", "closed"])
        passed, lines = grade(answers)
        self.assertFalse(passed)
        self.assertTrue(any("must not be closed" in l for l in lines))

    def test_an_extra_problem_is_a_note_not_a_failure(self) -> None:
        answers = right_answer()
        answers["A04"] = ("drop", ["competitor", "bought"])
        passed, lines = grade(answers)
        self.assertTrue(passed)
        self.assertTrue(any(l.startswith("note A04") and "bought" in l for l in lines))

    def test_a_missing_record_fails(self) -> None:
        answers = right_answer()
        del answers["A20"]
        passed, lines = grade(answers)
        self.assertFalse(passed)
        self.assertTrue(any(l.startswith("FAIL A20") for l in lines))

    def test_the_unsettled_company_passes_kept_or_dropped_only_as_bought(self) -> None:
        for answer, ok in ((("check-by-hand", []), True), (("drop", ["bought"]), True), (("drop", ["bought", "wrong-fit"]), False)):
            with self.subTest(answer):
                answers = right_answer()
                answers["A05"] = answer
                passed, _ = grade(answers)
                self.assertEqual(passed, ok)

    def test_the_key_covers_every_problem_type(self) -> None:
        planted = {p for want in KEY["companies"].values() for p in want.get("required", [])}
        self.assertEqual(planted, set(accounts.PROBLEMS))
        expects = [want["expect"] for want in KEY["companies"].values()]
        self.assertEqual((expects.count("clean"), expects.count("unsettled"), expects.count("planted")), (5, 1, 14))

    def test_the_saved_runs_pass_against_the_current_key(self) -> None:
        for name in PASSED_RUNS:
            with self.subTest(name):
                run = HERE / "check-set" / "runs" / name
                passed, lines = grader.grade(grader.final_records(run), KEY)
                self.assertTrue(passed, "\n".join(lines))


if __name__ == "__main__":
    unittest.main()
