# find-events check set

Tests the check stage: does a checker that never saw how records were found catch known errors, without inventing any?

| File | What it is |
|---|---|
| `check-set/records.md` | 10 event records. 5 accurate, 5 with one planted error each |
| `check-set/answer-key.json` | Which record carries which error, and the verdict expected |
| `check-set/ground-truth.md` | Every fact behind the records, with the organiser's page it came from |
| `check-set/runs/` | Checker output from each run, kept as evidence |
| `grade_check_set.py` | Grades a checker's output against the answer key |

## Running it

1. Strip the records into a folder outside this repo, so the checker can neither see the note at the top of `records.md` nor find the answer key:

   ```bash
   mkdir -p /tmp/checkset
   python3 skills/find-events/scripts/records.py strip tests/find-events/check-set/records.md /tmp/checkset/to-check.md
   ```

2. Brief a fresh general-purpose Claude Code subagent exactly as `SKILL.md` briefs a checker, with the three facts from `answer-key.json`: category **vendor**, window **1 December 2026 to 31 December 2027**, and who they want to meet: **operations, finance and technology decision-makers at mid-sized companies in the UK and Europe**. Have it write to `/tmp/checkset/checked.md`.

3. Grade it:

   ```bash
   python3 tests/find-events/grade_check_set.py /tmp/checkset/checked.md
   ```

## Before each release

Event pages change. Re-read each organiser page listed in `ground-truth.md` (its stability notes say what is likely to move), update the records and the ground truth to match, then run the check again. A planted error only tests anything while the truth it contradicts is still true.

## Results

- **2 November 2026, run 1** (`runs/2026-11-02-run-1-checked.md`, on the records before the fix). All 5 planted errors caught. 3 corrections on records written as accurate; each was confirmed on the organiser's page, so the records were fixed (see the end of `ground-truth.md`). It fails against the current key, as it should.
- **2 November 2026, run 2** (`runs/2026-11-02-run-2-checked.md`). Passed: all 5 caught with the right type, nothing changed on the 5 accurate records. A unit test grades this run against the current key, so CI fails if the key and the evidence drift apart.
