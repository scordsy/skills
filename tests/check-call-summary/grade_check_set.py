"""Grade a check-call-summary run on the check set against the answer key.

    python3 tests/check-call-summary/grade_check_set.py <transcript-lines.md> <key-facts.md> <check file>

Passes when the run's quotes all verify, every planted failure is caught with the right type (and a
made-up detail is not marked as said), both planted mislabels are flagged and no other line is, the
left-out competitor is marked missing as a competitor key fact, every claim from the mislabelled line
is marked doubtful with no failure, and no clean line gets a failure. Extra failure types on a planted
line and extra left-out facts are reported, not failed.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
SCRIPT = ROOT / "skills" / "check-call-summary" / "scripts" / "transcript.py"
spec = importlib.util.spec_from_file_location("transcript", SCRIPT)
assert spec and spec.loader
transcript = importlib.util.module_from_spec(spec)
# Dataclasses look their module up in sys.modules, so register it before running it.
sys.modules[spec.name] = transcript
spec.loader.exec_module(transcript)

CHECK_SET = HERE / "check-set"


def claims_from(check, line: str) -> list:
    target = transcript.plain(line)
    return [
        claim
        for claim in check.claims
        if any(target == transcript.plain(transcript.unquote(v)) for v in claim.get("From"))
    ]


def grade(lines, facts, doubts, summary: str, check, key: dict) -> tuple[bool, list[str]]:
    out: list[str] = []
    passed = True

    def result(ok: bool, text: str) -> None:
        nonlocal passed
        passed = passed and ok
        out.append(("pass " if ok else "FAIL ") + text)

    problems = transcript.verify_facts(lines, facts, doubts)
    more, hand = transcript.verify_check(lines, facts, doubts, summary, check)
    problems += more + [f"marked for checking by hand: {h}" for h in hand]
    result(not problems, "verify: " + ("all quotes on their lines, every line checked" if not problems else "; ".join(problems)))

    for planted in key["planted"]:
        found = claims_from(check, planted["line"])
        types = sorted({kind for claim in found for kind in transcript.failures_of(claim)})
        label = f"{planted['failure']}: {planted['line']}"
        if not found:
            result(False, f"{label} (no claim from this line)")
            continue
        extra = [t for t in types if t != planted["failure"]]
        note = f" (also flagged: {', '.join(extra)})" if extra else ""
        result(planted["failure"] in types, f"{label}{note}" if planted["failure"] in types else f"{label} (found: {', '.join(types) or 'none'})")
        if planted["failure"] == "made-up-detail":
            said = [c.ident for c in found if c.tag == "said"]
            result(not said, "made-up detail not marked as said" + (f" ({', '.join(said)} is)" if said else ""))

    for line in key["clean"]:
        found = claims_from(check, line)
        bad = [
            f"{c.ident} [{c.tag}] {', '.join(transcript.failures_of(c)) or ''}".strip()
            for c in found
            if transcript.failures_of(c) or c.tag not in ("said", "inferred")
        ]
        if not found:
            result(False, f"clean: {line} (no claim from this line)")
        else:
            result(not bad, f"clean: {line}" + (f" (marked {'; '.join(bad)})" if bad else ""))

    doubtful = key["doubtful_claim"]
    doubt_ids = {d.ident for d in doubts if int(d.tag) == doubtful["doubtful_line"]}
    found = claims_from(check, doubtful["line"])
    unmarked = [c.ident for c in found if not any(l.startswith("doubtful") and l.split("(")[-1].rstrip(")") in doubt_ids for l in c.get("Label"))]
    with_failures = [f"{c.ident} {', '.join(transcript.failures_of(c))}" for c in found if transcript.failures_of(c)]
    result(
        bool(found) and not unmarked and not with_failures,
        f"every claim from the mislabelled line marked doubtful, with no failure: {doubtful['line']}"
        + (" (no claim from this line)" if not found else "")
        + (f" (not marked doubtful: {', '.join(unmarked)})" if unmarked else "")
        + (f" (failures: {'; '.join(with_failures)})" if with_failures else ""),
    )

    flagged = {int(d.tag) for d in doubts}
    for number in key["doubtful_labels"]:
        result(int(number) in flagged, f"doubtful label flagged: L{number}")
    extra = sorted(flagged - {int(n) for n in key["doubtful_labels"]})
    result(not extra, "no other line flagged as doubtful" + (f" (also flagged: {', '.join(f'L{n}' for n in extra)})" if extra else ""))

    left = key["left_out"]
    on_lines = [
        f for f in facts if f.tag == left["kind"] and any(q.start <= n <= q.end for q in f.quotes for n in left["lines"])
    ]
    missing = [f.ident for f in on_lines if check.statuses.get(f.number, ("", None))[0] == "missing"]
    result(bool(missing), f"left-out: the {left['kind']} on L{left['lines'][0]} marked missing" + ("" if on_lines else " (no key fact lists it)"))
    others = sorted(
        f"{f.ident} {f.title}"
        for f in facts
        if check.statuses.get(f.number, ("", None))[0] == "missing" and f.ident not in missing
    )
    if others:
        out.append(f"note also marked missing: {'; '.join(others)}")
    return passed, out


def main(argv: list[str]) -> int:
    if len(argv) != 3:
        print(__doc__.strip().splitlines()[2].strip(), file=sys.stderr)
        return 2
    key = json.loads((CHECK_SET / "answer-key.json").read_text(encoding="utf-8"))
    lines = transcript.read_lines(Path(argv[0]))
    facts, doubts = transcript.read_facts(Path(argv[1]))
    summary = (CHECK_SET / "summary.md").read_text(encoding="utf-8")
    passed, out = grade(lines, facts, doubts, summary, transcript.read_check(Path(argv[2])), key)
    print("\n".join(out))
    print("\nPASSED" if passed else "\nFAILED")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
