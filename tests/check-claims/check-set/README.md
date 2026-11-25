# check-claims check set

Tests the whole run: do the reader, the researchers and the checker catch one planted problem of each type, give both out-of-date claims the right verdict, split a story into its parts, and leave the clean claims alone?

| File | What it is |
|---|---|
| `article.md` | A made-up article of 39 sentences, with 15 planted problems and 6 clean claims |
| `email.md` | A made-up sales email of 10 sentences: one planted problem, three clean claims, and two claims that must not be traced |
| `answer-key.md` | What each claim should get, with the first publisher's page, its exact words and the date it was read. Written by hand before any run |
| `runs/` | Every run: the claims list, each researcher's and checker's records, the report and the marked draft |

Both drafts are made up, and so are the seller Quillmere and the people named in the email. Their claims point at real public pages. Where a draft says something a real company's page does not say, that is the planted problem. Nothing here is a statement about those companies.

Unlike the drafts in the [test of the problem](../problem-test/README.md), these give a web address for some claims and quote a named person, because three problem types cannot be planted without them.

## What is planted

| Planted | Where |
|---|---|
| out-of-date, stated as the present position (must differ) | The fee to register a company, given as £50. It is £100 |
| number-wrong | A survey's 43% given as 53% |
| base-dropped | 40% of businesses that identified a breach, given as 40% of businesses |
| strength-changed, overstated | A cap on payment terms the government intends, given as law |
| second-hand | A government intention credited to a law firm's page that repeats it |
| publisher-disagrees | Forrester's 86%, where its own blog post on the same report says 91% |
| source-mislabelled | Gong's research credited to Salesforce |
| out-of-date, stated as a past finding (must stay supported) | Gong's $300 million of March 2025. It has since said $500 million |
| a report closed to the skill | A figure said to be in a Forrester report that is sold to clients |
| strength-changed, understated | Google's "more than 99.9%" given as "up to 99.9%" |
| no findable source | A figure made up for the draft |
| misquoted | Two words changed in a sentence of Paul Graham's |
| a story to split, one part unsupported | Stripe's "Collison installation", with a made-up count of customers added |
| page-gone, on a link the draft gives | A Salesforce address that answers 404 |
| page-gone, on a first publisher's page | RollWorks' case study on PayScale, which is no longer on its site |
| wrong-subject, one company's fact pinned on two | "Slack and Mailchimp, which are both part of Salesforce now" (in the email) |
| not to be traced | The sender's own results, and a named person's career (in the email) |

## Passing

A run passes when, graded by hand against `answer-key.md`:

- every planted problem carries its required problem type, and its required verdict where the key pins one;
- both out-of-date claims have the right verdict: the present-position one differs, the past-finding one is supported;
- the story is split into three or more claims, and its made-up part is not supported;
- no clean claim is marked `differs`;
- the two claims that must not be traced are listed and not traced.

Other problem types on a planted claim are notes, not failures. So is a clean claim that comes back `could-not-open` or `no-source`.

The grading is by hand because the reader numbers the claims, so the numbers differ from run to run.

## Running it

1. Make a run folder outside this repo, so no subagent can find the answer key, and number the draft:

   ```bash
   R="$TMPDIR/cc-checkset/check-claims/$(date +%F)-article"
   mkdir -p "$R/working" "$R/check-in"
   cp tests/check-claims/check-set/article.md "$R/"
   python3 skills/check-claims/scripts/claims.py number "$R/article.md" "$R/draft-lines.md"
   ```

2. Run Stages 2 to 6 of `SKILL.md` exactly as written: a fresh reader, a fresh researcher per batch of 10, `verify`, `report`, a fresh checker per file in `check-in/`, `verify`, `report`, then the marked draft.
3. Do the same for `email.md`.
4. Copy each run folder into `runs/`, leaving out `working/pages/`, which holds the full text of other people's pages.
5. Grade it by hand against the key and add the result below.

## Before each release

Pages change. Read every page in `answer-key.md` again, change the key if a fact has moved, and say so here. The key's last section lists what is likeliest to go stale.

## Results

Both runs were the skill as written, in Claude Code on 25 November 2026, with every reader, researcher and checker a fresh subagent. The run's own logs show all 20 on one model, `claude-fable-5-2`, and show that none of them opened the answer key. Tokens are all subagents together. Time is the reader, plus the longest researcher, plus the longest checker, because researchers run side by side and so do checkers.

| Run | Draft | Result | Claims | Planted caught | Clean marked differs | Re-checked, changed | Quotes found by the script | Tokens | Time |
|---|---|---|---|---|---|---|---|---|---|
| 2 | article | **passed** | 25 | 15 of 15 | 0 | 13, 1 | 37 of 38 | 877,973 | 10 min 23 s |
| 2 | email | **passed** | 12, of which 5 traced | 1 of 1, and 2 of 2 not traced | 0 | 5, 0 | 13 of 14 | 352,278 | 6 min 48 s |
| 1 | email | passed | 14, of which 6 traced | 1 of 1, and 2 of 2 not traced | 0 | 5, 1 | 17 of 19 | 346,597 | 8 min 41 s |
| 1 | article | failed, on the key | 27 | 14 of 15 | 0 | 16, 1 | 38 of 40 | 952,931 | 11 min 59 s |

Run 2 is the published result: the skill as it stands, after the reader's rule and the script's fix below. Run 1 is kept so nobody reads run 2 as a first try.

### Run 1 (`runs/2026-11-25-run-1/`)

