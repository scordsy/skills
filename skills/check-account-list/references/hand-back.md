# Hand-back

The script writes three files in the run folder:

- `checks.md`, the report: counts, the check-by-hand list, then every company with its verdict, problems, reason, what was found, what the checker did, and every piece of evidence with whether the script confirmed the quote.
- `checked.csv`: the whole list with the verdict columns added, ready to import into a spreadsheet or a CRM.
- `keepers.csv`: the keeps only.

Read `checks.md` back against the records once. If a line in it does not match its record, fix the record and run the report again. Never edit `checks.md` by hand.

## The message

Short, in this order:

1. **Where the files are.**
2. **The headline**, from the counts: "Of 50 companies, 9 keep, 33 drop, 8 check by hand." Then the problem counts, largest first, in plain words: "18 the wrong size, 11 bought in the last five years, 6 based outside your countries, 3 your competitors."
3. **The ones worth a second look**, at most five, each in one line with its reason: a competitor or existing customer on the list, a company owned by the same group as a best customer, a redirect to a buyer's site, a name trap. Pick the ones a person would most regret missing.
4. **The checker's work**, in one line: how many it re-checked and how many it changed.
5. **What was not checked**, if anything: companies with no record, records sent to the checker that did not come back, quotes that could not be confirmed by code (accounts PDFs, sites that would not load), and companies whose size is unverified. `report` prints these counts. Also any rows `report` flags as giving the same company number: they may be one company listed twice, in different batches.

Never add companies to the list or suggest replacements. The skill checks a list; it does not build one.

## Unchecked

If the user declined the re-check, run the report with `--unchecked`, which puts this line at the top of `checks.md`, and put the same line at the top of the message: "Not checked: these verdicts are the first pass only, and no separate check tried to prove them wrong."
