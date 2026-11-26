# check-claims: spec

The agreed design for `check-claims`, settled on 25 November 2026 and revised the same day from the [test of the problem](../../tests/check-claims/problem-test/README.md) ([ADR 0020](../adr/0020-check-claims-promises-current-traceable-facts.md)), and again for the order of the report ([ADR 0021](../adr/0021-the-report-opens-with-what-to-do.md)). The skill is built, and its [check set](../../tests/check-claims/check-set/README.md) passed on 25 November 2026, on the subagent route in Claude Code. The [README example](../examples/check-claims/README.md) ran the same day, on a draft from the test of the problem, which has a prompt and no conversation to link to. Still owed: a run on the chat route, and a run of the one published skill that does similar work. Reviews check the skill against this file. Change it only on a new decision, and say why in a decision record.

## What it does

Traces every factual claim in a draft to whoever first published it, and says whether the fact is still current and credited to the right publisher, before the draft is published or sent.

1. **Number.** A script numbers every sentence of the draft, so every finding cites a sentence you can read.
2. **Claims.** A reader lists every factual claim, one fact each, and marks every other sentence as holding none.
3. **Trace.** A researcher finds the first publisher of each claim and records what its page says now, with evidence.
4. **Verify.** The script loads every page cited and confirms each quote is on it, word for word.
5. **Re-check.** A separate checker, which never sees the researcher's sources, tries to prove each claim wrong.
6. **Hand-back.** A report, and the draft marked up with a verdict on every claim.

It checks a draft. It never writes one, never rewrites the prose, and never publishes or sends anything.

## Why it exists

AI makes drafts fast, and the facts in them come from the model's memory. A figure can be real and still be two editions old, linked to nothing, or credited to the wrong company. Nobody reading the draft can tell which facts those are without tracing each one, and that is the work this skill does.

The worry about AI and facts is public. Three cases, each read at its own source on 25 November 2026:

