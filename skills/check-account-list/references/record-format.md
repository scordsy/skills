# Record format

One record per company, in exactly this shape. The script reads these records, so the labels, the order of the evidence parts and the straight double quotes matter.

```
## A07 | Rotageek
- Website given: rotageek.com
- Website: https://www.rotageek.com/ loads; staff scheduling software
- Registered: UK, Companies House, 06783810, active since 2009
- Owner: Elmo Software UK Holdings Limited, since 30 May 2025
- Size: 39 staff (UK company, accounts to 30 June 2025)
- Fit: sells scheduling software to large retail and hospitality chains
- Conflicts: same group as your best customer, Breathe
- Verdict: drop
- Problems: bought, wrong-size, wrong-fit, customer
- Reason: Owned since May 2025 by ELMO, the group that owns Breathe; 39 staff; sells to large chains.
- Evidence:
  - E1 | owner | https://find-and-update.company-information.service.gov.uk/company/06783810/persons-with-significant-control | "Elmo Software Uk Holdings Limited"
  - E2 | size | https://find-and-update.company-information.service.gov.uk/company/06783810/filing-history/MzUxNDEyMjI5MmFkaXF6a2N4/document?format=pdf&download=0 | "The average number of persons employed by the company during the year was 39"
  - E3 | fit | https://www.rotageek.com/ | "workforce management for enterprise"
```

## The lines

The six lines from Website to Conflicts are **claims**. They are all the checker sees of your work, so write facts, and name the document a fact comes from ("39 staff, accounts to 30 June 2025"). Leave out how you found it ("matched by the redirect", "the privacy notice names") and what you concluded from it ("so not bought", "the kind of product you sell"). Conclusions go in Reason, and pages and quotes in Evidence.

- **Heading:** `## <ID> | <name as given on the list>`. Keep the ID from the batch file.
- **Website given:** as the list gave it, or `none`.
- **Website:** the address it lands on, whether that is this company, and what the site says the company sells, in a few words. If the given address is not the company's, say so and give the right one if you found it.
- **Registered:** country, register, company number and status (`active`, `dissolved on <date>`, `in liquidation`, `in administration`, or the register's own word), or `not found` with where you looked.
- **Owner:** `independent` with who controls it, or the owner and since when. Where the owner is another company, give the one at the top of the chain too, and since when. Say if the owner is private equity, and since when.
- **Size:** staff, with the source and the year: the register, filed accounts, or a figure the company states on its own site. For a company in a group, say whose figure it is (the legal company often employs nobody and a subsidiary employs everyone). `unverified` if no primary source gives it. `not needed` when the profile sets no staff range.
- **Fit:** one line on what it sells and to whom, in the company's own terms. Whether that fits the profile goes in Problems and Reason.
- **Conflicts:** `none`, or what it conflicts with: a competitor, an existing customer, the same group as a best customer or an existing customer, or another row on the list (give its ID).
- **Verdict:** exactly one of `keep`, `drop`, `check-by-hand`.
- **Problems:** `none`, or every problem type that applies, separated by commas. The types are below.
- **Reason:** one line a busy person can act on.
- **Evidence:** one line per item: `E<n> | <check> | <web address> | "<quote>"`. The check is one of `website`, `trading`, `owner`, `size`, `fit`, `conflict`. The quote is two or more words copied exactly from that page, never paraphrased. A script loads every page and checks the quote is on it, word for word.

## Problem types

- **wrong-website:** the given address does not load, is another company's, or is a parked page.
- **closed:** dissolved, in liquidation or administration, or the site says it has shut. A brand that still trades as a product of another company is **bought**, not closed.
- **bought:** a takeover, merger or change of control in the last five years, whether the new owner is a company or an investor. When the profile says "Owned by a larger group: not wanted", a company owned by a trading group also counts as bought, however long ago that happened. Ownership by an investor that is older than five years is noted in Owner and is not a problem.
- **not-in-country:** based outside the profile's countries. Use where the company is registered and headquartered, not where it sells.
- **wrong-size:** staff outside the profile's range, from a primary source.
- **wrong-fit:** sells something, or to someone, the profile rules out.
- **competitor:** sells what the user sells, or is named as a competitor in the profile.
- **customer:** an existing customer named in the profile, or owned by the same group as one of the best customers or existing customers.
- **duplicate:** the same company as another row (same website or the same company number). Drop the later row and name the earlier one in Conflicts.

## Verdict rules

- **keep:** every check passed, with evidence for `website`, `trading`, `owner`, `size` and `fit`. Size can be `not needed` only when the profile sets no staff range. Problems: `none`.
- **drop:** at least one problem type, each with evidence.
- **check-by-hand:** the evidence is missing or contradicts itself, and no problem is proven. `unverified` is never a problem on its own: it is a reason to check by hand. The Reason line says exactly what a person should look at.
