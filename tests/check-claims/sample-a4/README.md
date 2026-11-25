# Sample: draft A4 through the script

A sample built by hand from the [test of the problem](../problem-test/README.md)'s records for draft A4, to show what `claims.py` writes. It is not a run of the skill: no reader, researcher or checker ran here, and every verdict is the test's own.

`verify` ran with page loading switched off, so no quote was looked for on a live page. That is why `check.md` shows every quote as not loaded, and lists five claims as sent to the checker with nothing back.

What the conversion added, because the test's records do not hold it:

- **`claims.md`** is the test reader's list for A4, nine claims, with every other sentence marked `no claim`.
- **Four records are the test's final ones**, after Stefan read the page by hand: C02, C05, C06 and C07. They sit in the research file. Only C08 had a real re-check, so only C08 has a checker's record.
- **Each Use instead line** restates that record's "page says". The test did not write one.
- **C08's first pass** recorded no first publisher or date. The publisher is taken from its two quotes and the date is marked as not recorded.
- **One quote, C08 E3 in the checker's file,** has a straight apostrophe where the page has a curly one. The quote check treats them as the same.
- **Each record's long note is left out.** It is in `records.json`.

**`marked.md` was written by hand** from this sample's records, by following the skill's `SKILL.md` and its hand-back reference. No page was loaded for it. A4 has only three kinds of mark in it (differs, supported with a problem type, and no-source): the hand-back reference shows the others.

To build it again, run `number` on `../problem-test/drafts/A4.md`, then `verify` and `report` on this folder. Run from a shell, `verify` will try the live pages.
