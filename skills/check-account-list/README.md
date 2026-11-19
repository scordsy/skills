# check-account-list

**Every company on a target account list checked before you spend on it: website, still trading, bought, size, fit and competitors, each with evidence you can click.**

Ask an AI assistant for "fifty companies like my best customer" and you get a list that looks right. I tested exactly that, and none of the companies was made up. Most were still wrong for the person asking: bought by someone else, too small or too big, based in another country, selling to the wrong buyer, or a competitor of the seller. One was owned by the same group as the best customer. Both assistants said to check the list before using it. Neither did.

`check-account-list` does the checking. It builds a short profile of who you sell to, then checks every company on your list against it, from the company's own website and the free official company register for its country. Every finding carries a web address and the exact words from that page, and a script loads each page to confirm the words are there. A separate checker then tries to prove every keep wrong.

It checks a list. It never builds one, never adds companies to it, and never contacts anyone.

## An example run

ChatGPT's real list of 50, from [this shared conversation](https://chatgpt.com/share/6aeb419c-94e0-83ed-b5e4-2338fdf3b679): "Breathe HR is one of our best customers. Give me a list of 50 companies like them that we should target." ChatGPT asked what the seller sells, and was told a customer review and advocacy platform for the marketing teams of B2B software companies, with Breathe as a UK software company of 50 to 200 staff.

**The seller is made up.** Breathe HR has nothing to do with it, and neither do the 50 companies. A drop below means "does not fit this made-up seller", not a judgement on the company. The profile also names two made-up existing customers, Crunch and Thrive Learning, to show that check.

| | Companies |
|---|---|
| Keep | 8 |
| Drop | 39 |
| Check by hand | 3 |

| Why dropped (a company can have several) | Companies |
|---|---|
| Wrong size for 50 to 200 staff | 22 |
| Bought or taken over in the last five years | 16 |
| Sells to the wrong buyer, mostly large enterprises | 12 |
| Wrong website | 5 |
| A competitor of the seller | 5 |
| Based outside the UK | 2 |
| An existing customer, or in the best customer's group | 2 |
| The same company twice | 1 |

The ones a person would most regret missing:

- **The best customer's own group.** Rotageek, in ChatGPT's highest-priority group, has been owned since May 2025 by ELMO, the group that owns Breathe.
- **Five of the seller's competitors.** Feefo, Reviews.io and Mention Me sit in ChatGPT's "highest priority" marketing group. The check also caught Force24, which sells an advocacy product, and Gleanin, a word-of-mouth tool for events.
- **Companies that are now someone else's.** Pure360's site lands on Spotler's and Peppermint Technology's on Litera's. Natural HR was bought by Moorepay in 2023 and Futrli by Sage in 2022.
- **The same company twice.** Capsule CRM and Zestia are one company under two names and two websites.
- **A wrong address for a good company.** apron.com is not Apron's site. Apron, at getapron.com, would otherwise have passed.

The 8 keeps are Cezanne HR, RotaCloud, Tribepad, Commusoft, CyberSmart, Red Sift, Juro and Legl. The 3 to check by hand are BrightPay, ApprovalMax and Street.co.uk, each with what a person should look at: where the company is really run from, which company employs the team, and whether a new investor took control.

The [full run is here](../../docs/examples/check-account-list/): the [list](../../docs/examples/check-account-list/list.csv), the [profile](../../docs/examples/check-account-list/profile.md), the [report](../../docs/examples/check-account-list/checks.md), the [CSV](../../docs/examples/check-account-list/checked.csv) and every researcher's and checker's records.

## How it works

1. **Profile.** A short interview, one question at a time, with a draft to correct before each one: what you sell, one to three best customers and why, the hard limits (countries, staff range, who buys, whether a company owned by a larger group counts), and competitors and existing customers to drop, taken from your answers and never from the list. You approve it before anything is checked.
2. **Load.** Only then does it ask for your list. A script reads it (a paste, `.csv`, `.xlsx`, `.md` or `.txt`), loads every website and records where it lands. A redirect to another company's domain is often the first sign of a takeover.
3. **Research.** Batches of 10, each researched by its own fresh subagent. Six checks for every company: website, still trading, owner (followed up to the top company), size, fit and conflicts. Only primary sources count: the company's own site, the free official register for its country, and the buyer's or company's own announcement. Never LinkedIn, a database or a listing site.
4. **Verify.** The script loads every page cited and confirms each quote is on it, word for word. A quote it cannot find goes back to a researcher.
5. **Re-check.** A separate checker that never sees how the first pass reached its answers tries to prove every keep wrong, and re-checks every drop whose evidence the script could not confirm (most often a PDF of accounts).
6. **Hand-back.** `checks.md` with the counts, a check-by-hand list and every company with its evidence; `checked.csv` with every company and its verdict; and `keepers.csv`.

Each company gets one verdict: **keep** (every check passed, with evidence), **drop** (at least one problem, with evidence) or **check by hand** (the evidence is missing or contradicts itself). "Unverified" is never a reason to drop.

## Companies in any country

Every company gets the same six checks. How much can be proven depends on the free official register for its country, and the skill says so company by company rather than hiding it. The UK's Companies House gives status, owners and staff numbers in filed accounts; Norway's register gives an exact headcount; many others give status only, and size then comes from a figure on the company's own site or stays unverified. [`registers.md`](references/registers.md) lists what each free register shows. So far it has been tested in depth on UK companies; the non-UK companies in the tests were checked for where they are based.

