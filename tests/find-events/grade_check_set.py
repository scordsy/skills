"""Grade a checker's output against the check set's answer key.

    python3 tests/find-events/grade_check_set.py <checked records file>

The check set is 10 records: 5 clean and 5 with one planted error each. The checker passes when it
catches every planted error with the right correction type, gives the expected verdict, and invents
no correction on a clean record. Extra correction types on a planted record are reported, not failed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCRIPT = ROOT / "skills" / "find-events" / "scripts" / "records.py"
spec = importlib.util.spec_from_file_location("records", SCRIPT)
assert spec and spec.loader
records = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = records
spec.loader.exec_module(records)


def grade(key: dict, checked: list) -> tuple[bool, list[str]]:
    by_number = {r.number: r for r in checked}
    lines: list[str] = []
    passed = True
    for number_text, expected in sorted(key["records"].items(), key=lambda item: int(item[0])):
        number = int(number_text)
        planted = expected.get("planted")
        label = f"{number:>2}. {expected['name']} ({planted or 'clean'})"
        record = by_number.get(number)
        if record is None:
            lines.append(f"FAIL {label}: missing from the checker's output")
            passed = False
            continue
        found = record.corrections
        problems: list[str] = []
        if found is None:
            problems.append("no Corrections line")
        elif planted and planted not in found:
            problems.append(f"missed {planted} (found: {', '.join(found) or 'none'})")
        elif not planted and found:
            problems.append(f"invented {', '.join(found)}")
        allowed = expected.get("verdicts", [])
        if allowed and record.verdict not in allowed:
            problems.append(f"verdict {record.verdict}, expected {' or '.join(allowed)}")
        if problems:
            lines.append(f"FAIL {label}: {'; '.join(problems)}")
            passed = False
        else:
            extra = [kind for kind in (found or []) if kind != planted]
            note = f" (also flagged: {', '.join(extra)})" if extra else ""
            lines.append(f"pass {label}{note}")
    return passed, lines


def main(argv: list[str]) -> int:
    if len(argv) != 1:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    key = json.loads((HERE / "check-set" / "answer-key.json").read_text(encoding="utf-8"))
    passed, lines = grade(key, records.read(Path(argv[0])))
    print("\n".join(lines))
    print("\nPASSED" if passed else "\nFAILED")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
