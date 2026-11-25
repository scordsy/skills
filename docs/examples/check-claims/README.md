# check-claims: example run

A real run of the skill on a real AI-written article: draft A1 from the [test of the problem](../../../tests/check-claims/problem-test/README.md), "Why B2B Buying Committees Keep Growing, and What Marketers Should Do About It". Claude wrote it on 25 November 2026 with web search switched off, from the first prompt in [`prompts.md`](../../../tests/check-claims/problem-test/prompts.md). A subagent wrote it, not a chat, so there is no conversation to link to: the prompt and the draft are both in that folder, exactly as used.

| File | What it is |
|---|---|
| `A1.md` | The draft, exactly as given |
| `draft-lines.md` | The draft with its 55 sentences numbered, written by the script |
| `claims.md` | The reader's list: 25 claims |
| `working/research-*.md` | Each researcher's records, as written |
| `check-in/to-check-*.md` | What each checker was given: the claims and verdicts only |
| `working/check-*.md` | Each checker's records, as written |
| `working/evidence.json` | Whether the script found each quote on its page |
| `check.md` | The report, built by the script |
| `marked.md` | The draft with a mark beside every claim |

## What it found

The report opens: "12 of the 25 claims need nothing from you."

| What to do | Claims |
|---|---|
| Fix: the first publisher says something else | 4 |
| Update or re-credit: supported, with a newer figure to give | 3 |
| Your call: no source was found | 1 |
| Confirm with a person: a page to open yourself | 5 |
| Nothing to do | 12 |

- **No figure was wrong when it was written. Several are stale.** The draft's three 6sense figures have all been replaced: the buying group of 11 is now 10, the 70% is now 59%, and the first vendor contacted now wins 76.6% of the time, not four times in five.
- **One publisher disagrees with itself.** Forrester's press release says 86% of purchases stall. Its own blog post on the same report says 91%.
- **Five claims sit on pages that would not open**, four of them Gartner's, which met every request with a check for a human. The fifth is a Harvard Business Review article behind its paywall. The report gives the address and what to look for on each.
- **Two claims were firmer than their sources.** Snowflake and Salesforce each have a tool for working out a return. Neither page says they "invest heavily".

One update, as the report gives it:

> **The draft says:** "the vendor they contact first wins the deal about four times out of five"
> **Use instead:** In 2023 6sense found that 84% of buyers bought from the first vendor they contacted. Its 2026 report gives 76.6%.

## How it ran

Run on 25 November 2026 in Claude Code, on the subagent route: 7 subagents, all on one model, and 925,655 tokens. The reader took 1 minute 35 seconds. The 3 researchers ran side by side, the longest for 7 minutes 10 seconds. The 3 checkers re-checked 18 claims, the longest for 8 minutes 44 seconds, and changed 3:

- a claim resting on the Harvard Business Review article went from supported to could-not-open, because the page shows only its opening paragraph and the figure is not in it;
- the Forrester 86% gained publisher-disagrees;
- one 6sense claim kept its verdict and changed its problem types.

**The script confirmed 26 of 42 quotes.** The other 16 are on two sites that refused its page loader with an HTTP 403: `6sense.com` and `sec.gov`. The researchers and checkers could read both with the assistant's own page reader, so the claims were traced, but those quotes were not confirmed by code. The report says so beside each one.

`marked.md` was written with a short helper that follows the skill's hand-back rules, then checked as those rules ask: 25 marks for 25 claims, and with the marks taken out, the draft exactly as given.

The same draft was traced by hand in the test of the problem, before the skill existed. That record is in [`records.json`](../../../tests/check-claims/problem-test/records.json), under A1. No subagent in this run was shown it.