Registers are read by the researchers the way a person would, a few pages per company, never in bulk. If a register refuses or asks to slow down, the skill stops using it. Nobody should be blocked because of this skill.

## Install

See the [install steps](../../README.md#install). Then run `/check-account-list`, or ask Claude something like "check this list of target accounts before I buy contacts for it".

**In Claude Code**, the full version: up to 50 companies a run, a researcher subagent per batch of 10 and a separate checker per batch, all in parallel.

**In a Claude.ai or Claude Desktop chat**, turn on web search and **Create and edit files**, and use a normal chat, not an incognito one: the skill opens its own files, and the quote check is a script. A chat that can run subagents runs the same full version as Claude Code: on 19 November 2026 Claude.ai did, on my account. A chat that can't takes up to 15 companies and researches them in the chat. For the re-check it builds one block for you to paste into a fresh chat, because research that checks itself marks its own homework. If you skip that, the report says at the top that nothing was re-checked. That second way has not been run end to end yet.

## What a run costs

The example run of 50 companies used 12 subagents: 5 researchers, 2 that fixed a quote the script could not find, and 5 checkers. Together they used 1,941,173 tokens. From the start of the research to the report took 34 minutes 28 seconds, on high effort. The check set's 20 companies used 812,717 tokens at medium effort and 767,178 at high.

## Tested

20 real companies against the same made-up seller: 6 written as fitting, and 14 with at least one planted problem of every type, including three name traps, where Companies House holds an unrelated company with the same or a similar name. The answer key was written by hand from Companies House, the Norwegian register and the companies' own sites before any run.

It took three runs at each effort to get here, and all three are published:

- **Run 1.** High passed. Medium failed on two companies, both dropped for the right reason but missing a second problem: the researcher stopped at the first problem it found, and read only a company's direct owner, not who owns that owner. The instructions were fixed for any list: finish all six checks, and follow owners to the top.
- **Run 2.** Both efforts passed.
- **Run 3**, after two independent reviews tightened the script and the instructions. Both passed: every planted problem caught with the right type, all three name traps seen through, no company that fits dropped. Both checkers also found something my key had missed: a July 2026 filing that puts one of Payescape's investors above 50%. The register's summary page still showed the old figure. That company is now marked unsettled, and under the key as first written the high run would have failed on it.

| Run 3 | Result | Tokens | Time |
|---|---|---|---|
| medium | passed | 812,717 | 19 min 2 s |
| high | passed | 767,178 | 26 min 0 s |

Time is the longest researcher plus the longest checker. Every run, the answer key and its sources are in [`tests/check-account-list/`](../../tests/check-account-list/).

**On Claude.ai, 19 November 2026**, in a normal chat with memory off, I played the made-up seller through the profile interview, then gave it 12 of the 20 check-set companies, covering every problem type and all three name traps. Payescape, the unsettled one, was left out. That chat could run subagents, so it took the same route as Claude Code: 2 research batches and separate checkers. Every verdict matched the key: 3 kept, 9 dropped with every required problem type and none forbidden, and nothing sent to check by hand. The script confirmed 128 quotes, and 11 were in PDFs, which the checker reviewed. The checker re-checked 9 companies and changed nothing. It was graded by hand, and the run's files are not in the repo.

The profile interview showed two slips, both fixed in 0.3.2. It asked for the list and its first question in the same message. And after seeing the list, it added Feefo, a company on it, to my named competitors, which would have given away the test of catching a competitor by the kind of product. I had it taken out before approving the profile. The skill now asks for the list only once the profile is approved, and never takes a competitor or customer from it. It also now opens its own files first, and stops and says so if it can't, as find-events does. These changes have not been re-run on Claude.ai yet.

## Read it with care

- **Facts go stale.** Companies are bought and close every week. The report is dated; check again before you act on an old one.
- **The researchers and the checker are AI too.** The script confirms every quote is real and on the page cited. Whether a company sells to small businesses, or whether an investor took control, is still a judgement, written down with its reason and evidence so you can disagree.
- **Size is a staff figure from filed accounts or the company's own site.** For a company in a group, the legal company can report nobody while a subsidiary employs everyone. The record says whose figure it is.
- **It searches the names you give it.** Company names, and your best customers' and competitors' names, go to web search and to public registers, and the script loads each company's website and each page cited. Nothing else leaves the assistant you already use. Do not use it on a list you are not allowed to research.

## Related

Hyreflow's [qualify a company list against your ICP](https://www.hyreflow.ai/skills/qualify-against-icp) qualifies a list before you pay to enrich it, using its paid data connections and looking at a company's site only where it cannot decide. This skill uses no paid tools, and checks every company for whether it still trades, who owns it and whether it is the right size, with evidence for each.

Its sibling is [list-decay](https://github.com/scordsy/list-decay), which finds the dissolved and closing companies on a UK prospect list before you pay to enrich, verify or email them.

## Where it came from

My own test on 4 November 2026: free ChatGPT and Claude each asked for 50 companies like Breathe HR, for the made-up seller above. A separate check of 15 companies from each list found 1 usable as given from ChatGPT's, and 3 or 6 from Claude's. None of the 45 was made up. They were real companies that were the wrong size, bought, based elsewhere, selling to the wrong buyer, or the seller's own competitors.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [More skills](../../README.md)
