# 13. Any country, and registers are read the way a person would

**Status:** accepted, 4 November 2026

## Context

`check-account-list` needs facts a company's own website rarely gives: whether it is still trading, who owns it, whether it has changed its name, and how many people it employs. Official company registers hold them, but every country's register is different, many charge, and the ones with free APIs need a key, which this repo does not use ([ADR 0004](0004-no-api-keys.md)).

An early build had the script read the UK register's public web pages directly. That made the skill UK-first, and it had the script making a few hundred register requests per run. Companies House says its search services are "not intended to be a source for bulk downloads", and that heavy users "may be denied access to these services without notice". My call: the skill should work for any country, and no one should be blocked because of it.

## Decision

- **Every company, in any country, gets the same six checks.** How much can be proven depends on that country's free register, and `references/registers.md` lists what each free register shows. Where no free source gives a fact, it is marked unverified and the company goes to check by hand.
- **The script never searches or browses a register.** The researcher reads registers with its own web tools, the way a person would: search, open the company's page and the one or two pages it needs, move on. Never in bulk, never in a loop. If a register refuses or asks it to slow down, it stops using that register.
- **The script loads each company's own website once, and each cited page once to check the quotes.** Most cited pages are register pages, so the quote check does touch registers: in the check set, 41 to 69 register pages per 20 companies, one at a time. It waits 2 seconds between requests to the same site and 5 seconds for a register, never downloads a PDF it cannot read, and stops loading a register that refuses it (HTTP 403 or 429) for the rest of the run.
- **Size can come from a figure the company states on its own site** where no register gives it, with the page cited. Never from a database or LinkedIn.

## Why

A skill that works in one country is a UK skill with a broad name. Being universal costs some certainty in countries with thin free registers, and the skill says so company by company instead of hiding it. Keeping register reads at a person's pace keeps every user well inside what the registers themselves ask for.

## Amended, 4 November 2026

The first version said the script never reads a register. A review found that the quote check loads every page a record cites, and most of those are register pages. Checking a quote needs the page, so the decision now says what the script does: it loads only pages a researcher has already cited, once each, at a slower pace for registers, and stops if a register refuses it. That keeps it to a person's reading of the same pages, without searching or browsing.
