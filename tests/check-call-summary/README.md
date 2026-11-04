# check-call-summary check set

Tests the reader and the checker together: does a run catch one planted failure of each type, flag both planted mislabels as doubtful labels, and leave the clean lines alone?

| File | What it is |
|---|---|
| `check-set/call.vtt` | A made-up 20-minute call with three speakers. Two lines carry a planted mislabel |
| `check-set/summary.md` | A summary of that call: one planted failure of each type, a left-out competitor, one line resting on a mislabelled line, and clean lines |
| `check-set/answer-key.json` | Every planted failure, the line it rests on and why, written by hand before any run |
| `check-set/runs/` | Each run's key facts and check file, kept as evidence |
| `grade_check_set.py` | Grades a run against the answer key |

Everything in the call is fictional: the companies, the people and the numbers.

## Running it

1. Set up a run folder outside this repo, so neither the reader nor the checker can find the answer key:

   ```bash
   R="$TMPDIR/ccs-checkset"
   mkdir -p "$R/summaries" "$R/reader-in" "$R/working"
   python3 skills/check-call-summary/scripts/transcript.py number tests/check-call-summary/check-set/call.vtt "$R/transcript-lines.md"
   cp "$R/transcript-lines.md" "$R/reader-in/"
   cp tests/check-call-summary/check-set/summary.md "$R/summaries/1-notetaker.md"
   ```

2. Brief a fresh general-purpose Claude Code subagent exactly as `SKILL.md` briefs the reader, writing `$R/key-facts.md`. Then brief a second fresh subagent exactly as `SKILL.md` briefs a checker, for the summary named `notetaker`, writing `$R/working/check-1-notetaker.md`.

3. Grade it:

   ```bash
   python3 tests/check-call-summary/grade_check_set.py "$R/transcript-lines.md" "$R/key-facts.md" "$R/working/check-1-notetaker.md"
   ```

The grade fails on any quote the script cannot find on its line, a planted failure missed or given the wrong type, a planted mislabel not flagged, any other line flagged as doubtful, the left-out competitor not marked missing as a `competitor` key fact, any claim from the mislabelled line not marked doubtful or given any failure, or any failure on a clean line. Extra failure types on a planted line and extra left-out key facts are listed as notes, not failed: the reader lists more key facts than the summary was written to carry, and some of them are fair catches.

The companies in the call were first written as Ostlund Haulage and Cartwheel. Cartwheel turned out to be a real company, so it was renamed Wheelrota after run 1, in every file at once.

## Results

- **4 November 2026, run 1** (`runs/2026-11-04-run-1/`). Passed. The reader listed 21 key facts and flagged both planted labels (L20, L35). The checker split the summary into 25 claims and caught all 6 planted failures with the right type and the left-out Wheelrota demo, marked both claims on the L20 line doubtful without calling them wrong-speaker, and put no failure on any of the 9 clean lines. Every quote verified. It also flagged "Doncaster and Wakefield" as overstated (Priya said "probably"), a fair catch on a planted line, and marked 4 more key facts as left out that the summary was never written to carry.
- **4 November 2026, run 2** (`runs/2026-11-04-run-2/`), on the skill as fixed after its two reviews, graded by the tightened grader. Passed. The reader listed 25 key facts and flagged both planted mislabels and nothing else. The checker split the summary into 25 claims, caught all 6 planted failures with the right type and the left-out Wheelrota demo, marked both claims from L20 doubtful with no failure, and put no failure on any clean line. Every quote verified first time.

A unit test grades every saved run against the current key, so CI fails if the key and the evidence drift apart.
