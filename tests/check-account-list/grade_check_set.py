"""Grade a check-account-list run on the check set against the answer key.

    python3 tests/check-account-list/grade_check_set.py <run folder>

Reads the run's final records the way the report does: the checker's record where there is one, the
researcher's otherwise. Passes when every planted company is dropped with each required problem type
and no forbidden one, no clean company is dropped, and the unsettled company is
kept, sent to check by hand, or dropped only for a problem type it accepts. Extra problem types, clean companies sent to
check by hand, and quotes the script could not find are reported as notes, not failed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCRIPT = ROOT / "skills" / "check-account-list" / "scripts" / "accounts.py"
spec = importlib.util.spec_from_file_location("accounts", SCRIPT)
assert spec and spec.loader
accounts = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = accounts
spec.loader.exec_module(accounts)

CHECK_SET = HERE / "check-set"


def final_records(run: Path) -> dict:
    research, checks, _ = accounts.merged(run)
    out = {r.id: r for r in research}
    out.update(checks)
    return out


def grade(records: dict, key: dict, states: dict | None = None) -> tuple[bool, list[str]]:
    out: list[str] = []
    passed = True

    def result(ok: bool, text: str) -> None:
        nonlocal passed
        passed = passed and ok
        out.append(("pass " if ok else "FAIL ") + text)

    for ident, want in key["companies"].items():
        label = f"{ident} {want['name']}"
        record = records.get(ident)
        if record is None:
            result(False, f"{label}: no record")
            continue
        found = record.problems
        shown = f"{record.verdict}" + (f" ({', '.join(found)})" if found else "")
        if want["expect"] == "unsettled":
            accepted = record.verdict != "drop" or (found and all(p in want["accept"] for p in found))
            result(accepted, f"{label}: unsettled, {shown}" + ("" if accepted else f"; only {', '.join(want['accept'])} is accepted"))
            continue
        if want["expect"] == "clean":
            result(record.verdict != "drop", f"{label}: clean, {shown}")
            if record.verdict == "check-by-hand":
                out.append(f"note {label}: clean but sent to check by hand: {record.fields.get('reason', '')}")
            continue
        required = want["required"]
        missing = [p for p in required if p not in found]
        forbidden = [p for p in want.get("forbidden", []) if p in found]
        ok = record.verdict == "drop" and not missing and not forbidden
        detail = f"{label}: needs {', '.join(required)}, got {shown}"
        if missing and record.verdict == "drop":
            detail += f"; missing {', '.join(missing)}"
        if forbidden:
            detail += f"; must not be {', '.join(forbidden)}"
        result(ok, detail)
        extra = [p for p in found if p not in required and p not in forbidden]
        if extra:
            out.append(f"note {label}: also marked {', '.join(extra)}")

    if states:
        counts = Counter(states.values())
        out.append("note evidence: " + ", ".join(f"{n} {s}" for s, n in sorted(counts.items())))
    return passed, out


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    run = Path(argv[0])
    key = json.loads((CHECK_SET / "answer-key.json").read_text(encoding="utf-8"))
    passed, out = grade(final_records(run), key, accounts.evidence_states(run))
    print("\n".join(out))
    print("\nPASSED" if passed else "\nFAILED")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
