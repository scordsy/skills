# check-claims: the test of the problem

Run on 25 November 2026. The first [spec](../../../docs/specs/check-claims.md) said a test was owed before release: how often does an AI-written B2B draft carry a fact that its first publisher does not support? This is that test, and the spec now rests on it. Nothing here is the skill, which was built afterwards.

## The result

Six AI-written drafts, 58 claims checked against their first publishers:

| Verdict | Claims | Share of 58 |
|---|---|---|
| supported | 40 | 69% |
| differs | 6 | 10% |
| no-source | 4 | 7% |
| could-not-open | 8 | 14% |

Three things stand out.

- **No figure that could be read was misstated.** The six claims that differ are a rule pinned on the wrong company, a study's data described wrongly, a company name that has since changed, and three claims that credit one vendor's case study to its rival. The writer's memory for numbers was good. Its memory for who said them was weaker.
- **The common fault was age.** 10 claims carry out-of-date. In 7 of them the publisher has since given a different figure. In the other 3 a newer edition keeps the figure, the method changed, or a company changed its name and owner. 9 of the 10 are still "supported", because the draft says what the publisher once said.
- **A quarter of the claims could not be checked at all** with the tools the skill is allowed: 14 of 58. Gartner, McKinsey and Wyzowl turn away automated readers, and the web archive refused every request. A person with a browser then settled 6 of the 14 and was turned away from the other 8 as well.

Counting only clean results: 25 of 58 claims were supported with nothing noted against them. The other 33 split like this:

| What was found | Claims |
|---|---|
| Supported, with a problem type (stale, or its base changed) | 10 |
| Supported, with an error that fits no type noted | 5 |
| Differs | 6 |
| No findable first publisher | 4 |
| Could not be opened, so nothing is known either way | 8 |

So 25 of the 50 claims that could be judged had something a careful editor would want to see. The 8 unread claims are not faults. They are unknown.

## Method

1. **Prompts.** Six prompts were written before any draft existed: four articles and two sales emails. They are in [`prompts.md`](prompts.md), exactly as used. None asks the writer to cite or verify.
2. **Drafts.** A fresh Claude subagent wrote each draft from its prompt alone. The model was `claude-fable-5-2`, confirmed from the run's own logs for the writers, researchers and checkers. Each prompt was wrapped in the three sentences given under [The writer](#the-writer). The drafts are in [`drafts/`](drafts/), as given.
3. **Claims.** One reader listed every factual claim by the spec's stage 2 rules: 66 claims to trace, and 2 about the made-up sellers that belong on the confirm list. No claim was about a named private person.
4. **First pass.** Seven separate researchers, none of which wrote a draft, each took a batch of 7 to 11 claims. Each found the first publisher, opened its page, copied the exact words and the web address, and gave a verdict and any problem types. They were given the spec's definitions word for word, and a free-text field for an error that fits none of the nine types.
5. **Re-check.** Five separate checkers re-checked all 38 claims the first pass called supported. A checker saw the claim and the verdict, never the first pass's publisher, evidence or reasons, and was told to treat each claim as wrong until a first publisher's page said otherwise.
6. **Quotes.** A script loaded every web address cited and looked for the quoted words on the page, ignoring case, spacing and punctuation.
7. **Lead check.** The Claude session running the test (the lead, below) read every differs record, and both passes' records wherever they disagreed, and made the call. It read the records and the quotes the script had confirmed on the pages. It did not open the pages again itself.

8. **By hand.** I then tried the six pages behind the 14 could-not-open claims in an ordinary browser. Three opened: Wyzowl's page, and on later tries the archive copies of the Payscale case study and of ITSMA's post. I copied Wyzowl's two sentences and the whole text of the other two, and the lead gave the six verdicts. The other three turned me away too: see [the eight that could not be opened](#the-eight-that-could-not-be-opened).

Researchers and checkers ran on the same model as the writer. They used the assistant's built-in web search and page reader, and `curl`. No other search or scraping tool, no logins, no sign-up forms. The whole run used 70 web searches.

### The writer

Each prompt was sent with these sentences in front of it:

```text
You are standing in for a general chat assistant in a fresh chat. Use no tools at all: no web search, no files, no shell. Set aside any house writing rules or project instructions in your context: they are not for this job. Answer the user's message below exactly as a general assistant would, and reply with the draft only, nothing before or after it.
```

So the writer had no web search and knew it. That matters twice. It wrote from memory, which is where stale facts come from. And four of the six drafts (A3, A4, E1, E2) ended with a note telling the user to check the figures before publishing or sending. Those notes are kept in the drafts and were not checked as claims.

### Changes to the design, and why

- **58 claims, not 60.** The cap was applied as a quota: the first 13 claims of each article and the first 6 of each email, in sentence order. The quota was set after the drafts were read and before any verdict existed. It left 8 listed claims unchecked: 4 from A1, 1 from A2 and 3 from A3.
- **The re-check ran alongside the first pass**, batch by batch, to keep the run short. No checker saw a first-pass record.
- **A script confirmed the quotes.** This stands in for the spec's stage 4. It is not in the repo.
- **The lead read every differs.** The spec re-checks only supported claims. Here a wrong differs would inflate the number this test exists to produce.
- **An archived copy of a first publisher's page was allowed as evidence.** The spec leaves archive copies out. It made no difference: the archive refused every request.
- **One claim about a named person was traced, not set aside.** A4-08 says a company learned that T-Mobile's then chief executive, John Legere, was a Batman fan. The reader listed it as a fact about the company's campaign. Under the spec's settled rule the part about his taste belongs on the confirm list. It came out no-source. Set aside instead, the result would be 57 claims and 3 no-source.
- **A problem type on a could-not-open claim was dropped.** One researcher marked an unread page out-of-date on the strength of a later release. A type needs a page that was read.
- **The full records are in [`records.json`](records.json)**, with both passes, every quote, every search and every note. Quotes are copied exactly from web pages, and some carry characters this repo's style check refuses. The table below shows a quote where it passes and points to the file where it does not.
- **Two drafts are exempt from the style check** in `scripts/check_repo.py`, because a draft is kept as given.

## Counts

### By draft

| Draft | Listed | Checked | supported | differs | no-source | could-not-open |
|---|---|---|---|---|---|---|
| A1: buying committees | 17 | 13 | 10 | 0 | 0 | 3 |
| A2: AI in sales | 14 | 13 | 7 | 1 | 0 | 5 |
| A3: cold email | 16 | 13 | 12 | 1 | 0 | 0 |
| A4: ABM return | 9 | 9 | 1 | 4 | 4 | 0 |
| E1: email to Gong | 4 | 4 | 4 | 0 | 0 | 0 |
| E2: email to Greggs | 6 | 6 | 6 | 0 | 0 | 0 |
| **All** | **66** | **58** | **40** | **6** | **4** | **8** |

