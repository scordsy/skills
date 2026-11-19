# check-call-summary check set 2

Tests the reader and the checker together on a second made-up call, written after set 1 had passed so the skill was never tuned on it: does a run catch a new planted failure of each type, leave an accurate summary alone, and leave correctly labelled lines alone even when they look like mislabels?

| File | What it is |
|---|---|
| `halvercombe-follow-up.txt` | A made-up follow-up call with four speakers, one joining late, as a plain-text export: title, date and participant lines on top, then a speaker-and-time heading above each turn. 48 lines, timestamped across 9 minutes 38 seconds. No mislabels |
| `notetaker-2.md` | A notetaker's summary: one planted failure of each type, eight clean lines, and the audit committee rule left out |
| `rep-note.md` | A short, fully accurate rep note. Any failure on it is a false alarm |
| `answer-key.json` | Every planted failure, the line it rests on and why, the clean lines, the four lines that look like mislabels but are not, and the pass rule, written by hand before any run |
| `make_call.py` | Writes `halvercombe-follow-up.txt`, so the call can be rebuilt exactly |
| `runs/` | Each run's saved files, kept as evidence |

Everything in the call is fictional: the housing association, the supplier, the people and the numbers. The company name was searched before use and no real company was found.

It differs from set 1 on purpose: a plain-text export rather than `.vtt` captions, four speakers rather than three, two summaries in one run, one of them clean, and no real mislabels, only four lines that could be mistaken for them (L25, L27, L31, L47: people naming each other or themselves).

## Running it

1. Set up a run folder outside this repo, so neither the reader nor the checkers can find the answer key:

   ```bash
   R="$TMPDIR/ccs-checkset-2"
   S=tests/check-call-summary/check-set-2
   mkdir -p "$R/summaries" "$R/reader-in" "$R/working"
   python3 skills/check-call-summary/scripts/transcript.py number "$S/halvercombe-follow-up.txt" "$R/transcript-lines.md"
   cp "$R/transcript-lines.md" "$R/reader-in/"
   ```

2. Brief a fresh general-purpose Claude Code subagent exactly as `SKILL.md` briefs the reader. When it has finished, copy `reader-in/key-facts.md` to `$R/key-facts.md` and only then save the summaries:

   ```bash
   cp "$S/notetaker-2.md" "$R/summaries/1-notetaker-2.md"
   cp "$S/rep-note.md" "$R/summaries/2-rep-note.md"
   ```

   Brief two fresh subagents exactly as `SKILL.md` briefs a checker, one per summary, writing `$R/working/check-1-notetaker-2.md` and `$R/working/check-2-rep-note.md`. Run `verify` on each and `report`, as Stages 4 and 5 say.

3. Save the run to `runs/<date>-<name>/`: `transcript-lines.md`, `key-facts.md`, both check files, `check.md` and `corrected.md`. The key facts and the check files are what a full grade needs.

4. Grade it against `answer-key.json`. It passes when every quote verifies, all 6 planted failures in notetaker-2 are caught with the right type, no clean line of notetaker-2 and no line of rep-note gets a failure, the audit committee rule is listed as a who-decides key fact and marked missing or carried wrongly against the approved-budget claim, and no line is flagged as a doubtful label. Extra failure types on a planted line and extra left-out key facts are notes, not failures.

## How it is graded

**By hand, and partly in CI.** `grade_check_set.py` grades set 1 from a run's key facts and check files. The only run of this set saved its report (`check.md`) and corrected draft, not those, so that grader cannot run on it, and it has not been extended for this set's two-summary key.

The report still holds every claim, with its quotes, verdict and failures, and the key facts table with each summary's mark. So [`test_call_summary_check_set_2.py`](../../test_call_summary_check_set_2.py) re-verifies every claim quote in the saved report against the call with the skill's own quote check, confirms every line of both summaries was checked, and reads each rule in the key off the report. What it cannot check is the key facts' own quotes, which the report does not carry, or that the reader never saw a summary. When a run saves its key facts and check files, extend `grade_check_set.py` to this key and grade that run in full.

## Results

- **19 November 2026, on Claude.ai** (`runs/2026-11-19-claude-ai/`), in a normal chat with memory off, on plugin version 0.3.1. Passed every rule in the key. The chat could launch subagents, so it took the subagent route, with a separate reader that never saw the summaries. The reader listed 17 key facts. It read the plain-text export cleanly: Joe's first spoken line is L1, so the title, date and participant lines were not counted.
  - **notetaker-2**: 21 claims. All 6 planted failures caught with the right type: wrong-speaker on the SSO requirement, tone-read-as-sincere on "pay double", made-up-detail on the 25 users, overstated on the budget, intention-as-done on the questionnaire, and owner-or-date-wrong on the export. No failure on any of the 8 clean lines. The audit committee rule was marked carried wrongly against the approved-budget claim, which the key accepts. It would have been a false fail under the key as first drafted, which is why the key takes either mark.
  - **rep-note**: 23 claims, no failures. 3 were marked inferred, all fair: the "follow-up" label, and the pound sign on 50,000 and 38,000, which nobody said aloud.
  - **Doubtful labels**: none flagged, so all four lines that look like mislabels passed.
  - **Quotes**: all 54 claim quotes in the report are on their lines, word for word and from the speaker cited. They were first checked by hand after the run, then by the CI test above.
