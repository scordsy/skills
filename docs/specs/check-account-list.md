# check-account-list: spec

The agreed design for `check-account-list`, settled in two design rounds on 4 November 2026, after a test of the problem it solves. Reviews check the skill against this file. Change it only on a new decision, and say why in a decision record.

## What it does

Checks every company on a target account list against the user's own profile, with evidence, before anyone spends money or time on the list.

1. **Profile.** An interview builds the profile: what the user sells, their best customers and why, the hard limits, and who to drop on sight. The user approves it.
2. **Load.** The skill asks for the list, and a script reads it, loads every website, records where each one lands, and splits the list into batches of 10.
3. **Research.** A fresh subagent per batch checks each company for six things, from primary sources, and writes a record with evidence.
4. **Verify.** The script loads every page cited and confirms each quote is on it, word for word.
5. **Re-check.** A separate checker re-checks every keep and every drop whose evidence the script could not confirm, without seeing the first pass's reasons or evidence.
6. **Hand-back.** A report and two CSV files.

It checks a list. It never builds one, never adds companies, and never contacts anyone ([ADR 0015](../adr/0015-it-checks-lists-and-never-adds-to-them.md)).

## Why it exists

On 4 November 2026 free ChatGPT and Claude were each asked for "50 companies like Breathe HR", for a made-up seller of a review platform whose best customer is a UK software company of 50 to 200 staff. A separate checker took 15 companies from each list. Usable as given: 1 of 15 from ChatGPT, 3 of 15 from Claude with the same context, 6 of 15 from Claude without it. None of the 45 was made up. The failures were real companies that were the wrong size, bought, based elsewhere, selling to the wrong buyer, or the seller's own competitors, and one was owned by the same group as the best customer. Both assistants told the user to check the list; neither did.

## Who it's for

Anyone about to work a list of target companies: sales, marketing, founders, agencies. The README frames it around the AI-made lookalike list. Nothing in the skill assumes where the list came from.

## What it takes in

- **A list.** Asked for once the profile is approved, never alongside a profile question ([ADR 0018](../adr/0018-the-list-comes-after-the-profile.md)). Pasted, or a `.csv`, `.xlsx`, `.md` or `.txt` file. A company name per row is the minimum. A website column is used when present, matched by header (website, domain, url and similar). Up to 50 companies a run on the subagent route and 15 on the chat route; longer lists are run in parts.
- **The interview's answers**, which become `profile.md`.

## The profile

From `references/profile.md`: one question at a time (each message asks one numbered question and nothing else, with a question's own parts in one list), a draft offered before each question, "not sure" always accepted with a stated default. It asks what the user sells (reading their site), one to three best customers (reading theirs, looking up each one's owner on its register, and drafting what they have in common), why they are the best customers, the hard limits (countries, staff range, buyer, whether group-owned companies count), and competitors and existing customers to drop. Named competitors and existing customers come only from the user's answers, or from the user's own site with the user's yes, never from the list being checked: a company named from the list is caught because it was named, not because the check worked ([ADR 0018](../adr/0018-the-list-comes-after-the-profile.md)). Nothing is checked before the user approves the profile.

## The six checks

Every company, against the profile, all six even after one finds a problem, so a drop lists every problem that applies:

1. **Website:** loads, is this company, and where it lands. A redirect to another domain is recorded by the script.
2. **Still trading:** the status on the official register for the company's country, or the best primary source where there is no free register.
3. **Owner:** bought or merged in the last five years (a rename is noted in Owner, and is not a problem on its own), including by the same group as a best customer. Owners are followed up to the top: a takeover of a parent company is a takeover of the company. When the profile does not want group-owned companies, ownership by a trading group counts as bought however old it is ([ADR 0016](../adr/0016-claims-are-facts-and-group-ownership-has-no-age-limit.md)).
4. **Size:** against the staff range, from the register or filed accounts where they give it, or a figure the company states on its own site.
5. **Fit:** what it sells and to whom, against the profile.
6. **Conflicts:** a competitor, an existing customer, the same group as a customer, or a duplicate row.

## Verdicts and problem types

Exactly one verdict per company: **keep** (every check passed, with evidence for website, trading, owner, size and fit), **drop** (at least one problem type, with evidence) or **check-by-hand** (evidence missing or contradictory, no problem proven). "Unverified" is never a problem on its own.

Problem types, counted in the report: **wrong-website**, **closed**, **bought**, **not-in-country**, **wrong-size**, **wrong-fit**, **competitor**, **customer**, **duplicate**. Definitions in `references/record-format.md` and the glossary.

## Countries

Any country. Every company gets the same six checks. How much can be proven depends on the free official register for the company's country; `references/registers.md` lists what each one shows. Where no free primary source gives a fact, it is `unverified` and the company goes to check by hand. Registers are read by the researcher the way a person would, never in bulk; the script only loads register pages a record cites, to check the quotes ([ADR 0013](../adr/0013-any-country-registers-read-by-hand.md)).

