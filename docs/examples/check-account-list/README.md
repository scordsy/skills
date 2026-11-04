# check-account-list: example run

A real run of the skill on ChatGPT's real list of 50, from [this shared conversation](https://chatgpt.com/share/6aeb419c-94e0-83ed-b5e4-2338fdf3b679). The seller in the profile is made up: a customer review and advocacy platform sold to the marketing teams of B2B software companies, with Breathe HR as its best customer. Breathe HR and the 50 companies have nothing to do with it, and the two existing customers in the profile, Crunch and Thrive Learning, are made up for the example too. A drop means "does not fit this made-up seller", not a judgement on the company.

| File | What it is |
|---|---|
| `list.csv` | The 50 companies and websites exactly as ChatGPT gave them |
| `profile.md` | The profile they were checked against |
| `companies.md`, `web.md` | The numbered list, and where each website landed, written by the script |
| `working/research-*.md` | Each researcher's records, as written |
| `working/check-*.md` | Each checker's records, as written |
| `working/evidence.json` | Whether the script found each quote on its page |
| `checks.md` | The report, built by the script |
| `checked.csv`, `keepers.csv` | Every company with its verdict, and the keeps only |

Run on 4 November 2026 in Claude Code, at high effort: 12 subagents and 1,941,173 tokens. Loading the 50 websites took 55 seconds. The 5 researchers ran in parallel, the longest for 21 minutes 28 seconds (943,269 tokens together). Two quotes the script could not find were sent back to fresh researchers (168,694 tokens). The 5 checkers re-checked 33 companies (829,210 tokens) and changed the problems on 2 of them: Mention Me and Peppermint Technology also sell to large organisations. No verdict changed. From the start of the research to the report took 34 minutes 28 seconds.

One quote stayed unconfirmed: Findmyshift's homepage shows different words to visitors from different countries, so the words a researcher saw were not on the page the script loaded. Its drop rests on Findmyshift's own terms page, which says it is a Dutch company.

The run used the skill as it stood after the check set's second run, before its two reviews. The review fixes to the script change no verdict here: the records pass the tighter checks as they are. Two later changes to the instructions were not in force for this run: claim lines now hold facts only, and ownership by a trading group now counts whatever its age when group-owned companies are not wanted. Satago, owned by the TruFin group since 2018, was already dropped as bought on that reading.