- The Content Marketing Institute's [B2B research](https://contentmarketinginstitute.com/articles/b2b-content-marketing-trends-research) (4 November 2026) reports that 54% of marketers named ensuring accuracy as a hurdle with AI. The article does not say whether that is 54% of all 861 marketers surveyed or of those using AI, which is the kind of gap this skill reports.
- [Fortune](https://fortune.com/2025/10/07/deloitte-ai-australia-government-report-hallucinations-technology-290000-refund/) (7 October 2025) reported that Deloitte Australia "will refund its last payment installment" on a $290,000 government report found to contain fabricated references.
- The [DeepTRACE paper](https://arxiv.org/abs/2509.04499) (2 September 2025), by authors at Salesforce AI Research and Microsoft Research, measured citation accuracy of 40 to 80% across AI research tools. Its questions were general, not about sales or marketing.

None of these measures a marketing draft, so this skill's own test did. On 25 November 2026 Claude, with web search switched off for the test, was given six prompts a marketer or seller might type: four B2B articles and two sales emails. Separate checkers, and then a person with a browser, traced 58 claims from the six drafts to their first publishers. 40 were supported, 9 of them out of date. 6 differed, 4 had no findable first publisher, and 8 sat on pages nobody could open. Of the 46 claims whose first publisher could be read, none misstated a figure. The faults were age and credit: in 7 claims the publisher had since given a different figure, such as a 74% the government has replaced with 69%, and 3 claims credited one vendor's case study to its rival. No draft gave a web address for anything. Four of the six drafts told the user to check the figures, which the writer had not been able to do. The test is at [tests/check-claims/problem-test](../../tests/check-claims/problem-test/README.md).

So the test does not support a claim that AI drafts are full of wrong numbers. With this writer they were not. It supports a narrower one: 25 of the 58 claims were clean, and a careful reader could not tell those 25 from the other 33 without doing this work.

That is one writer, on one day, with no web search. The skill's README says so wherever it quotes the test. A draft written by another assistant, or with search on, may carry different faults, such as crediting a page that repeats a figure. The problem types cover those, and the check set plants them.

One published skill, [audit-content](https://github.com/onvoyage-ai/gtm-engineer-skills) (read 25 November 2026), already checks a draft's claims against the pages the draft cites, and searches for statistics that cite nothing, in one pass by one auditor. This skill differs in three ways: every claim is traced past any page that repeats it to the first publisher, a separate checker re-checks the result, and code confirms every quote. Its instructions have been read, not run, so this comparison is owed a test.

## Who it's for

Anyone about to publish or send something that states facts: content and product marketers, people writing sales emails and decks, founders. What they get is, for every fact in the draft:

- **Where it comes from.** The first publisher and its page, or a plain statement that none could be found.
- **Whether it is still current.** The date it was published, and any newer figure the same publisher has given since.
- **Whether the credit is right.** A right figure pinned on the wrong publisher is reported as firmly as a wrong figure.

A wrong figure is caught too, but the skill does not promise the user will find many. The README frames it around an AI-written article. Nothing in the skill assumes how the draft was written.

## What it takes in

- **A draft.** Pasted text, or a `.txt`, `.md` or `.docx` file: an article, a report, the text of a deck, a sales email. PDF is refused with a way round it (another format, or a paste), as in check-call-summary.
- **Up to 40 claims a run** on the subagent route and 15 on the chat route. A longer draft is run in parts, and the skill says which sentences each part covered.

English drafts only. Other languages are not tested, so not claimed.

## Stage 1: Number

`scripts/claims.py number` writes `draft-lines.md`: one numbered sentence per line, `[S12] text`. Headings and list items are numbered as sentences. It prints the sentence count, which the skill shows the user so a wrongly read file is caught at once.

## Stage 2: Claims

The reader gets the numbered draft and writes `claims.md`. Every sentence either carries one or more claims or is marked `no claim` (opinion, advice, a question, a call to action). A claim is one checkable fact, with the sentence it comes from and the source the draft gives for it, if any. A fact keeps its own date, amount and length of time: "rose to £12.71 an hour in April 2026" is one claim, not two.

**A story is split into its parts.** Each part that could be true while another is false is its own claim: who did it, what they did, each colourful detail, and what came of it. "GumGum made a Batman comic starring the chief executive and won the account" is four claims: that it made a comic, that the comic starred the chief executive, that it was Batman-themed, and that it won the account. In the test of the problem a story listed as two claims forced one verdict onto a claim that was half supported. Splitting raises the count against the cap, and the reader says how many claims each story became.

| Kind | What it covers |
|---|---|
| statistic | Any figure presented as measured: a percentage, a count, a sum of money, a ranking |
| quotation | Words credited to a named person or organisation |
| company-fact | Something stated about a named company other than the user's own: what it sells, charges, owns, announced or did |
| event | A dated thing that happened: a launch, a ruling, a takeover, a publication |
| citation | A named study, report, paper or article said to exist and to say something |

Two kinds of claim are listed but never traced, and go on the confirm list instead:

- **About the user's own company or product.** No public page settles what the user's product does or what their customers achieved.
- **About a named private person**, beyond words they published themselves. Public pages on a person are thin and often behind a login.

## Stage 3: Trace

A fresh researcher per batch of 10 claims. For each claim it finds the **first publisher**: the organisation or person that produced the figure or made the statement, on their own page or in their own document. A page that repeats someone else's figure is never the first publisher, however well known it is. A news outlet is the first publisher of its own reporting and of nothing it relays.

The researcher starts from the source the draft gives, when it gives one, and follows it back. Once it has the first publisher's page, it looks for anything newer from the same publisher on the same thing: a later edition, a later announcement, a changed name or owner. It writes one record per claim: the verdict, any problem types, the first publisher, the date it published, and evidence (the web address and the exact words).

### Verdicts

Exactly one per claim:

- **supported**: the first publisher's page says what the draft says. The record carries the evidence.
- **differs**: the first publisher's page says something else. The record carries the evidence and at least one problem type.
- **no-source**: no first publisher was found. The record lists the searches tried. The skill never says a source was made up: not finding something is not proof it does not exist.
- **could-not-open**: a first publisher was found, but its page could not be read (a paywall, a sign-up form, a refusal, a file the tools cannot read, a page that has gone). The record says what stood in the way.

**Expect could-not-open to be large.** In the test of the problem the tools alone left 14 of 58 claims unread, 24%. After a person tried every one of those pages in a browser, 8 were still unread, 14%. They sat with the publishers B2B writing quotes most. A could-not-open claim is unknown, not wrong, and the skill never guesses its verdict. What it hands a person for each one is set out in stage 6.

### Problem types

Counted by type. A claim carries none, one or several. Drawn from errors found while checking the research behind this skill, and changed after the test of the problem ([ADR 0020](../adr/0020-check-claims-promises-current-traceable-facts.md)). There are ten:

- **second-hand**: the draft credits a page that repeats the claim, not the first publisher.
- **number-wrong**: the figure is not the one the first publisher gives.
- **base-dropped**: the figure is right but who it counts has gone or changed. "45% of leaders with agents in use" becomes "45% of leaders".
- **wrong-subject**: the figure or fact is about a different group or thing from the one the draft applies it to, or is true of one of several subjects the draft pins it on. A threshold that is Google's rule becomes "Google and Yahoo's".
- **strength-changed**: the strength of the claim has changed: a plan, a hedge, a range or a single case made firm, or a qualifier dropped. It works both ways. "Will refund" becomes "refunded", which overstates. "Significantly more than 3,000" becomes "3,000", which understates. A best band of 2 to 4 becomes "fewer is better".
- **source-mislabelled**: the source is described wrongly. Either who published it (a vendor's own survey called independent, the wrong name, the wrong year or edition, one vendor's case study credited to its rival) or how the study was done (the data it rests on, the sample, the method). "7.1 million sales opportunities" becomes "millions of recorded calls".
- **misquoted**: the quoted words are not the words on the page.
- **out-of-date**: the first publisher has since published a newer figure, or the fact has since changed. The record carries the newer figure or fact, its date and its evidence.
- **publisher-disagrees**: the first publisher gives two figures for the same thing over the same period. The record carries both quotes.
- **page-gone**: a page the claim rests on is no longer there. Either the web address the draft gives does not load or loads a page that does not hold the claim, or the first publisher's own page has gone or been replaced by an edition without the figure. The record says which address, and what loads there now.

Inventing a problem to look thorough is the same failure as missing one.

### Which verdict a problem type sits on

- **Out-of-date follows how the draft states the fact.** When the draft dates the figure or states it as a past finding ("the 2025 survey found 74%"), the claim is supported and carries out-of-date. When the draft states it as the present position ("is now part of"), the claim differs and carries out-of-date.
- **Four types are about the source, not the draft's words**, and can sit on a supported claim: second-hand, out-of-date under the rule above, publisher-disagrees and page-gone.
- **The other six say the draft departs from the page**: number-wrong, base-dropped, wrong-subject, strength-changed, source-mislabelled and misquoted. A claim carrying one of them differs, unless the claim is still true as the draft words it, in which case it stays supported and the record says why.
- **Page-gone is the only type a claim can carry without a page that was read.** A could-not-open or no-source claim carries page-gone or nothing. Every other type needs the first publisher's words.

### Telling neighbouring types apart

- **Number-wrong or strength-changed.** A different figure is number-wrong. The same figure with its hedge, range or qualifier changed is strength-changed.
- **Base-dropped or wrong-subject.** The publisher's own group with its limits lost is base-dropped. A different group or thing altogether, or one subject stretched over several, is wrong-subject.
- **Base-dropped or source-mislabelled.** Who the figure counts is base-dropped. A wrong account of how the study was done, where the draft gives one, is source-mislabelled.
- **Second-hand or source-mislabelled.** Crediting a page that repeats the first publisher is second-hand. Crediting someone who never published it is source-mislabelled.
- **Out-of-date or publisher-disagrees.** A newer edition or a later announcement is out-of-date. Two figures for the same period, both still standing, is publisher-disagrees.
- **Out-of-date or page-gone.** A newer figure that was read is out-of-date. A page that is missing, with nothing newer read, is page-gone.

## Stage 4: Verify

`scripts/claims.py verify` checks every record's shape and loads every cited page once, recording each quote as verified, not-on-page, pdf or could-not-load (case, spacing, quote marks and punctuation are ignored, nothing else). It waits 2 seconds between requests to the same site and loads pages with a normal browser identity. It fails on:

- a sentence with neither a claim nor a `no claim` mark, and a claim with no record;
- a `differs` with no problem type, a `supported` with no evidence, and a `no-source` with no searches listed;
- a problem type that is not one of the ten;
- an `out-of-date` with no quote for the newer figure or fact;
- a `publisher-disagrees` with fewer than two quotes;
- a `page-gone` that does not name the address that has gone;
- a `supported` carrying number-wrong, base-dropped, wrong-subject, strength-changed, source-mislabelled or misquoted with no reason given for why it is still supported;
- a `could-not-open` or `no-source` carrying any type other than page-gone, and a `could-not-open` that does not say what stood in the way.

It also fails on a record the report in stage 6 could not be written from:

- a claim whose draft words are not in the sentence it cites;
- a record with no one-line finding;
- a `supported`, `differs` or `could-not-open` that names no first publisher, and a `supported` or `differs` with no date published (the date, or "not shown");
- a `differs` with no evidence, or with no words to use instead;
- a `could-not-open` with no web address to open, or nothing to look for.

A quote the script does not find on its page does not fail the run. It is recorded as not-on-page and the claim goes to the checker.

## Stage 5: Re-check

The checker re-checks every **supported** claim and every claim whose evidence the script could not confirm. A `differs` whose every quote the script found on its page goes straight to the report. A wrong "supported" is the costly error, because it looks finished.

The checker gets the claims and the verdicts, never the first publisher the researcher named, its evidence or its reasons. It finds its own, and looks for anything newer from the same publisher, as the researcher did. It is told each claim is wrong until a first publisher's page says otherwise. Its record replaces the first pass's in the report, which says what it changed.

## Stage 6: Hand-back

`scripts/claims.py report` builds `check.md`. It opens with what the user has to do, least work first, so a draft that needs one fix does not read as a draft pulled apart ([ADR 0021](../adr/0021-the-report-opens-with-what-to-do.md)). In this order:

1. One line saying how many claims need nothing from the user, then a count for each kind of work below.
2. **Fix these**: every `differs`, with the words to use instead, then what the first publisher says now.
3. **Update or re-credit these**: every `supported` claim that carries a problem type, with the newer figure or the right source.
4. **Your call**: every `no-source`, with the searches tried. The user cuts it, softens it or cites it themselves.
5. **Confirm with a person**: every claim about the user's own company, every claim about a named person, every `could-not-open`, and every `supported` claim whose quote the script looked for and did not find.
6. **Nothing to do**: every `supported` claim with nothing against it, with its first publisher and date.
7. **How this was checked**: counts by verdict and by problem type, how many claims the checker re-checked and changed, and one line saying comparisons between claims were not checked.

No verdict changes with the order, and nothing is left out. When no verdict was re-checked, the report still says so above everything else.

Each `could-not-open` on the confirm list is written so a person can settle it in one visit: the web address, the draft's exact words, what stood in the way, and what to look for on the page (the figure, who it counts, and the date). The skill does not try a second route round a page that refused it.

A `supported` claim goes on the confirm list when the script loaded the page, looked for every quote the claim rests on, and found none of them. It stays `supported` in the counts, and the list gives the web address and the quote to look for. A quote in a PDF, or on a page that would not load for the script, is different: the script could not look. That claim stays where it was, with the quote's state shown beside it.

Then the skill writes `marked.md`: the draft with a verdict beside every claim. For each `differs`, and each `supported` claim that carries a problem type, the corrected fact, the newer figure or the right source follows in bold with its link. The prose is otherwise untouched.

## Sources

The first publisher's own page or document is the only evidence. Search results, AI answers, listing sites and pages that repeat a figure help find it and never stand in for it. Only the assistant's built-in web search and page reading, plus `curl` in a shell: no third-party search, scraping or enrichment tools, and no API keys ([ADR 0004](../adr/0004-no-api-keys.md)).

## Where it runs

- **First, on every route**, the skill runs its script with no arguments. If the script does not run, the skill lists its own folder, stops and tells the user why. If it can run code and the folder holds no `scripts/`, the skill was saved without its files, for example from a chat's offer to save it, and the user removes it and uploads the zip from the latest release under Customize, then Skills. Otherwise this chat cannot open the skill's files or run its script, and the user needs a normal chat (not an incognito one) with Create and edit files on ([ADR 0017](../adr/0017-a-skill-stops-when-it-cannot-open-its-files.md)).
- **The route follows what the chat can do**, not the app ([ADR 0019](../adr/0019-the-route-follows-what-the-chat-can-do.md)).
- **The subagent route**: a fresh reader, a fresh researcher per batch in parallel, and a fresh checker per batch that sees only the stripped claims.
- **The chat route**: up to 15 claims. The reader and the research run in the chat. The check is handed to a fresh chat as one block to paste, because the checker has to go and find the source, and a chat that already believes the research would look in the same place ([ADR 0002](../adr/0002-the-checker-never-sees-the-research.md)). If the user declines, the report says at the top that no verdict was re-checked.
- **Other agents** are not tested and not claimed.

## Files

A folder `check-claims/<YYYY-MM-DD>-<short-name>/` in the working directory: `draft-lines.md`, `claims.md`, `check.md`, `marked.md`, the draft as given, `working/` for each researcher's and checker's file, and `check-in/` holding only the stripped claims a checker reads.

## Privacy

Checking a claim means searching for it, so the claims in an unpublished draft go out as web searches. The skill says so before it starts. Nothing else leaves the assistant it runs in, and its files stay in the user's folder.

## Not in v1

- Writing or rewriting drafts.
- Claims about the user's own company checked against their own files.
- **Comparisons between claims.** Each claim gets its own verdict. Whether two supported figures can fairly be set side by side, such as a reply rate counted against emails sent beside one counted against emails opened, is not checked, and the report says so.
- Images, charts and tables.
- PDF drafts.
- Reading a draft from a CMS or a sequencer.
- Drafts in languages other than English.
- Archive copies of pages that have gone. A page that has gone is reported as page-gone and, when nothing else holds the claim, could-not-open. The skill does not go to a web archive for it.

## Tests

- **Script tests**, no network: sentence numbering for each format, the record format, the coverage check, the quote check, each shape rule in stage 4, what goes to the checker, and the report.
- **Check set.** A made-up article and a made-up sales email, whose claims point at real public pages. Unlike the drafts in the test of the problem, they give a web address for some claims and quote a named person, because three types cannot be planted without them. Planted, one or more of each:
  - second-hand, number-wrong, base-dropped, source-mislabelled, misquoted and publisher-disagrees;
  - wrong-subject, as a fact true of one named company pinned on two;
  - strength-changed twice, once overstated and once understated;
  - out-of-date twice, once stated as a past finding (supported) and once as the present position (differs);
  - page-gone twice, once on a link the draft gives and once on a first publisher's page that has gone;
  - a story to be split into its parts, one part supported and one not;
  - one claim with no findable source, one in a report that is closed to the skill (behind a sign-up form or sold to clients only), and clean claims.

  The answer key is written by hand from the first publishers' pages before any run, and re-confirmed before each release, because pages change. Pass: every planted problem caught with the right type, both out-of-date claims given the right verdict, the story split, and no clean claim marked `differs`.
- **README example.** A real AI-written article on a B2B subject, run live, with the conversation or the prompt that produced it linked.
- **The test of the problem.** Run on 25 November 2026 with Claude as the writer. No second writer is tested before the build. The six prompts are kept so anyone can run them on another assistant.

## Words to add to the glossary

**Draft** (the text being checked, as given), **numbered draft** (`draft-lines.md`), **claim** (one checkable fact from the draft), **first publisher** (as defined in stage 3), **evidence** (a first publisher's web address and the exact words copied from it), **verdict** (the four above), **problem type** (the ten above, with their names as given: second-hand, number-wrong, base-dropped, wrong-subject, strength-changed, source-mislabelled, misquoted, out-of-date, publisher-disagrees and page-gone), **confirm list**, **reader**, **researcher**, **checker**, **re-check**, **report** (`check.md`) and **marked draft** (`marked.md`).

## Settled

- **The promise is current, traceable, rightly credited facts.** Stefan's call on 25 November 2026, from the test of the problem. The skill does not claim AI drafts are full of wrong numbers ([ADR 0020](../adr/0020-check-claims-promises-current-traceable-facts.md)).
- **Ten problem types.** All nine first drafted are kept, four of them with wider meanings and two of those four under new names, and one is added (ADR 0020).
- **A small departure can stay supported.** Stefan's call on 25 November 2026. A claim carrying one of the six types that say the draft departs from the page differs, unless it is still true as the draft words it. Then it stays supported and the record says why. Without this, every dropped qualifier would be a differs.
- **The report opens with what to do, least work first.** Stefan's call on 25 November 2026, after reading a sample report. The verdicts and counts are unchanged and come last ([ADR 0021](../adr/0021-the-report-opens-with-what-to-do.md)).
- **The script also fails a record the report could not be written from.** Stefan's call on 25 November 2026, when the script was built. The six rules are listed in stage 4. Without them a `differs` could reach the user with no words to use instead.
- **A supported claim the script could not confirm goes on the confirm list.** Stefan's call on 25 November 2026. "Nothing to do" is the part of the report a user trusts without reading, so a claim whose quote the script looked for and did not find cannot sit there.
- **A draft over the cap is run in parts, in one run folder.** Made while the instructions were written, and confirmed by Stefan on 25 November 2026. The reader lists every claim once. Each part traces the next 40 claims in claim order (15 on the chat route), and its report lists the claims still waiting as not checked. The skill says which sentences each part covered and asks before starting the next. The script already allowed this, so it did not change.
- **A file the publisher hosts openly may be read, even when its report page asks for a form.** Stefan's call on 25 November 2026, after the check set's first run. A report planted there as sitting behind a sign-up form was also on the publisher's site as a file anyone can open, and the researcher and the checker each read it. It is the first publisher's own document at its own address, and no form was filled in, so it is not a second route. A copy on another site still is.
- **The reader keeps a fact with its own date and amount, the quote check closes a gap between a figure and its percent sign, and the check set's closed report may be behind a form or sold to clients only.** Three calls made while the check set ran, and confirmed by Stefan on 25 November 2026 when he approved the release.
- **A page gets two tries at one address, and no second route.** Made while the instructions were written, and confirmed by Stefan on 25 November 2026. The sources section allows `curl`, and stage 6 says the skill tries no second route round a page that refused it. So: the built-in reader, then `curl` once at the same address, is one route by two tools. A web archive, a cached copy, another site's copy, a sign-up or a bot check is a second route, and is never taken.
- **The privacy line is said, and the skill does not wait for a yes.** Made while the instructions were written, and confirmed by Stefan on 25 November 2026. The skill says in its first message that the draft's facts go out as web searches and that a user with a draft under embargo should say so now. It then carries on, and stops if the user objects. Numbering and listing the claims search nothing, so the user has that long to object.
- **What the marked draft looks like.** Made while the instructions were written, and confirmed by Stefan on 25 November 2026. A mark in square brackets follows each claim's draft words: the claim number, the verdict and any problem types. For a `differs`, and a `supported` with a problem type, the record's Use instead line follows in bold, then a link to the newer page where there is one, otherwise to the first publisher's page. The draft's own words are never struck through. A claim that was not traced is marked as not traced, with why. A supported claim on the confirm list is marked "confirm the quote".
- **No second writer is tested before the build.** Stefan's call on 25 November 2026. The test of the problem has one writer, Claude with web search off, and the spec and README say so.
- **The blocked pages in the test stay unread.** Stefan tried every one by hand on 25 November 2026. 8 claims stay could-not-open.
- **Sales email is in v1.** Stefan's call on 25 November 2026. The evidence that teams want outbound checked is thin (one Reddit thread title and vendor stories), but the method is the same and no skill was found doing it. The README leads with the article.
- **Claims about the user's own company go on the confirm list.** Checking them against a file the user supplies is a second skill's worth of work.
- **Claims about a named person go on the confirm list.** No public page settles them without a login.
- **The cap is 40 claims on the subagent route.** It began as check-account-list's cost of one careful check per company. The test of the problem then measured it: 58 first-pass checks and 38 re-checks took 70 web searches, because researchers went straight to a named publisher's site, so 40 claims a run is within reach. The four articles in that test, briefed at 600 to 800 words, held 9 to 17 claims each, before any story was split. A draft that names no publishers may cost more. The check set measured it again on 25 November 2026: its article, 25 claims and 13 re-checks, took 877,973 tokens and 10 minutes 23 seconds, so 40 claims fit in one run. It did not count searches, and it held too few claims to run in parts.
- **Formats are paste, `.txt`, `.md` and `.docx`.** Decks and PDFs wait until they are tested.
- **The name is `check-claims`**, to sit beside check-call-summary and check-account-list.

## Calls made while the script was built

Technical calls made on 25 November 2026, one line each. The skill's `references/record-format.md` and `references/reader.md` fix how each file is written.

- **Three commands:** `number`, `verify` and `report`. With no arguments the script prints how to use it and exits 2. Exit codes follow the sibling skills: 0 for ok, 1 for a problem found or a file that cannot be read, 2 for a command it does not know.
- **`verify` has three forms.** With `--claims` it checks the reader's file before any research. With record files named it checks those files only. With none named it checks the whole run, and every traced claim needs a record.
- **The record format** follows check-account-list's: a `##` heading, `- Label: value` lines, and evidence lines split by `|`.
- **An evidence line is marked `page` or `newer`.** It was not called `claim`, so the glossary word keeps one meaning.
- **A quote not found on its page does not fail `verify`.** Stage 4's list leaves it out and stage 5 sends the claim to the checker. `verify` prints the line and exits 0.
- **A space between a figure and its percent sign is spacing.** Some pages hold the two in separate tags, so their text reads "86 %". The quote check closes that gap on the quote and on the page. Found in the check set's second run, when a researcher's exact quote came back not found.
- **Each page is loaded once.** check-account-list loads a page a second time when a quote is missing. This script does not, because stage 4 says once.
- **A page that failed to load is tried again by the next `verify`**, never twice in one.
- **`report` writes the stripped claims**, not a command of its own, so there are three commands as the stages name. It is run once before the re-check and once after.
- **The checker is not told the problem types.** Stage 5 says it gets the claims and the verdicts. A type such as out-of-date would tell it what to find.
- **In each entry of the report the words to use come before what was found.**
- **The report says at the top that no verdict was re-checked** whenever claims were sent to the checker and no checker's record exists. No flag turns it on, so it cannot be forgotten.
- **A claim sent to the checker with no record back** is named in the counts and shown with its first pass.
- **A heading is one sentence**, however many question marks it holds. A list item keeps its marker and is split like a paragraph. A table row is one sentence.
- **Lines with no blank line between them are one paragraph**, as in Markdown, so hard-wrapped text is not cut mid-sentence. A sign-off on three lines becomes one sentence.
- **The numbered draft keeps Markdown marks** such as `#` and `**`, so the text is exactly as given.
- **A sentence that starts with a lower-case letter is joined to the one before.** A missed split costs nothing: the sentence is still covered.
- **Only `.docx` is read as a Word file.** A slide deck or a spreadsheet is refused, not read as Word.
- **Quote marks are written straight.** The quote check treats curly and straight marks as the same, and the repo bans curly ones.
- **The caps are said, not enforced.** Over 15 traced claims, or over 40, `verify --claims` says so and still passes, because the skill decides how to run a draft in parts.
- **The script does not write `marked.md`.** The skill does, by the rules in `references/hand-back.md`.
- **The script waited in a holding folder** under `tests/` until the skill had its `SKILL.md`, so the repo check was not weakened. It moved to `skills/check-claims/scripts/` on 25 November 2026.
