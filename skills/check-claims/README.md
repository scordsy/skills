# check-claims

**Every fact in a draft traced to whoever first published it, before you publish or send it: still current, rightly credited, or not found, each with a link and the exact words.**

Ask an AI assistant for an article and you get one in a minute, with statistics, named studies and case studies in it. The facts come from the model's memory. A figure can be real and still be two editions old, linked to nothing, or credited to the wrong company. Reading the draft will not tell you which facts those are. Tracing each one will, and that is the slow part that gets skipped.

`check-claims` does the tracing. It lists every factual claim in your draft, finds whoever first published each one, and records what that page says today, with the web address and the exact words. A script loads each page to confirm the words are there. A separate checker, which never sees where the first pass looked, then tries to prove each claim wrong.

It checks a draft. It never writes one, never rewrites your prose, and never publishes or sends anything.

## Little to fix, in my test

I tested the problem before building the skill. Claude wrote six drafts, four B2B articles and two sales emails, and 58 of their claims were traced to their first publishers. 25 of the 58 needed nothing at all. 6 needed a fix. No figure that could be read was misstated: the faults were a figure the publisher had since replaced, or a real result credited to the wrong company.

That is one writer, on one day (25 November 2026), with web search switched off. A draft written by another assistant, or with search on, may carry different faults.

So the skill is not a hunt for wrong numbers, and its report is not a list of faults. It opens with how many claims need nothing from you, then gives the rest with the least work first:

1. **Fix these.** The first publisher says something else. The words to use are given, so each one is a paste.
2. **Update or re-credit these.** The claim holds, and there is a newer figure or a better source to give.
3. **Your call.** No source was found. You cut it, soften it or cite it yourself.
4. **Confirm with a person.** One visit or one question each: a page that would not open, or a claim about your own company.
5. **Nothing to do.** Every claim that stands, with its first publisher and date.

No verdict is softened to get that order. A claim that differs is said to differ.

## An example run

A real AI-written article, run live on 25 November 2026: "Why B2B Buying Committees Keep Growing, and What Marketers Should Do About It", written by Claude with web search switched off. It is one of the six drafts from my test below, and its prompt is kept beside it. The [whole run is here](../../docs/examples/check-claims/README.md).

The report opens: "12 of the 25 claims need nothing from you." Then:

| What to do | Claims |
|---|---|
| Fix: the first publisher says something else | 4 |
| Update or re-credit: supported, with a newer figure to give | 3 |
| Your call: no source was found | 1 |
| Confirm with a person: a page to open yourself | 5 |

No figure in the article was wrong when it was written. Several were stale. One update, as the report gives it:

> **The draft says:** "the vendor they contact first wins the deal about four times out of five"
> **Use instead:** In 2023 6sense found that 84% of buyers bought from the first vendor they contacted. Its 2026 report gives 76.6%.

The five pages to open yourself are four of Gartner's, which met every request with a check for a human, and one Harvard Business Review article behind its paywall. The run took 7 subagents and 925,655 tokens, and its longest researcher and longest checker ran for 7 minutes 10 seconds and 8 minutes 44 seconds.

- [`check.md`](../../docs/examples/check-claims/check.md), the report
- [`marked.md`](../../docs/examples/check-claims/marked.md), the article with a mark beside every claim

## What you get

Two files, in a folder beside your draft.

- **`check.md`**, the report, in the order above. Every claim is in it, with its first publisher, the date it was published, the page's exact words, and whether the script found those words on the page. It ends with the counts and with what was not checked.
- **`marked.md`**, your draft with a mark beside every claim, such as `[C02: supported, out-of-date]`. Where there are words to use instead, they follow the mark in bold with a link to the page. Nothing else in the draft is changed.

For every fact, that tells you three things:

- **Where it comes from.** The first publisher and its page, or a plain statement that none could be found.
- **Whether it is still current.** The date it was published, and any newer figure the same publisher has given since.
- **Whether the credit is right.** A right figure pinned on the wrong publisher is reported as firmly as a wrong figure.

## How it works

