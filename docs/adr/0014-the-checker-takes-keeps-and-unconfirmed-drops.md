# 14. The checker takes keeps and unconfirmed drops, not everything

**Status:** accepted, 4 November 2026

## Context

Every verdict could be checked twice. In the test behind the skill, one careful check of 15 companies took 9 to 12 minutes and 200,000 to 250,000 tokens of subagent work, so checking all 50 companies twice would double an already large bill.

## Decision

After the script has checked every quote, the checker re-checks every **keep** and every **drop** that rests on evidence the script could not confirm: a PDF of accounts, a page that would not load, or a quote not found. A drop whose every quote the script found on its page goes straight to the report. Companies marked check-by-hand are already going to a person. The checker sees the claims and verdicts, never the reasons or the evidence ([ADR 0002](0002-the-checker-never-sees-the-research.md)).

## Why

The two errors cost different amounts. A wrong keep sends money and time at a company that should not be on the list, and it is the error a person is least likely to catch, because a keep looks finished. A wrong drop loses one company from a list that had too many. A drop proven by quotes the script found on the cited pages is already checked by code, and a second agent adds little. Where the script could not confirm the evidence, the checker does.
