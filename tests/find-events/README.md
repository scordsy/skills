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

- **2 November 2026, run 1** (`runs/2026-11-02-run-1-checked.md`, on the records before the fix). All 5 planted errors caught. 3 corrections on records written as accurate. Each was confirmed on the organiser's page, so the records were fixed (see the end of `ground-truth.md`). It fails against the current key, as it should.
- **2 November 2026, run 2** (`runs/2026-11-02-run-2-checked.md`). Passed: all 5 caught with the right type, nothing changed on the 5 accurate records. A unit test grades this run against the current key, so CI fails if the key and the evidence drift apart.
- **4 November 2026, release check for v0.3.0.** Every organiser page in `ground-truth.md` was re-read first. Nine events were unchanged. Retail Technology Show now publishes a "commercial admission pass (£150 + VAT)" for vendors who are not exhibiting, so the ground truth now records it. Record 8 still says "Your price: not published": that is now a second, unplanted error, which the grader reports without failing. Accountex London's pages sit behind an "I'm not a robot" check, so they were read in a browser by a person.
  - **Run 3** (`runs/2026-11-04-run-3-checked.md`). Not a fair run. Record 8 had been edited to carry the £150 vendor price, which put the gate into the record, so there was no missing gate left to catch. The edit was reverted.
  - **Run 4** (`runs/2026-11-04-run-4-checked.md`). All 5 planted errors caught. Two corrections on records written as accurate. On Infosecurity Europe (record 1) the checker found the organiser's own 2026 news post: registration was "free until 5th May. After this date, the entry cost to attend will be £49". That is a fair catch, so record 1 and the ground truth were fixed. On HANNOVER MESSE (record 7) it changed the matchmaking rule from "three or more people" to "groups of 12 or more". That is wrong: the matchmaking page still says "only available for delegations of three or more people", and the 12-person rule belongs to a different delegation service.
  - **Run 5** (`runs/2026-11-04-run-5-checked.md`), on the fixed records. Failed. All 5 planted errors caught with the right type, and nothing invented on 4 of the 5 accurate records. The checker again changed HANNOVER MESSE's matchmaking rule to the other service's 12-person rule. It said it found "no three-person threshold anywhere on the organiser's site". It should have marked the rule unverified, not corrected it. This weakness is in the check instructions and was there on 2 November too. Nothing in find-events changed between runs 2 and 5.
- **4 November 2026, 0.3.1, after the fix.** `references/check.md` now says that not finding something is not the same as it being wrong: a correction needs an organiser's page about the same thing, and a field that cannot be confirmed is left as it is and noted as unverified.
  - **Run 6** (`runs/2026-11-04-run-6-checked.md`). HANNOVER MESSE was left alone this time. The checker also found a gate missed since 2 November: Accountex's terms of entry say "there is a £500 (+VAT) charge for non-exhibiting vendors, business development, sales and marketing professionals", and visitors agree "Not to solicit business anywhere on the show floor". Read in a browser and confirmed, so record 3 and the ground truth were fixed. It fails against the current key, as it should.
  - **Run 7** (`runs/2026-11-04-run-7-checked.md`), on the fixed records. Passed: all 5 planted errors caught with the right type, nothing invented on the 5 accurate records. A unit test now grades this run against the current key.
- **19 November 2026, release 0.3.2: not rerun, on my call.** 0.3.2 changes how each skill starts (it opens its own files first, and stops if it can't), the interview wording, and when check-account-list asks for the list. None of the instructions, reference files or scripts this check set exercises (the check instructions and the strip script) changed, so the set was not run again, and its records were not re-confirmed against the organisers' pages. The changed behaviour is to be retested on Claude.ai instead.
- **25 November 2026, release 0.4.0: not rerun, on my call.** 0.4.0 adds a fourth skill, check-claims, and changes nothing in this skill's instructions, reference files or script. So this check set was not run again and its answer key was not re-confirmed.
- **25 November 2026, release 0.4.1: not rerun, on my call.** 0.4.1 changes only the wording of check-claims' description, in the skill, the plugin and the marketplace entry. No instruction, reference file or script changed in any skill, so no check set was run again and no answer key was re-confirmed.
- **26 November 2026, release 0.4.2: not rerun, on my call.** 0.4.2 changes only what each skill says when it stops at its first step: a skill saved without its files, for example from a chat's save shortcut, now says so and how to reinstall it. None of the instructions, reference files or scripts this check set exercises changed, so the set was not run again and no answer key was re-confirmed. The new message was tested instead, in Claude Code with only each skill's main file installed: check-call-summary and find-events both stopped and gave the reinstall steps. A complete install of check-call-summary still passed its first step.