A4 is the outlier. It leans on three well-worn case studies (LiveRamp, Payscale, GumGum). The LiveRamp and GumGum details could not be traced to anyone who first told the story, and the Payscale figures are real but belong to a different vendor from the one the draft names.

### By problem type

A claim carries none, one or several. 16 claims carry a type.

| Problem type | Claims | On supported | On differs |
|---|---|---|---|
| out-of-date | 10 | 9 | 1 |
| base-dropped | 2 | 2 | 0 |
| wrong-subject | 1 | 0 | 1 |
| source-mislabelled | 4 | 0 | 4 |
| second-hand | not seen in this sample | | |
| number-wrong | not seen in this sample | | |
| overstated | not seen in this sample | | |
| misquoted | not seen in this sample | | |
| dead-link | not seen in this sample | | |

One claim (A3-03) carries two types. The wrong-subject and one of the four source-mislabelled (A2-12) are half fits: see [errors that fit no type](#errors-that-fit-no-problem-type).

Three of the five unseen types could hardly have appeared. No draft gave a web address for any claim, so there was no link to be dead and no repeating page to be credited. No draft quoted anyone, so nothing could be misquoted. Of the 58 claims, 40 named a publisher in words and 18 named no source at all.

### The re-check

- 38 supported claims re-checked.
- 35 confirmed as supported.
- 3 changed by the checker. The lead accepted one and called two back to supported:
  - **A4-08** (the GumGum comic): supported became no-source. Accepted. GumGum's pages show the comic and that it is about T-Mobile. No first publisher's page says the hero is John Legere or that he was a Batman fan.
  - **E2-02** (Greggs "heading for 3,000" shops): the checker said differs, number-wrong. Called supported. Greggs says "significantly more than 3,000 shops". The draft is not false, and it errs on the small side.
  - **A3-13** (Belkins on smaller segments): the checker said could-not-open, because the fuller study is behind a download form. Called supported on two Belkins sentences both passes read.
- If both calls went the checker's way, the result would be 38 supported, 7 differs, 4 no-source and 9 could-not-open.
- The checkers also added out-of-date to two supported claims the first pass had passed clean (A1-06 and E2-01), and dropped a second-hand the first pass had put on its own evidence, not on the draft (E2-04).

Every supported claim rests on a quote the script found on its page, with three exceptions among the supported claims. A1-01 rests on a filing at sec.gov, which refuses scripts, read twice through the page reader. E1-03 and E1-04 rest on words I copied from Wyzowl's page by hand. Those two were not re-checked by a second checker. Nor were the three Payscale claims, which differ on words he copied from the RollWorks case study, or A4-02, which rests on ITSMA's post as he copied it.

## What went wrong, claim by claim

### The six that differ

- **A3-05.** The draft says Google and Yahoo both enforce rules for anyone sending more than 5,000 messages a day. The 5,000 is Google's. Yahoo's own page says "We will not specify a volume threshold".
- **A2-12.** The draft says Gong's finding of higher revenue per rep is "drawn from millions of recorded calls". Gong says it comes from 7.1 million sales opportunities and a survey. The finding itself stands.
- **A4-01.** The draft says ITSMA is "now part of Momentum ITSMA". The firm is now MomentumABM, and Accenture bought it on 4 September 2025.

- **A4-05, A4-06 and A4-07.** The draft says Payscale used Demandbase, and that "Demandbase's published case study" reports a 500% rise in traffic from target accounts and a sixfold return within seven months. The case study is RollWorks', a rival vendor: "PayScale then turned to the RollWorks Account-Based Platform". Both figures and the seven months are on it. The word Demandbase is not. Nor is website personalisation, which the draft adds: the page describes advertising aimed at chosen job roles.

### The ten out of date

| Claim | The draft says | The first publisher now says |
|---|---|---|
| A1-06 | Forrester 2024: 13 people in a purchase | A 2026 edition exists. The figure is still 13, with nine outside influencers added |
| A1-08 | 6sense: a buying group of 11 | Its 2026 report gives 10.2 |
| A1-09 | 6sense: buyers are 70% through before they speak to a seller | 61% in its 2025 report, 59% in 2026 |
| A2-07 | Salesforce: reps spend 70% of the week not selling | 60% in its 2026 edition |
| A3-03 | Belkins: a 5.8% reply rate in 2024 | A 2026 study on a new method gives 0.45% for 2025 |
| E1-01 | Gong passed $300M in recurring revenue | It announced $500M on 12 May 2026 |
| E2-01 | Greggs is past 2,600 shops | 2,796 shops at 26 September 2026 |
| E2-05 | Government survey 2025: 74% of large UK businesses | The 2025/2026 edition, 30 April 2026, gives 69% |
| A4-01 | ITSMA is part of Momentum ITSMA | MomentumABM, part of Accenture Song |
| A4-02 | ITSMA: 87% say ABM gives a higher return | 76% in its 2020 study, released January 2021 |

The two sales emails show why this matters. E1 congratulates Gong on a milestone it passed 20 months ago, and it has since announced $500M. The writer's own note under that draft says the milestone "may no longer count as recent". It could not look.

### The four with no findable source

All four are in A4: LiveRamp's "15 Fortune 500 target accounts" (A4-03), its "33% conversion rate to meetings within four weeks" (A4-04), the story that GumGum made a comic starring T-Mobile's chief executive because he was a Batman fan (A4-08), and that GumGum won the account (A4-09). Each appears on several marketing blogs that repeat it without a link to where it came from. Not finding a first publisher is not proof that there is none.

The searches tried, with the full list for each claim in `records.json`:

- **A4-03 and A4-04**, four searches shared: `LiveRamp ABM 15 Fortune 500 accounts 33% conversion meetings four weeks`, then the same figures with "original interview LiveRamp marketing director", with "Lattice Engines LiveRamp case study", and with "Named Account Marketing" and "case study source". Three repeating pages were read: Metadata.io, Cognism and TripleDart. One lead was left unread: the programme is said to have used Lattice Engines, since bought by Dun & Bradstreet, whose archived case study could not be opened.
- **A4-08**, eight searches across the two passes, among them: `GumGum T-Mobile comic book "T-Man and Gums" John Legere Batman`, the same with "Batman fan account-based marketing", and the same with the names of GumGum's executives and "interview". GumGum's comic, its guide page and Legere's own post were read.
- **A4-09**, five searches: `GumGum T-Mobile comic book "T-Man and Gums" John Legere Batman`, then variants adding "won account ABM", "won business account-based marketing", "pitch won T-Mobile business", and one limited to GumGum's, T-Mobile's and X's own sites.

### The eight that could not be opened

The tools left 14 claims unread. I tried all six pages in a browser the same day, and settled 6 claims.

| First publisher | Claims | What stood in the way of the tools | In a browser |
|---|---|---|---|
| Gartner | A1-04, A1-05, A1-11 | Every request met a "verify you're human" check | The address now leads to Gartner's marketing home page. The page has moved or gone |
| McKinsey | A2-02, A2-03, A2-04, A2-05 | The site did not answer `curl` or the page reader | The address now shows a 2026 edition, and reading it needs a registration |
| MIT | A2-06 | The report's address now leads to a page offering it through a form | The archive copy shows the report's cover and nothing else |
| Wyzowl | E1-03, E1-04 | A bot check on the statistics page | **Opened.** Both claims supported |
| RollWorks, on Payscale | A4-05, A4-06, A4-07 | The page has gone from the live site | **Opened** from the archive on a later try. All three differ |
| ITSMA | A4-02 | The old site fails its secure connection | **Opened** from the archive on a later try. Supported, and out of date |

The web archive answered every request in this run with "429 Too Many Requests", from the first researcher to the last checker, and at first gave my browser the same answer. The likeliest cause is the run itself: seven researchers and five checkers asked the archive many times from one connection. That is a guess. Two archive pages opened for him later.

The four McKinsey claims name the 2025 edition. McKinsey has since published a 2026 edition at the same address, so those four are likely out of date as well as unread. That is a lead, not a verdict.

## Errors that fit no problem type

Each of these was written down by a researcher or checker in the free-text field, in its own words. The grouping is the lead's. This section is written against the nine problem types as they stood on the day of the test. The spec has since changed to cover most of what is listed here.

1. **The publisher disagrees with itself.** Forrester's press release says 86% of purchases stall. Its own blog post on the same report, the same day, says 91% (A1-12). Belkins gives 6.8% and 5.8% on one page and 7% and 5.1% on another for the same two years (A3-03, A3-04). The draft matched one of the two each time. Seen on 3 claims.
2. **The data behind a finding described wrongly.** Calls where the publisher says opportunities (A2-12). Marked source-mislabelled as a half fit: the publisher's name is right.
3. **A fact true of one publisher pinned on two** (A3-05). Marked wrong-subject as a half fit: the figure is right for Google.
4. **Understated.** A dropped qualifier that makes the claim smaller than its source: "significantly more than 3,000" became 3,000 (E2-02). Overstated has no opposite.
5. **A best band flattened into a direction.** Belkins found a best middle band, 2 to 4 contacts for each company. The draft says fewer is better (A3-13).
6. **Two facts joined as if one explained the other.** "More than 99.9% of spam, which is nearly 15 billion emails a day" (A3-10). Google states them as two separate facts.
7. **Partly supported.** The core of a story is on the first publisher's page and the colourful details are only on pages that repeat it (A4-08). Or a real case study gains a detail it does not hold: website personalisation, in A4-05. One verdict cannot say both.
8. **Stale but true.** A figure the publisher did give, since replaced. The spec does not say which verdict out-of-date carries. Here a claim stated as a past finding stayed supported, and a claim stated as the present position (A4-01, "now part of") became differs.
9. **The page has gone or been rewritten.** Belkins replaced its study page with a new edition that drops the old figures. The Payscale case study and the MIT report have gone from their addresses. Dead-link is defined only for an address the draft gives, and no draft gave one. Seen on 4 publishers.
10. **Unlike measures set side by side.** A3 puts Backlinko's 8.5% (of emails sent) beside Belkins' 5.8% (of recipients who opened) and says the trend points down. Each claim is supported alone. The error is in the comparison, and no per-claim verdict can carry it.
11. **A narrow base left out, with the figure intact.** Microsoft's 9.4% is for one business group of 687 sellers against low users of the tool (A2-09, A2-10). The checker passed both, because the draft keeps "among high-usage sellers". Close to base-dropped, and a judgement call.
12. **A narrowed object widened.** Wyzowl's 86% is about a business that invests in "onboarding content that welcomes and educates". The draft says a business that invests in onboarding (E1-04). Close to wrong-subject, and too slight to call differs.

## Proposals

I accepted all of these on 25 November 2026. The spec carries them, and [ADR 0020](../../../docs/adr/0020-check-claims-promises-current-traceable-facts.md) says why. They are kept here as proposed. Two names changed on the way into the spec: the widened overstated is `strength-changed`, and the widened dead-link is `page-gone`.

### A replacement for the unmeasured paragraph in "Why it exists"

To replace the paragraph that begins "None of these measures how often":

> On 25 November 2026 Claude, with web search switched off for the test, was given six prompts a marketer or seller might type: four B2B articles and two sales emails. Separate checkers, and then a person with a browser, traced 58 claims from the six drafts to their first publishers. 40 were supported, 9 of them out of date. 6 differed, 4 had no findable first publisher, and 8 sat on pages nobody could open. Of the 46 claims whose first publisher could be read, none misstated a figure. The faults were age and credit: in 7 claims the publisher had since given a different figure, such as a 74% the government has replaced with 69%, and 3 claims credited one vendor's case study to its rival. No draft gave a web address for anything. Four of the six drafts told the user to check the figures, which the writer had not been able to do. The test is at [tests/check-claims/problem-test](README.md).

The three public cases above that paragraph can stay. This test does not support a pitch that AI drafts are full of wrong numbers. With this writer they were not. It supports a different one: the facts are as old as the model's memory, nothing is linked, and a careful reader cannot tell the 25 clean claims from the 33 others without doing this work.

### Changes to the nine problem types

1. **Keep all nine.** Five were not seen, and three of those five could not have been, because no draft gave a link or a quotation. A draft written with web search on, or by a person, will give both.
2. **Say which verdict out-of-date carries.** Proposed rule: supported when the draft dates the figure or states it as a past finding, differs when the draft states it as the present position. It was the commonest type by far, and the two passes had to make this rule up.
3. **Add a type for a publisher that gives two figures for the same thing.** Seen on 3 claims from 2 publishers. A suggested name: **publisher-disagrees**. The record carries both quotes.
4. **Widen overstated into a type that works both ways**, or add its opposite. A dropped qualifier can shrink a claim as well as inflate it, and a best band can be flattened into a rule. A suggested definition: "the strength of the claim has changed: a plan, a hedge, a range or a single case made firm, or a qualifier dropped."
5. **Widen source-mislabelled to cover how the study was done**, not only who published it: the data it rests on, the sample, the method. One case here, and it is the kind of error a reader of the report would mind.
6. **Widen wrong-subject to say "or one of several subjects"**, for a fact true of one named company and pinned on two.
7. **Widen dead-link to the first publisher's page**, not only the draft's link: the page has gone, or has been replaced by an edition without the figure. A suggested name for the wider type: **page-gone**.

### Other things the test raised for the spec

- **Split a story into its parts at stage 2.** "GumGum made a Batman comic starring the chief executive and won the account" is four claims. Listed as two, it forced one verdict onto a claim that was half supported.
- **could-not-open will be large.** 24% with the tools alone, and still 14% after a person tried every page. The spec leaves archive copies out, and the archive refused this run anyway. The hand-back needs to make this list short work for a person: the address, what the draft says, and what to look for.
- **A comparison between two claims is a thing to check.** Out of scope for the first version, and worth a line under "Not in this version" so the report does not imply it was done.
- **The cap of 40 claims a run looks reachable.** 58 first-pass checks and 38 re-checks took 70 web searches, because researchers went straight to a named publisher's site. An article of 700 to 800 words held 9 to 17 claims.

## Limits

- **One AI writer.** Claude, model `claude-fable-5-2`, on one day. No other assistant has been run. The prompts are in `prompts.md` for anyone who wants a second column.
- **The writer had no web search and was told so.** An assistant with search on may write fresher facts and give links. It may also carry different errors, such as crediting a page that repeats a figure. This test says nothing about that.
- **The writer ran as a subagent inside a coding session**, not in a plain chat. The wrapper told it to set the session's house rules aside. The drafts' plain style suggests some of those rules still showed.
- **A small sample.** Six drafts and 58 claims. The percentages are counts of this sample, not rates to quote for AI writing at large.
- **The quota took claims in sentence order**, not at random. The 8 unchecked claims come from the ends of three articles.
- **One reader listed the claims.** A second reader might split or merge some.
- **Claude checked Claude.** Researchers, checkers and the lead ran on the writer's model. A memory the writer has wrong, a checker may share. The guard is that every supported claim needed exact words from the publisher's page, found there by a script.
- **The prompts were written by the tester**, who knew what the test was for. They invite statistics and named companies, as a real brief often does.
- **8 claims are unsettled**, and they are not a random 8. They sit with the publishers most often quoted in B2B marketing. Their true verdicts could move the result either way.
- **Two verdicts are the lead's call** against the checker. Both are shown above with the other outcome.
- **No verdict here says a source was made up.**

## Every claim

The claim is as the reader listed it. Kind, the draft's exact words, the source the draft gives, both passes, every quote and every search are in `records.json` under the same ID.

| ID | Claim | Verdict | Problem types | What the first publisher's page says | Evidence |
|---|---|---|---|---|---|
| A1-01 | CEB is now part of Gartner. | supported | none | Gartner's own release of 6 April 2017 says it has completed its acquisition of CEB Inc., which matches the draft's 'now part of Gartner'. | [page 1](https://www.sec.gov/Archives/edgar/data/749251/000093041317001425/c88055_ex99-2.htm): "announced today that it has completed its acquisition of CEB Inc." |
| A1-02 | CEB put the average B2B buying group at 5.4 people in 2015. | supported | none | CEB's authors wrote in HBR in March 2015 that on average 5.4 people have to formally sign off on each B2B purchase, which matches the draft's 5.4 in 2015. | [page 1](https://hbr.org/2015/03/making-the-consensus-sale): "We found that, on average, 5.4 people now have to formally sign off on each purchase."<br>[page 2](https://hbr.org/2017/03/the-new-sales-imperative): "the number of people involved in B2B solutions purchases has climbed from an average of 5.4 two years ago to 6.8 today" |
| A1-03 | By 2017, CEB research published in Harvard Business Review had raised the average buying group to 6.8 people. | supported | none | The March-April 2017 HBR article by CEB authors says the average number of people involved in a B2B solutions purchase rose from 5.4 two years earlier to 6.8, as the draft says. | [page 1](https://hbr.org/2017/03/the-new-sales-imperative): "the number of people involved in B2B solutions purchases has climbed from an average of 5.4 two years ago to 6.8 today" |
| A1-04 | Gartner describes a typical complex B2B purchase as involving six to ten decision-makers. | could-not-open | none | Not read: Gartner's page could not be opened, so the draft's 'six to ten decision-makers' is neither confirmed nor contradicted. | none: the note is in `records.json` |
| A1-05 | Gartner says each of those decision-makers arrives with four or five pieces of information they have gathered on their own. | could-not-open | none | Not read: Gartner's page could not be opened, so the draft's 'four or five pieces of information they have gathered on their own' is neither confirmed nor contradicted. | none: the note is in `records.json` |
| A1-06 | Forrester's 2024 State of Business Buying report found that the average purchase involves 13 people. | supported | out-of-date | Forrester's own release for The State Of Business Buying, 2024 says on average 13 people are involved in the buying decision, as the draft says. | [page 1](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/): "On average, 13 people within an organization are involved in the buying decision, with 89% of purchases involving two or more departments."<br>[page 2](https://www.forrester.com/press-newsroom/forrester-2026-the-state-of-business-buying/): "The typical buying decision now includes 13 internal stakeholders and nine external influencers, with that number rising for more complex or strategic purchases." |
| A1-07 | Forrester's 2024 State of Business Buying report found that 89% of purchases span two or more departments. | supported | none | Forrester's own release for The State Of Business Buying, 2024 says 89% of purchases involve two or more departments, as the draft says. | [page 1](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/): "On average, 13 people within an organization are involved in the buying decision, with 89% of purchases involving two or more departments." |
| A1-08 | 6sense's Buyer Experience research puts the typical buying group at 11 members. | supported | out-of-date | A 6sense research article of November 2025 says buying groups average 11 members, as the draft says, but the 2026 Buyer Experience Report now puts the group at roughly 10 people. | [page 1](https://6sense.com/science-of-b2b/buyers-are-even-less-of-a-blank-slate-than-we-thought): "Given that buying groups average 11 members, and each of them have a wealth of experience, it would be surprising"<br>[page 2](https://6sense.com/buyer-experience-report-2026): "They average 10 members, and in 71% of journeys the group enters with preferences for two or more vendors" |
| A1-09 | 6sense found that buyers are roughly 70% of the way through their process before they speak to a seller. | supported | out-of-date | 6sense's 2024 report says 69% of the purchase process happens before buyers engage sellers, which matches the draft's roughly 70%, but its 2025 report moved the figure to 61% and its 2026 report to 59.2%. | [page 1](https://6sense.com/science-of-b2b/2024-buyer-experience-report/): "69% of the purchase process happens before B2B buyers engage with sellers"<br>[page 2](https://6sense.com/science-of-b2b/buyer-experience-report-2025/): "The point of first contact (POFC) shifted from 69% of the journey to 61%" |
| A1-10 | 6sense found that the vendor buyers contact first wins the deal about four times out of five. | supported | none | 6sense says 84% of buyers who had ranked their shortlist before contact bought from the first vendor they spoke with, and its 2026 report table puts 'Eventual winner was first vendor contacted' at 76.6% globally, both of which fit the draft's about four times out of five. | [page 1](https://6sense.com/science-of-b2b/buyers-are-even-less-of-a-blank-slate-than-we-thought): "before seller contact (nearly all buyers), 84% went on to purchase from the first vendor they spoke with."<br>[page 2](https://6sense.com/buyer-experience-report-2026): "Eventual winner was first vendor contacted" |
| A1-11 | Gartner's research shows buyers spend only 17% of their purchase time meeting potential suppliers, split across every vendor under consideration. | could-not-open | none | Not read: Gartner's B2B buying journey page, where the 17% figure is reported to sit, could not be opened, so the draft's wording is unchecked. | none: the note is in `records.json` |
| A1-12 | Forrester found that 86% of B2B purchases stall at some point in the process. | supported | none | Forrester's press release on The State Of Business Buying, 2024 says 86% of B2B purchases stall during the buying process, as the draft says, though Forrester's blog post of the same day gives 91%. | [page 1](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/): "Currently, 86% of B2B purchases stall during the buying process and 81% of buyers express dissatisfaction with their chosen providers."<br>[page 2](https://www.forrester.com/blogs/state-of-business-buying-2024/): "Nearly all (91%) of purchases stall at some point in the process, our survey data shows." |
| A1-13 | Forrester found that 81% of buyers end up dissatisfied with the provider they chose. | supported | none | Forrester's blog and press release on The State Of Business Buying, 2024 both say 81% of buyers express dissatisfaction with the provider they choose at the end of a purchase, as the draft says. | [page 1](https://www.forrester.com/blogs/state-of-business-buying-2024/), words in `records.json`<br>[page 2](https://www.forrester.com/press-newsroom/forrester-the-state-of-business-buying-2024/): "More than 80% of buyers are dissatisfied with the provider they choose at the end of a purchase process" |
| A2-01 | Salesforce's State of Sales report (2024) found that 81% of sales teams were either experimenting with AI or had fully implemented it. | supported | none | Salesforce's own announcement of the sixth State of Sales report (July 2024, 5,500 sales professionals) gives 81% of sales teams experimenting with or having fully implemented AI, which is what the draft says. | [page 1](https://www.salesforce.com/news/stories/sales-ai-statistics-2024/): "In fact, 81% of sales teams are either experimenting with or have fully implemented AI." |
| A2-02 | McKinsey's State of AI survey (2025) reported that 88% of organisations use AI regularly in at least one business function. | could-not-open | none | Not read. The draft says 88% of organisations use AI regularly in at least one business function; McKinsey's page could not be opened to check it. | none: the note is in `records.json` |
| A2-03 | McKinsey's State of AI survey shows marketing and sales consistently among the business functions where AI is most commonly used. | could-not-open | none | Not read. The draft says marketing and sales are consistently among the functions where AI is most commonly used; McKinsey's page could not be opened to check it. | none: the note is in `records.json` |
| A2-04 | The same McKinsey survey found only 23% of organisations were scaling AI agents anywhere in the business. | could-not-open | none | Not read. The draft says only 23% of organisations were scaling AI agents anywhere in the business; McKinsey's page could not be opened to check it. | none: the note is in `records.json` |
| A2-05 | The same McKinsey survey found a further 39% of organisations were still experimenting with AI agents. | could-not-open | none | Not read. The draft says a further 39% were still experimenting with AI agents; McKinsey's page could not be opened to check it. | none: the note is in `records.json` |
| A2-06 | MIT's "GenAI Divide" study (2025) claimed 95% of generative AI pilots produced no measurable impact on profit and loss. | could-not-open | none | Not read. The draft says 95% of generative AI pilots produced no measurable impact on profit and loss; the report itself could not be opened to check whether the 95% counts pilots, organisations or custom tools. | none: the note is in `records.json` |
| A2-07 | Salesforce's research has repeatedly found that sales reps spend 70% of their week on non-selling work. | supported | out-of-date | Two Salesforce editions back the draft (2024: 70% of time on non-selling tasks; 2022: 28% of the week selling, so 72% not), but the newest edition (February 2026) puts not-selling time at 60%, 'more than half', so '70%' is no longer Salesforce's current figure. | [page 1](https://www.salesforce.com/news/stories/sales-ai-statistics-2024/): "Sales reps report spending 70% of their time on non-selling tasks, making it difficult to connect with prospects."<br>[page 2](https://www.salesforce.com/news/stories/sales-research-2023/): "Reps spend just 28% of their week actually selling, with the majority of their time consumed by other tasks like deal management and data entry." |
| A2-08 | In Salesforce's 2024 data, 83% of sales teams using AI reported revenue growth, compared with 66% of teams without it. | supported | none | Salesforce's July 2024 announcement says 83% of sales teams with AI saw revenue growth that year against 66% without AI, matching the draft's figures, groups and year. | [page 1](https://www.salesforce.com/news/stories/sales-ai-statistics-2024/): "83% of sales teams with AI saw revenue growth this year vs. 66% without AI." |
| A2-09 | Microsoft's internal study of its own sellers using Copilot reported 9.4% higher revenue per seller. | supported | none | Microsoft reports a 9.4% increase in revenue per seller among high users of Copilot in one business group (687 sellers, Jan to June 2024, compared with low-usage sellers); the draft gives 9.4% higher revenue per seller in a sentence that ends "among high-usage sellers", which matches. | [page 1](https://www.microsoft.com/en-us/worklab/ai-is-already-changing-work-microsoft-included): "For one business group, Copilot is providing a 9.4% increase in revenue per seller and a 20% increase in close rates among high users of the tool."<br>[page 2](https://www.microsoft.com/en-us/worklab/ai-is-already-changing-work-microsoft-included): "Internal Microsoft sales team data based on 687 sellers of Microsoft 365 Copilot from Jan. - June 2024, as compared with sellers with low usage of Copilot." |
| A2-10 | Microsoft's internal study of its own sellers using Copilot reported 20% more deals closed among high-usage sellers. | supported | none | Microsoft reports a 20% increase in close rates among high users of Copilot, and elsewhere a 20% increase in won deals for a cohort of sellers; the draft says 20% more deals closed among high-usage sellers, which matches. | [page 1](https://www.microsoft.com/en-us/worklab/ai-is-already-changing-work-microsoft-included): "For one business group, Copilot is providing a 9.4% increase in revenue per seller and a 20% increase in close rates among high users of the tool."<br>[page 2](https://www.microsoft.com/en-us/worklab/ai-is-already-changing-work-microsoft-included): "High usage of Copilot means sellers who use Copilot daily at least 50% of the time during the testing period." |
| A2-11 | Salesforce deployed its own Agentforce AI agents on inbound lead follow-up and on its help site, and published the results. | supported | none | Salesforce says it runs Agentforce on its own help site and on lead follow-up by its sales development team, and publishes figures for both, as the draft says. | [page 1](https://www.salesforce.com/news/stories/first-year-agentforce-customer-zero/): "After one year, our service agent has handled 1.5+ million support requests on our help site, the majority of cases without humans."<br>[page 2](https://www.salesforce.com/news/stories/first-year-agentforce-customer-zero/): "(SDR) agent has worked on over 43,000 leads and generated $1.7 million in new pipeline from dormant ones." |
| A2-12 | Gong Labs research, drawn from millions of recorded calls, has reported higher revenue per rep among teams that use AI regularly. | differs | source-mislabelled | Gong reports that teams that deeply use AI generate 77% more revenue per representative than those that do not use it, which supports the draft's finding; but Gong says the analysis covered 7.1 million sales opportunities, where the draft says millions of recorded calls. | [page 1](https://www.gong.io/press/new-gong-labs-research-finds-ai-is-now-a-trusted-decision-maker-in-revenue-teams): "Teams that deeply leverage AI generate 77% more revenue per representative"<br>[page 2](https://www.gong.io/press/new-gong-labs-research-finds-ai-is-now-a-trusted-decision-maker-in-revenue-teams): "the Gong Labs research team analyzed 7.1 million sales opportunities across 3,613 companies" |
| A2-13 | HubSpot has built prospecting and research agents directly into its CRM. | supported | none | HubSpot's own product pages say its prospecting agent is built into its Smart CRM and that its data agent writes research to the CRM record, as the draft says. | [page 1](https://www.hubspot.com/products/sales/ai-prospecting-agent): "Prospecting agent is built into HubSpot's Smart CRM"<br>[page 2](https://www.hubspot.com/products/sales/ai-prospecting-agent): "Prospecting agent researches accounts, finds the right contacts, and drafts personalized outreach" |
| A3-01 | Backlinko's 2019 study with Pitchbox analysed 12 million outreach emails. | supported | none | Backlinko's own study page, dated 16 April 2019, says it analysed 12 million outreach emails with Pitchbox as data partner, as the draft says. | [page 1](https://backlinko.com/email-outreach-study), words in `records.json`<br>[page 2](https://backlinko.com/email-outreach-study): "Along with our data partner for this study, Pitchbox" |
| A3-02 | The Backlinko study found that only 8.5% of outreach emails received a response. | supported | none | Backlinko's study page says only 8.5% of outreach emails receive a response, as the draft says. | [page 1](https://backlinko.com/email-outreach-study): "Only 8.5% of outreach emails receive a response." |
| A3-03 | Belkins reported an average cold email reply rate of 5.8% in 2024. | supported | out-of-date, base-dropped | A live Belkins page says average cold email reply rates were 5.8% in 2024, as the draft says; Belkins' 2026 study adds that such earlier figures were counted against recipients who opened, and gives 0.45% for 2025. | [page 1](https://belkins.io/blog/how-to-generate-sales-leads): "Average cold email reply rates dropped from 6.8% in 2023 to 5.8% in 2024, based on our analysis of 16.5 million cold emails"<br>[page 2](https://belkins.io/blog/cold-email-response-rates): "In prior studies, reply rates were calculated against the number of unique recipients who opened an email." |
| A3-04 | Belkins reported an average cold email reply rate of 6.8% in 2023. | supported | base-dropped | A live Belkins page says average cold email reply rates were 6.8% in 2023, as the draft says; Belkins' 2026 study adds that such earlier figures were counted against recipients who opened. | [page 1](https://belkins.io/blog/how-to-generate-sales-leads): "Average cold email reply rates dropped from 6.8% in 2023 to 5.8% in 2024, based on our analysis of 16.5 million cold emails"<br>[page 2](https://belkins.io/blog/cold-email-response-rates): "In prior studies, reply rates were calculated against the number of unique recipients who opened an email." |
| A3-05 | In February 2024, Google and Yahoo began enforcing requirements for anyone sending more than 5,000 messages a day to their users: SPF, DKIM and DMARC authentication and one-click unsubscribe. | differs | wrong-subject | Google's page sets the February 2024 start, the 5,000 a day threshold, SPF, DKIM, DMARC and one-click unsubscribe as the draft says, but Yahoo's pages apply their rules to 'bulk senders' and say Yahoo will not specify a volume threshold, so the 5,000 figure is not Yahoo's. | [page 1](https://support.google.com/mail/answer/81126?hl=en): "Starting February 1, 2024, email senders who send more than 5,000 messages per day to Gmail accounts must meet the requirements in this section"<br>[page 2](https://support.google.com/mail/answer/81126?hl=en): "Marketing messages and subscribed messages must support one-click unsubscribe, and include a clearly visible unsubscribe link in the message body" |
| A3-06 | Those requirements include a spam complaint rate below 0.3%. | supported | none | Google's sender guidelines and Yahoo's sender page both require a spam rate below 0.3%, as the draft says. | [page 1](https://support.google.com/a/answer/81126?hl=en): "Keep spam rates reported in Postmaster Tools below 0.3%."<br>[page 2](https://senders.yahooinc.com/best-practices/): "Use the CFL to monitor your complaint rate, and ensure you are remaining below 0.3% if you are a bulk sender." |
| A3-07 | Google recommends staying under a 0.1% spam complaint rate. | supported | none | Google's sender guidelines say to keep spam rates below 0.10%, as the draft says. | [page 1](https://support.google.com/a/answer/81126?hl=en): "Keep spam rates reported in Postmaster Tools below 0.10% and avoid ever reaching a spam rate of 0.30% or higher." |
| A3-08 | Microsoft announced similar sender rules for Outlook consumer addresses in 2025. | supported | none | Microsoft's own post of 2 April 2025 announces SPF, DKIM and DMARC requirements for domains sending more than 5,000 emails a day to Outlook.com consumer addresses (hotmail.com, live.com, outlook.com), which is what the draft says. | [page 1](https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%E2%80%99s-new-requirements-for-high%E2%80%90volume-senders/4399730): "This applies to Outlook.com - our consumer service, which is supporting hotmail.com live.com and outlook.com consumer domain addresses."<br>[page 2](https://techcommunity.microsoft.com/blog/microsoftdefenderforoffice365blog/strengthening-email-ecosystem-outlook%E2%80%99s-new-requirements-for-high%E2%80%90volume-senders/4399730), words in `records.json` |
| A3-09 | Google says Gmail's AI defences block more than 99.9% of spam, phishing and malware. | supported | none | Google's own post says Gmail's AI-powered defences stop more than 99.9% of spam, phishing and malware from reaching inboxes, which matches the draft. | [page 1](https://blog.google/products/gmail/gmail-security-authentication-spam-protection/), words in `records.json` |
| A3-10 | Google says Gmail blocks nearly 15 billion unwanted emails a day. | supported | none | Google's own post says Gmail's defences block nearly 15 billion unwanted emails every day, matching the draft's figure. | [page 1](https://blog.google/products/gmail/gmail-security-authentication-spam-protection/), words in `records.json` |
| A3-11 | Apple's Mail Privacy Protection launched in September 2021 and preloads tracking pixels. | supported | none | Apple's iOS 15 release notice dated 20 September 2021 lists Mail Privacy Protection among the new features, and Apple's privacy page says the feature downloads remote content in the background whether or not the email is opened, which is the preloading the draft describes. | [page 1](https://www.apple.com/newsroom/2021/09/ios-15-is-available-today/), words in `records.json`<br>[page 2](https://www.apple.com/legal/privacy/data/en/mail-privacy-protection/), words in `records.json` |
| A3-12 | The Backlinko study found that personalised message bodies got 32.7% more replies than generic ones. | supported | none | Backlinko's own study page (12 million outreach emails, data partner Pitchbox, published April 2019) says personalised message bodies got 32.7% more replies than non-personalised ones, matching the draft. | [page 1](https://backlinko.com/email-outreach-study), words in `records.json`<br>[page 2](https://backlinko.com/email-outreach-study), words in `records.json` |
| A3-13 | Belkins' data shows smaller, tightly defined segments and fewer contacts per company outperform broad sends. | supported | none | Belkins' own statistics page says contacting 2 to 4 prospects per organisation gives the highest reply rates (over 7%) and campaigns targeting 240 to 499 people get the highest reply rates (10%), which points the same way as the draft's 'smaller segments and fewer contacts per company' but as a best band, not a rule. | [page 1](https://belkins.io/blog/cold-email-outreach-statistics): "prospects per organization gives the highest average reply rates (>7%)."<br>[page 2](https://belkins.io/blog/cold-email-outreach-statistics): "people get the highest reply rates of 10%." |
| A4-01 | ITSMA is now part of Momentum ITSMA. | differs | out-of-date | The firm's own site now calls it MomentumABM and says it is part of Accenture Song, and Accenture's 4 September 2025 release says Accenture acquired MomentumABM, which had earlier acquired ITSMA; the draft's 'now part of Momentum ITSMA' is the position before that. | [page 1](https://newsroom.accenture.com/news/2025/accenture-acquires-momentumabm-expanding-marketing-advisory-and-account-based-marketing-capabilities-for-b2b-growth): "Its capabilities were further strengthened by the acquisition of ITSMA five years ago."<br>[page 2](https://momentumabm.com/): "MomentumABM, now part of Accenture Song, is the growth advisory behind some of the world" |
| A4-02 | ITSMA found that 87% of marketers who measure ROI say ABM outperforms their other marketing investments. | supported | out-of-date | ITSMA's own post of 19 July 2017 says a full 87% of B2B marketers agree that ABM delivers higher ROI, which matches the draft's figure; ITSMA's 2020 study, released in January 2021, gives 76%. | [page 1](https://web.archive.org/web/20220323174537/https://www.itsma.com/abm-beyond-revenue-two-rs/): "with a full 87% of B2B marketers agreeing that ABM delivers higher ROI"<br>[page 2](https://www.prnewswire.com/news-releases/the-abm-leadership-alliance-and-itsma-release-2020-abm-research-study-301208219.html): "76% of respondents reported seeing higher ROI with ABM than with other types of marketing." |
| A4-03 | LiveRamp's ABM programme picked 15 Fortune 500 target accounts. | no-source | none | No first publisher's page was found for '15 Fortune 500 target accounts'; it appears only on pages that repeat it without a link to an origin. | none: the note is in `records.json` |
| A4-04 | LiveRamp's ABM programme produced a 33% conversion rate to meetings within four weeks. | no-source | none | No first publisher's page was found for '33% conversion rate to meetings within four weeks'; it appears only on pages that repeat it without a link to an origin, and those pages do not agree on what the 33% counts. | none: the note is in `records.json` |
| A4-05 | Payscale used Demandbase to focus advertising and website personalisation on target accounts. | differs | source-mislabelled | RollWorks' own case study says PayScale turned to the RollWorks platform to serve advertising to chosen job roles in its target accounts; the draft names Demandbase, a different vendor, and adds website personalisation, which the page does not mention. | [page 1](https://web.archive.org/web/20251011222624/https://www.rollworks.com/resources/case-studies/payscale): "PayScale then turned to the RollWorks Account-Based Platform to reach and engage those personas." |
| A4-06 | Demandbase's published case study on Payscale reports a 500% increase in traffic from target accounts. | differs | source-mislabelled | RollWorks' case study says PayScale increased traffic from its target accounts by 500% within seven months; the figure is right, and the draft credits it to a Demandbase case study. | [page 1](https://web.archive.org/web/20251011222624/https://www.rollworks.com/resources/case-studies/payscale): "Within seven months, the PayScale marketing team was able to show they increased traffic from their target accounts by 500%." |
| A4-07 | Demandbase's published case study on Payscale reports a sixfold return on investment within seven months. | differs | source-mislabelled | RollWorks' case study lists a 6x return in revenue among the results PayScale's marketing team influenced in seven months; the figure and the seven months are right, and the draft credits them to a Demandbase case study. | [page 1](https://web.archive.org/web/20251011222624/https://www.rollworks.com/resources/case-studies/payscale): "So far, PayScale's ABM program with RollWorks has delivered a 6x ROI in revenue."<br>[page 2](https://web.archive.org/web/20251011222624/https://www.rollworks.com/resources/case-studies/payscale): "In seven months, the marketing team at PayScale influenced:" |
| A4-08 | GumGum, wanting T-Mobile as a customer, produced a custom Batman-themed comic book starring T-Mobile's then-CEO John Legere. | no-source | none | GumGum's own pages say it published a comic, T-Man and Gums in The Data Knight, about a superhero helping 'a major mobile carrier', and the comic itself names T-Mobile; nothing read on them names John Legere or Batman or says he was a Batman fan, whereas the draft says GumGum learned Legere was a Batman fan and made a comic starring him. | [page 1](https://insights.gumgum.com/hubfs/T-Man_and_Gums_The_Data_Knight_Comic_Book.pdf): "GUMGUM PRESENTS: T-MAN AND GUMS, November 2016. Published by GumGum, Inc., 1314 7th St. Floor 5, Santa Monica, California 90401."<br>[page 2](https://insights.gumgum.com/hubfs/T-Man_and_Gums_The_Data_Knight_Comic_Book.pdf): "Oh. I switched to T-Mobile. I saw they did unlimited data on an ad when I was checking out reviews of the new Natural Disasters album." |
| A4-09 | GumGum won the T-Mobile account after the comic book. | no-source | none | No page from GumGum or T-Mobile was found saying GumGum won the T-Mobile account; Legere's own post only thanks GumGum for the comic. | none: the note is in `records.json` |
| E1-01 | Gong passed $300M in annual recurring revenue. | supported | out-of-date | Gong's own press release of 5 March 2025 says it surpassed $300 million in ARR, as the draft says, but Gong announced on 12 May 2026 that ARR has surpassed $500 million. | [page 1](https://www.gong.io/press/gong-surpasses-300m-arr-amid-increased-demand-for-ai-powered-revenue-solutions): "announced that it has finished a strong year and surpassed $300 million in ARR for fiscal year 2025, continuing its leading growth trajectory since its 2016 founding."<br>[page 2](https://www.gong.io/press/gong-growth-accelerates-past-55-yoy-arr-tops-500m): "Annual recurring revenue (ARR) has now surpassed $500 million." |
| E1-02 | Gong has launched AI agents. | supported | none | Gong's press release of 16 April 2025 introduces over a dozen AI agents, and its product page offers pre-built and custom agents today, as the draft says. | [page 1](https://www.gong.io/press/gong-redefines-ai-agents-to-deliver-real-revenue-impact): "the leading revenue AI company, is introducing over a dozen AI agents built specifically for revenue teams"<br>[page 2](https://www.gong.io/platform/ai-agents-for-revenue-teams): "Deploy specialized pre-built and custom AI agents that understand your business, execute revenue work, and help teams scale what drives results." |
| E1-03 | Wyzowl's onboarding research found 63% of customers say onboarding factors into whether they buy at all. | supported | none | Wyzowl's 2020 page says 63% of customers call onboarding an important consideration in whether they make the decision in the first place, which is what the draft says. | [page 1](https://wyzowl.com/customer-onboarding-statistics/#buying-decision), words in `records.json` |
| E1-04 | Wyzowl's onboarding research found 86% of customers say they are more likely to stay loyal to a business that invests in onboarding. | supported | none | Wyzowl's 2020 page says 86% of people would be more likely to stay loyal to a business that invests in onboarding content that welcomes and educates them after they have bought; the draft shortens this to a business that invests in onboarding. | [page 1](https://wyzowl.com/customer-onboarding-statistics/#loyalty), words in `records.json` |
| E2-01 | Greggs has more than 2,600 shops. | supported | out-of-date | Greggs reports 2,796 shops at 26 September 2026 and says "more than 2,700" on its own site; "past 2,600" is true but a milestone behind. | [page 1](https://assets.greggs.com/f/162306/x/3dfc9eec9a/260930-greggs-q3-trading-update-2026-final.pdf): "a total of 2,796 shops trading at 26 September 2026 (comprising 2,157 company-managed shops and 639 franchised units)"<br>[page 2](https://corporate.greggs.co.uk/about-us): "We now have more than 2,700 shops" |
| E2-02 | Greggs is aiming for 3,000 shops. | supported | none | Greggs states its aim as "significantly more than 3,000 shops" and, in its 2026 interim results, "at least 3,500 UK shops"; the draft gives 3,000 as the destination. | [page 1](https://assets.greggs.com/f/162306/x/3ca2423983/260729-greggs-interim-results-2026.pdf): "clear opportunity for at least 3,500 UK shops over the longer term"<br>[page 2](https://corporate.greggs.co.uk/about-us): "our ambition is to reach significantly more than 3,000 shops" |
| E2-03 | Greggs has new supply chain sites at Derby and Kettering. | supported | none | Greggs describes new supply chain sites (distribution centres) in Derby and Kettering, as the draft says; at 30 September 2026 they were due fully operational in 2026 and 2027 respectively. | [page 1](https://assets.greggs.com/f/162306/x/3ca2423983/260729-greggs-interim-results-2026.pdf): "the new supply chain sites in Derby and Kettering are completed"<br>[page 2](https://assets.greggs.com/f/162306/x/3dfc9eec9a/260930-greggs-q3-trading-update-2026-final.pdf): "Our two new distribution centres in Derby and Kettering will become fully operational in 2026 and 2027 respectively" |
| E2-04 | The 2025 cyber attacks on M&S and Co-op reportedly began with staff being deceived (social engineering), not a technology failure. | supported | none | Both companies told MPs the attackers got in by impersonating someone (social engineering), which matches the draft; the draft's "reportedly" is weaker than the companies' own statements. | [page 1](https://committees-api.parliament.uk/api/OralEvidence/16268/Document/Html): "In our case, the initial entry, on 17 April, occurred through what people now call social engineering."<br>[page 2](https://committees-api.parliament.uk/api/OralEvidence/16269/Document/Html): "They were able to impersonate a colleague and successfully answer a number of security questions to get their account reset." |
| E2-05 | The UK government's Cyber Security Breaches Survey 2025 found 74% of large UK businesses had a breach or attack in the previous 12 months. | supported | out-of-date | The 2025 survey gives 74% of large businesses, as the draft says; the next edition (Cyber Security Breaches Survey 2025/2026, published 30 April 2026) gives 69%. | [page 1](https://www.gov.uk/government/statistics/cyber-security-breaches-survey-2025/cyber-security-breaches-survey-2025): "Prevalence of breaches and attacks among large businesses (74%, the same as in 2024) and medium businesses (67% in line with 70% in 2024) has remained consistent."<br>[page 2](https://www.gov.uk/government/statistics/cyber-security-breaches-survey-20252026/cyber-security-breaches-survey-20252026): "medium (65%) and large (69%) businesses were more likely to have experienced a cyber breach or attack in the last 12 months" |
| E2-06 | The Cyber Security Breaches Survey 2025 found phishing was by far the most common type of breach or attack. | supported | none | The 2025 survey says phishing was the most prevalent type of breach or attack by far, as the draft says; the 2025/2026 edition says the same. | [page 1](https://www.gov.uk/government/statistics/cyber-security-breaches-survey-2025/cyber-security-breaches-survey-2025): "Phishing attacks remained the most prevalent type of breach or attack by far"<br>[page 2](https://www.gov.uk/government/statistics/cyber-security-breaches-survey-20252026/cyber-security-breaches-survey-20252026): "Phishing attacks remained the most prevalent type of breach or attack by far" |

## Files

| File | Holds |
|---|---|
| `README.md` | This file |
| `prompts.md` | The six prompts, exactly as used |
| `drafts/` | The six drafts, as given |
| `records.json` | Every claim's full record from both passes |