**The email passed.** The claim that Slack and Mailchimp are both part of Salesforce came back as two claims: Slack supported, Mailchimp differs with wrong-subject. The three clean claims stayed clean. The sender's results and the named person's career were listed and not traced. The checker also found that Intuit agreed on 19 November 2026 to sell Mailchimp, six days before the run, and put it in the words to use.

**The article failed on two rows of the key as first written, and both faults were the key's.** One was the second-hand sentence, described under it. The other was a claim about Gong's State of Revenue AI 2026 report, planted as "behind a sign-up form". The form is real. But Gong also hosts the report as a file anyone can open, and the researcher and the checker each found it and read all 22 pages. Nothing stood in the way, so the claim came back `no-source` where the key asked for `could-not-open`. Every other planted problem was caught with the right type, the story became four claims, and no clean claim was marked `differs`.

Two more things run 1 showed:

- **The key's second-hand sentence was stale as I wrote it.** It said the government "intends" to require statutory interest. The checker moved it from supported to differs, because the government has since put a bill before Parliament. It kept second-hand, the required type, but the key had pinned the verdict as supported, so this row failed too. The checker was right and the sentence was mine.
- **The reader split facts from their own dates and amounts.** "Rose to £12.71 an hour in April 2026" became two claims, one of them just "in April 2026". "Agreed to buy Slack at an enterprise value of $27.7 billion" became two, and the named person's one sentence became four. Nothing was missed, but the report and the marked draft repeated themselves, and more claims went against the cap than the draft needed.

### What changed between the runs

- **The check set.** The Gong row was replaced by a claim about a Forrester report that is sold to clients, and the spec's list of what the check set plants now says "a report that is closed to the skill (behind a sign-up form or sold to clients only)". The second-hand sentence now dates the intention to March 2026. `answer-key.md` records both changes. No required verdict or type was loosened.
- **The reader's instructions.** `references/reader.md` gained one rule: a fact keeps its own date, amount and length of time. The spec's stage 2 says the same. It names no claim in this set.

### Run 2 (`runs/2026-11-25-run-2/`)

The article again, in a fresh run folder. **Passed**: all 15 planted problems caught with the right type and the right verdict, both out-of-date claims right, the story split into four with its made-up part `no-source`, and no clean claim marked `differs`. The reader listed 25 claims and split nothing from its date. The Forrester report came back `could-not-open`, with the address, what stood in the way (a client login or a purchase) and what to look for.

The email again, also in a fresh run folder. **Passed**, as in run 1: Slack supported, Mailchimp differs with wrong-subject, three clean claims supported, and seven claims about the sender and the named person listed and not traced. The reader listed 12 claims where run 1's listed 14, and kept "rose to £12.71 an hour in April 2026" as one.

Notes on the article, not failures:

- The second-hand claim also carries out-of-date, for the bill.
- The reader listed "most of them have no procurement team" as a claim, and it came back `no-source`. The key does not mention it. Listing a sentence when unsure is what the reader is told to do.
- Three extra clean claims were listed and supported: that Gong sells this kind of software, that Stripe is the essay's example, and each half of a two-sentence quotation.

### What the first live runs showed about the script

`verify` had never loaded a live page before these runs. Across the four it loaded pages on `gov.uk`, `forrester.com`, `gong.io`, `paulgraham.com`, `salesforce.com`, `slack.com`, `intuit.com`, `safety.google`, `adroll.com` and `mailchimp.com`, and found 105 of the 111 quotes in the final reports.

- **One quote came back not found, and the script was wrong.** Forrester's press release holds "86" and "%" in two tags, so the page's text reads "86 %", and a researcher's exact "86% of B2B purchases stall" was not found. A gap between a figure and its percent sign is spacing, which the spec says is ignored. The script now closes it, with a test whose page is that sentence. In run 1 the researcher had copied the quote with the gap in it, so it passed there.
- **Five quotes sat in PDFs**, which the script does not read: a government research report and an Intuit release. Each claim went to the checker, as the spec intends.
- **One site refused the script:** `sec.gov` answered HTTP 403 to its browser identity. A checker had cited it as a third quote for a claim that had two others found.
- **Sites that refused a researcher or checker**, each recorded in its record: Parliament's bill pages (a bot check), and `rollworks.com`, which sends the case study's address to another site's library.
- **No sign-up form stopped anything.** The one form in the set had an open file behind it.

Two lines went into every brief that are not part of the skill, because of where these runs happened: never use the browser extension, and a note that this machine's shell only reaches a site once the command names it, so a blocked request is not a site refusing. Without the second, a blocked request would have been written down as a page that would not open.

### How the marked drafts were made

The skill's instructions have the assistant write `marked.md` by hand. In these runs I wrote it with a short helper that follows the rules in `references/hand-back.md`: a mark after each claim's draft words, then the record's words to use and its link. Each saved one was then checked the way that file asks: one mark for every claim, and with the marks taken out, the draft exactly as given. The closing message to the user that the same file sets out was not written, because there was no user in these runs.

### Not covered

- **A real sign-up form.** No run met one. The one form in the set had an open file behind it, and the claim that replaced it sits behind a client login.

- **The chat route** has not been run, and nor has the block it builds for a fresh chat.
- **A draft in parts.** The article has 25 claims, under the cap of 40, so no run was split. The script said the chat route's cap of 15 out loud. The line for 40 was not seen.
- **A second writer or a second model.** Every subagent ran on one model.
