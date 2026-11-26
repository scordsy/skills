# check-account-list check set

Tests the whole run: do the researchers and the checker catch one planted problem of each type, see through the name traps, and leave the clean companies alone?

| File | What it is |
|---|---|
| `check-set/list.csv` | 20 real companies with the website as given: 6 clean, 14 planted |
| `check-set/profile.md` | The profile they are checked against, for a made-up seller |
| `check-set/answer-key.json` | What each company should get, written by hand before any run |
| `check-set/ground-truth.md` | Every fact behind the key, with the Companies House page, register entry or company page it came from |
| `check-set/runs/` | Each run's records, the checker's records and the report, kept as evidence |
| `grade_check_set.py` | Grades a run against the answer key |

The seller is made up: a customer review and advocacy platform sold to the marketing teams of B2B software companies, with Breathe HR as its best customer. Breathe and the 20 companies have nothing to do with it. A drop here means "does not fit this made-up seller", not a judgement on the company.

## What is planted

| Problem type | Planted in |
|---|---|
| wrong-website | Titania, given as titaniasecurity.com, which does not load |
| closed | Wejo, in administration |
| bought | Rotageek, Weekly10 (its site now lands on its buyer's), Interact, Engager |
| not-in-country | Pinpoint (Jersey), Fiken (Norway) |
| wrong-size | Capsule CRM (35 staff), Goodlord (318), Engager (3) |
| wrong-fit | Interact, which sells an intranet to enterprises |
| competitor | Feefo (reviews) and Mention Me (referrals), neither named in the profile, so they must be caught by the kind of product |
| customer | Rotageek, in the best customer's own group, and Crunch, named as an existing customer |
| duplicate | Zestia, the company behind Capsule CRM, under a different name and website, in the same batch. A duplicate in another batch is caught by the report comparing company numbers, which has a unit test but has not yet come up in a run |

Three are name traps, where Companies House holds a company with the same or a similar name that is unrelated: Engager, Interact and Pinpoint. Marking any of them closed fails.

The 6 companies written as clean (RotaCloud, Payescape, SeedLegals, CyberSmart, Apron and Commusoft) are UK companies of 50 to 200 staff from their filed accounts, active, not owned by a larger group or bought in the last five years, and selling to small businesses. Payescape is now **unsettled**: run 3's checker found a July 2026 filing, which I confirmed, that puts one long-standing investor above 50%. Whether that counts as bought is not settled, so it passes kept, sent to check by hand, or dropped for bought alone.

## Running it

1. Set up a run folder outside this repo, so no researcher or checker can find the answer key:

   ```bash
   R="$TMPDIR/cal-checkset"
   A=skills/check-account-list/scripts/accounts.py
   mkdir -p "$R/working" "$R/check-in"
   cp tests/check-account-list/check-set/profile.md "$R/profile.md"
   python3 $A load tests/check-account-list/check-set/list.csv "$R/companies.md"
   python3 $A web "$R/companies.md" "$R/web.md"
   python3 $A split "$R/companies.md" "$R/web.md" "$R/working"
   ```

2. Run Stages 3 to 6 of `SKILL.md` exactly as written: one fresh researcher per batch, `verify`, `strip`, one fresh checker per batch with records to check, `verify` again, then `report`.

3. Grade it:

   ```bash
   python3 tests/check-account-list/grade_check_set.py "$R"
   ```

The grade fails on any company with no record, any planted company not dropped or missing a required problem type, any name trap marked closed, and any clean company dropped. A clean company sent to check by hand passes with a note. Extra problem types on a planted company are notes: several planted companies have more than one true problem, and the key requires only the ones `ground-truth.md` proves.

## Before each release

These facts go stale: companies are bought, go into administration and change their websites. Re-read every source in `ground-truth.md`, update the key if anything has changed, then run the set again.

## Results

Each run was the skill as written, in Claude Code, with every researcher and checker a fresh subagent at the stated effort. Tokens are all subagents together. Time is the longest researcher plus the longest checker, the two stages that run in parallel.

| Run | Effort | Result | Planted caught (of 14) | Clean kept | Payescape | Re-checked, changed | Tokens | Time |
|---|---|---|---|---|---|---|---|---|
| 3 | medium | **passed** | 14 | 5 of 5 | check by hand | 15, 3 | 812,717 | 19 min 2 s |
| 3 | high | **passed** | 14 | 5 of 5 | dropped, bought | 16, 1 | 767,178 | 26 min 0 s |
| 2 | medium | passed | 14 | 5 of 5 | keep | 15, 0 | 690,363 | 16 min 38 s |
| 2 | high | passed | 14 | 5 of 5 | keep | 17, 1 | 761,605 | 27 min 9 s |
| 1 | medium | failed | 12 | 5 of 5 | keep | 10, 0 | 698,312 | 15 min 28 s |
| 1 | high | passed | 14 | 5 of 5 | keep | 11, 1 | 713,722 | 20 min 14 s |

Run 3 is the published result: the skill as it stands, after the fix from run 1 and the fixes and decisions from the two reviews. Runs 1 and 2 are kept so nobody reads run 3 as a first try.

- **4 November 2026, run 1** (`runs/2026-11-04-run-1-medium/`, `runs/2026-11-04-run-1-high/`). High passed. Medium failed on two companies, both dropped for the right reason but missing a second problem: Interact was dropped as wrong-fit without finding that its parent company had been bought in December 2025, and Engager was dropped as bought without its size. The records show why. Once the medium researcher found one problem it stopped ("accounts not opened; dropped on fit"), and for Interact it read only the direct owner, a holding company that has owned it since 2016, and never asked who owns the holding company. The checker never saw either, because a drop whose quotes the script confirms goes straight to the report.
- **The fix**, to `references/research.md`, `record-format.md` and `checker.md`, with the spec: finish all six checks even after finding a problem, and follow owners up to the top of the chain, because a holding company that has owned a company for years can itself have been bought. Both apply to any list. Neither names a company in this set.
- **4 November 2026, run 2** (`runs/2026-11-04-run-2-medium/`, `runs/2026-11-04-run-2-high/`), fresh run folders, the same list and key. Both passed: every planted problem caught with the right type, all three name traps seen through, no clean company dropped or sent to check by hand. Medium was cheaper and faster on this set. The high checker removed wrong-size from Interact (its group accounts give 200 staff, inside the range) and the high researcher added that Crunch is part-owned by an accountancy firm since August 2024. Both are notes, not failures.

- **The reviews' changes**, after run 2: claim lines hold facts and the documents they come from, with no reasoning, because they are all the checker sees ([ADR 0016](../../docs/adr/0016-claims-are-facts-and-group-ownership-has-no-age-limit.md)). Bought now covers any change of control, and a company owned by a trading group of any age when the profile does not want group-owned companies. And the script's record checks are tighter. Those change what researchers write, so the set was run again.
- **4 November 2026, run 3** (`runs/2026-11-04-run-3-medium/`, `runs/2026-11-04-run-3-high/`), fresh run folders. Both passed: every planted problem caught with the right type, all three name traps seen through, no clean company dropped. Both checkers found something the key had missed: a filing of 31 July 2026 that puts one of Payescape's long-standing investors above 50% from 17 July 2026. The register's summary page still shows the old 25 to 50%, which is what I read when writing the key. I confirmed the filing myself, and Payescape is now unsettled (see above). The key was changed during run 3, after the medium checker found the filing and before the high result came in. **Under the key as first written, run 3 high would have failed** on Payescape, dropped as bought on a real filing. Medium sent it to check by hand, which passes either way.

Every run had a quote or two the script could not find on the first pass (a page that changes between loads, a one-word quote). Stage 4 sent each back to a fresh researcher, which fixed it, and the tokens above include those fixes. Most size evidence is in accounts PDFs, which the script cannot read, so those drops went to the checker as ADR 0014 intends.

After the two reviews, the key's lists of allowed extra problem types were taken out, because `ground-truth.md` did not prove them. Every extra type now shows as a note. The required and forbidden types, which decide pass or fail, are as written before run 1. The one other change to the key is Payescape, above.

**19 November 2026, on Claude.ai**, in a normal chat with memory off, on plugin version 0.3.1, with 12 of the 20 companies to keep the cost down: RotaCloud, SeedLegals and Commusoft clean, and Capsule CRM, Zestia, Feefo, Pinpoint, Wejo, Interact, Engager, Titania and Crunch planted. That covers every problem type and all three name traps. Payescape, the unsettled one, was left out. I played the made-up seller through the profile interview. The chat could launch subagents, so it took the subagent route: 2 research batches and separate checkers. Passed every rule in the key, graded by hand against the key as it stood: 3 kept, 9 dropped with every required problem type and no forbidden one, and nothing sent to check by hand. The script confirmed 128 quotes, and 11 were in PDFs, which the checker reviewed. The checker re-checked 9 companies and changed nothing. Notes, not failures: extra types on Zestia (wrong-size), Wejo (wrong-website, a parked domain) and Titania (wrong-size and wrong-fit, with the size read from a scanned PDF and not confirmed). The run's files are not saved here, so CI does not grade it.

In the profile interview it asked for the list and its first question in the same message, and after seeing the list it added Feefo to the named competitors. That would have given away the test of catching Feefo by the kind of product, so it was taken out before the profile was approved. Both are fixed in 0.3.2 ([ADR 0018](../../docs/adr/0018-the-list-comes-after-the-profile.md)): the list is asked for only once the profile is approved, and nothing in the profile comes from it.

**19 November 2026, release 0.3.2: not rerun, on Stefan's call.** 0.3.2 changes how each skill starts (it opens its own files first, and stops if it can't), the interview wording, and when check-account-list asks for the list. None of the instructions, reference files or scripts this check set exercises (the research and checker instructions, their briefs and the script) changed, so the set was not run again, and its answer key was not re-confirmed against Companies House and the companies' own sites. The changed behaviour is to be retested on Claude.ai instead.

**25 November 2026, release 0.4.0: not rerun, on Stefan's call.** 0.4.0 adds a fourth skill, check-claims, and changes nothing in this skill's instructions, reference files or script. So this check set was not run again and its answer key was not re-confirmed.

**25 November 2026, release 0.4.1: not rerun, on Stefan's call.** 0.4.1 changes only the wording of check-claims' description, in the skill, the plugin and the marketplace entry. No instruction, reference file or script changed in any skill, so no check set was run again and no answer key was re-confirmed.

**26 November 2026, release 0.4.2: not rerun, on Stefan's call.** 0.4.2 changes only what each skill says when it stops at its first step: a skill saved without its files, for example from a chat's save shortcut, now says so and how to reinstall it. None of the instructions, reference files or scripts this check set exercises changed, so the set was not run again and no answer key was re-confirmed. The new message was tested instead, in Claude Code with only each skill's main file installed: check-call-summary and find-events both stopped and gave the reinstall steps. A complete install of check-call-summary still passed its first step.

A unit test grades every passing saved run against the current key, so CI fails if the key and the evidence drift apart.