This replaced a first build that had the script read Companies House pages and claimed full checks for UK companies only. My call on 4 November 2026: the skill should work in any country, and no one should be blocked by a register because of it.

## Sources

Primary sources only: the company's own site, the official company register for its country, and the buyer's or company's own announcement. Listing sites, review sites, LinkedIn, databases and search summaries are never evidence. No third-party search, scraping or enrichment tools, and no API keys ([ADR 0004](../adr/0004-no-api-keys.md)).

## The script

`scripts/accounts.py`, standard library only:

- `load`: reads the list and numbers the companies (`A01` onwards), flagging likely duplicates by domain or name.
- `web`: loads every website (https, then www, then http) and records the status, where it lands, any redirect to another domain, and the page title.
- `split`: writes batches of 10 with each company's website result.
- Every request waits 2 seconds after the last one to the same site, and 5 seconds for an official register. Pages are loaded with a normal browser identity. The script never searches or browses a company register: it loads a register page only when a record cites it, once, to check the quote, never downloads a PDF it cannot read, and stops loading a register that refuses it ([ADR 0013](../adr/0013-any-country-registers-read-by-hand.md)).
- `verify`: checks every record's shape, including evidence for each problem type a drop claims, and loads every cited page once, recording each quote as verified, not-on-page, pdf or could-not-load. A page that does not hold the quote is loaded once more, because some pages change between loads.
- `strip`: writes the records that need a re-check, claims only.
- `report`: merges the first pass and the re-check, writes `checks.md`, `checked.csv` and `keepers.csv`, flags rows that give the same company number (duplicates across batches), and names any record sent to the checker that did not come back. `--unchecked` puts the unchecked line at the top.

## Where it runs

- **First, on every route**, the skill opens `references/profile.md` with a real tool. If it cannot, it lists its own folder, stops and tells the user why. If it can open files and the folder holds no `references/`, the skill was saved without its files, for example from a chat's offer to save it, and the user removes it and uploads the zip from the latest release under Customize, then Skills. Otherwise this chat cannot open the skill's files, and the user needs a normal chat (not an incognito one) with Create and edit files on ([ADR 0017](../adr/0017-a-skill-stops-when-it-cannot-open-its-files.md)).
- **The route follows what the chat can do**, not the app ([ADR 0019](../adr/0019-the-route-follows-what-the-chat-can-do.md)).
- **The subagent route** is the full version, wherever subagents can be launched: always in Claude Code, and in some Claude.ai and Claude Desktop chats. A fresh researcher subagent per batch, all in parallel, and a fresh checker subagent per batch that sees only the profile and the stripped records.
- **The chat route**, in a chat that cannot launch subagents: up to 15 companies. The research runs in the chat, the script runs where code execution can reach the web, and the check is handed to a fresh chat as one block to paste, because research that checks itself marks its own homework (the fallback an earlier test of these skills settled on, and [ADR 0002](../adr/0002-the-checker-never-sees-the-research.md)'s reasoning). If the user declines, the report and the closing message say at the top that no verdict was re-checked.
- **Other agents** are not tested and not claimed.

## The checker

Re-checks every keep and every drop whose evidence the script could not confirm (most often a PDF of accounts), not every company, to keep the cost down ([ADR 0014](../adr/0014-the-checker-takes-keeps-and-unconfirmed-drops.md)). It gets the claims and verdicts, never the reasons or evidence, and finds its own. The claims are facts and the documents they come from, never how they were found or what was concluded from them ([ADR 0016](../adr/0016-claims-are-facts-and-group-ownership-has-no-age-limit.md)). Its record replaces the first pass's in the report, which says what it changed.

## Hand-back

`checks.md`: counts by verdict and by problem type, how many the checker re-checked and changed, the check-by-hand list, and every company with its verdict, problems, reason, findings, the checker's note, and every piece of evidence marked with whether the script confirmed it. `checked.csv`: every company on the list with the verdict columns. The list's own other columns, such as CRM IDs, are not carried over. `keepers.csv`: the keeps only. The closing message gives the headline counts, at most five companies worth a second look, the checker's work in a line, and what was not checked.

## Testing

- **Script tests**, no network: list formats, websites, the record format, the quote check, what goes to the checker, and the report.
- **Check set**: 20 real companies against the made-up seller, most in the UK and some elsewhere, with at least one planted problem of each type and 6 clean companies. The answer key is written by hand from the registers and the companies' own sites before any run, and re-confirmed before each release. Pass: every planted problem caught with the right type, and no clean company dropped. Run once at medium effort and once at high, and both results published.
- **README example**: ChatGPT's real list of 50 from the test, run live, with the shared conversation linked so anyone can see the input. The README says the seller is made up and a drop means "does not fit this made-up seller", not a judgement on the company.

## Out of scope

Building or extending lists; contacts and email addresses; enrichment; scoring or ranking keeps; paid registers, and register APIs that need a key or payment (the free, keyless lookups some countries publish, such as Norway's and France's, are read like any register page); reading a register in bulk; reading a CRM; lists over 50 in one run.
