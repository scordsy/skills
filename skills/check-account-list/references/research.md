# Research instructions

If you cannot read web pages in this conversation, say so and stop. A check from memory is worse than no check.

You are checking companies on someone's target list against their profile. The list probably came from an AI assistant, a database export or a bought list. In a test of exactly this, none of the companies on an AI-made list was made up, and most were still wrong: bought, the wrong size, based elsewhere, selling to the wrong buyer, or a competitor of the person the list was for. They all looked fine. Your job is to find out, with evidence, which ones really are.

## What you are given

- `profile.md`: what the user sells, their best customers, and the hard limits.
- A batch file: each company's ID, name and given website, plus what the script found when it loaded that website (whether it loads, where it lands, and the page title).
- `record-format.md`: the shape to write each company in.

## Sources

Only primary sources count as evidence:

- **The company's own website**, including its about, terms and privacy pages (the legal entity named there is often the giveaway after a takeover).
- **The official company register for the company's country**, where it is free to read. `registers.md` in this skill's folder lists the free registers and what each one shows: status, owners, previous names, staff numbers, filed accounts. Where staff numbers are only in filed accounts (a PDF in the UK, for example), open the latest accounts and find the line. Small companies sometimes leave it out.
- **The buyer's or the company's own announcement** of a takeover or merger.

Listing sites, review sites, LinkedIn, news aggregators and search engine summaries can point you somewhere. They are never evidence. If that is all there is, the fact is unverified.

**Read a register the way a person would**: search for the company, open its page and the one or two pages you need, and move on. Never page through results in bulk, never loop over a register with a script, and if a register refuses you or asks you to slow down, stop using it and mark what it would have given as `unverified`. Nobody should be blocked because of this skill.

Use only your built-in web search and page reading, plus `curl` in a shell. Do not use third-party search, scraping or enrichment tools, even if they are connected. If a site turns away the built-in reader, try `curl -sL` with a normal browser user agent. Never try to get past a bot check.

## Check every company for

1. **Website.** The batch file says whether it loads and where it lands. A redirect to another company's domain is the commonest sign of a takeover: find out why. Read the homepage and confirm it is the same company and what it sells.
2. **Still trading.** The status on the official register for the company's country. Watch for **name traps**: a company with the same name that is unrelated. Match on the website, the address or the directors before trusting a register entry. With no free register, the company's own site (recent news, a working product, current prices) is weaker evidence: say so in the record.
3. **Owner.** The owners or controlling persons on the register where it shows them, their dates, and any previous names. Plus the company's own site and its terms or privacy pages for a takeover. A takeover, merger or change of control in the last five years means **bought**, whether the new owner is a company or an investor. An investor taking a minority stake, with no one in control, is not a change of control. When the profile does not want companies owned by a larger group, a company owned by a trading group is bought however long ago that happened. **Follow the owners up to the top.** When the owner is another company, look up who owns that one, and so on, until you reach people, an investor or a listed company. A holding company that has owned it for years can itself have been bought last month, and a takeover of any company above it is a takeover of this one.
4. **Size.** Against the profile's staff range. From the register or filed accounts where they give it, with the year; otherwise from the company's own site where it states a figure ("a team of 80"), with the page. Never estimate. Never use a LinkedIn or database headcount.
5. **Fit.** What it sells and to whom, from its own site, against the profile. Say it plainly when it sells to large organisations and the profile is small businesses, or the other way round.
6. **Conflicts.** A competitor of the user (sells what they sell, or is named in the profile), an existing customer, the same group as a best customer or an existing customer, or a duplicate of another company in your batch. Always give the company number in Registered: the report compares numbers across the whole list, so a duplicate in another batch is still caught.

## How to work

- **Assume each company is wrong until a primary source says otherwise.** You are not looking for reasons to keep it.
- **Finish all six checks, even after you find a problem.** A drop lists every problem type that applies. One problem can be argued away; the person reading the record needs to see all of them.
- **Copy quotes exactly**, two or more words, from the page you cite. A script loads every page and checks the quote is on it, word for word. A quote it cannot find is thrown back at you.
- **One company, one record.** Write every company in your batch, in batch order, even the ones you could not check.
- **Say what you could not see.** `unverified` and `not found` are correct answers. A guess is not.
- Keep your notes to the record. Do not add commentary between records.

Write the records to the file named in your brief. Reply with one line only: the number of records and the count of each verdict.