1. **Number.** A script numbers every sentence of the draft (a paste, `.txt`, `.md` or `.docx`), so every finding cites a sentence you can read.
2. **Claims.** A reader lists every factual claim, one fact each, and marks every other sentence as holding none. A story is split into its parts: "made a Batman comic starring the chief executive and won the account" is four claims, because one part can be true while another is not.
3. **Trace.** Batches of 10, each traced by its own fresh subagent. For each claim it finds the first publisher, reads its page, then looks for anything newer from the same publisher. A page that repeats someone else's figure is never the first publisher, however well known it is.
4. **Verify.** The script loads every page cited and confirms each quote is on it, word for word.
5. **Re-check.** A separate checker gets the claims and the verdicts, never the sources, and is told each claim is wrong until a first publisher's page says otherwise. It re-checks every claim called supported, because a wrong "supported" looks finished.
6. **Hand-back.** The report and the marked draft.

Each claim gets one verdict:

- **supported**: the first publisher's page says what the draft says.
- **differs**: the first publisher's page says something else.
- **no-source**: no first publisher was found. The skill never says a source was made up. Not finding something is not proof it does not exist.
- **could-not-open**: a first publisher was found, but its page could not be read.

A claim can also carry one or more of ten problem types: second-hand, number-wrong, base-dropped, wrong-subject, strength-changed, source-mislabelled, misquoted, out-of-date, publisher-disagrees and page-gone. The [glossary](../../GLOSSARY.md#check-claims) says what each means.

Two kinds of claim are listed and not traced, and go to you to confirm: anything about your own company or product, and anything about a named private person. No public page settles those.

## Install

See the [install steps](../../README.md#install). Then run `/check-claims`, or ask Claude something like "check the facts in this draft before I publish it".

**In Claude Code**, the full version: up to 40 claims a run, a researcher subagent per batch of 10 and a separate checker per batch, all in parallel. A longer draft is run in parts, and the skill says which sentences each part covered.

**In a Claude.ai or Claude Desktop chat**, turn on web search and **Create and edit files**, and use a normal chat, not an incognito one: the skill opens its own files, and the quote check is a script. A chat that can run subagents runs the same full version as Claude Code. A chat that can't takes up to 15 claims and traces them in the chat. For the re-check it builds one block for you to paste into a fresh chat, because a chat that already believes its research would look in the same place. If you skip that, the report says at the top that no verdict was re-checked.

It uses no API keys, no paid tools, no logins and no connectors: only the assistant's own web search and page reading.

## Tested

**The check set passed on 25 November 2026**, in Claude Code, on the subagent route. It is a made-up article and a made-up sales email whose claims point at real public pages, with one or more of every problem type planted, and an answer key I wrote by hand from the first publishers' pages before any run.

| Run | Draft | Result | Planted problems caught | Clean claims marked wrong | Tokens | Time |
|---|---|---|---|---|---|---|
| 2 | article, 25 claims | passed | 15 of 15 | 0 | 877,973 | 10 min 23 s |
| 2 | email, 5 claims traced | passed | 1 of 1 | 0 | 352,278 | 6 min 48 s |
| 1 | email, 6 claims traced | passed | 1 of 1 | 0 | 346,597 | 8 min 41 s |
| 1 | article, 27 claims | failed | 14 of 15 | 0 | 952,931 | 11 min 59 s |

- **Run 1 of the article failed on two rows of my answer key, and both faults were the key's, not the skill's.** I had planted one claim as sitting behind a sign-up form. The publisher also hosts that report as an open file, and the skill found it and read it. And a sentence I had written as current was stale, which the checker caught. I replaced the first claim with one in a report sold to clients only, dated the second, and ran both drafts again.
- **In the run that passed,** both out-of-date claims got the right verdict (the one stated as a past finding stayed supported, the one stated as the present position differed), the story was split into four claims with its made-up part marked as having no source, and the closed report came back as a page to open yourself.
- **The checker earned its place.** In run 1 it overturned a claim the first pass had called supported, because the government had put a bill before Parliament since the page was written. In the email it found a sale announced six days earlier.
- **The script's page loading ran live for the first time.** In the check set it found 105 of 111 quotes on their pages. Five were in PDFs, which it does not read, and one site refused it. In the example run above it found 26 of 42: two sites, 6sense and the SEC, refused its page loader, though the researchers could read them. Those quotes are marked in the report as not confirmed by code. One exact quote came back "not found" because the page splits a figure from its percent sign. That was a fault in the script, now fixed, with a test.
- **The script has 95 tests**, with no network, covering the sentence numbering, the file formats, every rule a record must meet, the quote check, what goes to the checker, and the report.
- **Run 1 also changed one instruction.** The reader was splitting a fact from its own date or amount, so "rose to £12.71 an hour in April 2026" became two claims. It now keeps them together.

What has not been run:

- **A real sign-up form.** No run met one: the closed page in the set is a report sold to clients.
- **The chat route**, in a Claude.ai or Claude Desktop chat that cannot launch subagents, and the block it builds for a fresh chat.
- **A draft over the cap of 40 claims**, run in parts.
- **Any model but one.** Every subagent in these runs was the same model.
- **The comparison with audit-content** under Related.

The runs, the key and the full account are in [`tests/check-claims/check-set/`](../../tests/check-claims/check-set/README.md).

## Read it with care

- **Your claims go out as web searches.** Checking a claim means searching for it, so the facts in an unpublished draft are sent to web search, and the script loads each page cited. The skill says so before it starts. Nothing else leaves the assistant you already use, and its files stay in your folder. Do not use it on a draft under embargo.
- **Expect some pages to stay closed.** In my test, with one writer on one day and web search off, the tools could not read the pages behind 14 of 58 claims. They sat with the publishers B2B writing quotes most, behind bot checks and sign-up forms. I tried every one of those pages in a browser and was still turned away from the pages behind 8. The skill does not go round a page that refuses it. It tells you the address and what to look for, so each is one visit.
- **A claim it could not open is unknown, not wrong.** The same goes for a claim with no source found.
- **Facts go stale.** The report is dated. A figure that is current today can be replaced next month.
- **The researchers and the checker are AI too.** The script confirms every quote is real and on the page cited. Whether a claim is still true as you worded it is a judgement, written down with its reason and evidence so you can disagree.
- **Comparisons are not checked.** Each claim gets its own verdict. Whether two supported figures can fairly be set side by side is yours to judge, and the report says so.
- **English drafts only.** No images, charts, tables or PDFs.

## Where it came from

My own test on 25 November 2026. Claude, with web search switched off for the test, was given six prompts a marketer or seller might type: four B2B articles and two sales emails. Separate researchers and checkers, and then I with a browser, traced 58 claims from the six drafts to their first publishers.

| What was found | Claims |
|---|---|
| Supported, with nothing against it | 25 |
| Supported, with a problem type (stale, or who it counts changed) | 10 |
| Supported, with an error that fitted none of the problem types as they then stood | 5 |
| Differs from the first publisher | 6 |
| No findable first publisher | 4 |
| On a page nobody could open | 8 |

- **No figure that could be read was misstated.** The first publisher's page could be read for 46 of the 58 claims, and none of those misstated a figure.
- **The common fault was age.** 10 claims were out of date. In 7 of them the publisher had since given a different figure, such as a 74% the government has replaced with 69%.
- **The other fault was credit.** 3 claims credited one vendor's case study to its rival.
- **Nothing was linked.** No draft gave a web address for any claim. Four of the six drafts told the user to check the figures, which the writer had not been able to do.

This is one writer, on one day, with no web search. It does not show that AI drafts are full of wrong numbers. With this writer they were not. It shows something narrower: 25 of the 58 claims were clean, and a careful reader could not tell those 25 from the other 33 without doing this work. The prompts, the drafts and every record are in [`tests/check-claims/problem-test/`](../../tests/check-claims/problem-test/), so anyone can run the same prompts on another assistant.

## Related

[audit-content](https://github.com/onvoyage-ai/gtm-engineer-skills) checks a draft's claims against the pages the draft cites, and searches for statistics that cite nothing, in one pass by one auditor. This skill traces every claim past any page that repeats it to the first publisher, has a separate checker re-check the result, and confirms every quote by code. I have read audit-content's instructions and not run it, so that comparison is still owed a test.

Its siblings here check other work before you rely on it: [check-call-summary](../check-call-summary/) for an AI summary of a call, and [check-account-list](../check-account-list/) for a target account list.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [More skills](../../README.md)
