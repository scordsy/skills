# Hand-back

Two files and a message: `check.md`, which the script builds, `marked.md`, which you write, and a short message that opens with how little there is to do.

The person reading has just finished a draft they are happy with. A report that reads as a list of faults gets skimmed, and then the one fix that mattered is missed. So everything here puts the least work first. It never does that by softening a verdict.

## check.md

Built by the `report` command, in this order:

1. One line saying how many claims need nothing from the user, then a count for each kind of work.
2. **Fix these:** every `differs`, with the words to use instead first, then what the first publisher says now.
3. **Update or re-credit these:** every `supported` claim that carries a problem type, with the newer figure or the right source.
4. **Your call: no source found:** every `no-source`, with the searches tried. The user cuts it, softens it or cites it themselves.
5. **Confirm with a person:** claims about the user's own company, claims about a named person, pages that could not be opened, and supported claims whose quote the script looked for and did not find.
6. **Nothing to do:** every `supported` claim with nothing against it, with its first publisher and date.
7. **How this was checked:** counts by verdict and by problem type, how many claims the checker re-checked and changed, how many quotes the script found, and one line saying comparisons between claims were not checked.

Read it back against the records once. If a line does not match its record, fix the record and run `verify` and `report` again. Never reorder it and never change what the script wrote.

The script says what was not checked by itself: at the very top, that no verdict was re-checked, and in the last section, any claim sent to the checker that got no record back, any claim with no record, and how many quotes it could not confirm. Add nothing to the file.

## Pages that could not be opened

Each `could-not-open` claim is written in the report so a person can settle it in one visit: the web address, the draft's exact words, what stood in the way, and what to look for on the page (the figure, who it counts, and the date).

- **Do not try a second route** round a page that refused. No web archive, no cached copy, no other site's copy.
- **Do not guess the verdict** in the message or the marked draft. A could-not-open claim is unknown, not wrong.
- **Say it is one visit each,** and that the report gives the address and what to look for.

## marked.md

The draft with a mark beside every claim. You write it, from the draft exactly as given, the claims file and the final records: the checker's record where there is one, otherwise the first pass's. Take every word you add from `check.md`.

**Start from the draft as given**, not from the numbered draft, so its paragraphs, headings and formatting are kept. Change nothing in it. Add only marks and, where the rules below say so, the words to use.

**Where a mark goes.** Straight after the claim's draft words, and after the full stop if those words end the sentence. When two claims share the same draft words, their marks follow one another in claim order.

**What a mark says.** The claim number, then the verdict, then any problem types, in square brackets:

| The claim is | The mark |
|---|---|
| supported, nothing against it | `[C04: supported]` |
| supported, with a problem type | `[C02: supported, out-of-date]` then the words to use |
| supported, but on the confirm list because the script did not find its quote | `[C09: supported, confirm the quote]` |
| differs | `[C05: differs, source-mislabelled]` then the words to use |
| no-source | `[C03: no-source]` |
| could-not-open | `[C11: could-not-open]` |
| about the user's own company | `[C12: not traced, your own company]` |
| about a named person | `[C13: not traced, a named person]` |
| waiting for a later part, or with no record | `[C41: not checked]` |

**The words to use** follow the mark for every `differs` and every `supported` claim that carries a problem type. They are the record's Use instead line, word for word, in bold, then a link in round brackets:

```
[C02: supported, out-of-date] **In 2017 ITSMA reported 87%. Its 2020 study gives 76%.** ([ITSMA's 2020 study](https://example.org/2020-study))
```

- **The link's address** is the address of the record's first quote marked `newer` when it has one, otherwise of its first quote marked `page`.
- **The link's text** is who published that page and what it is, in a few words.
- **Do not strike through or delete the draft's own words.** The user decides what to change. The mark and the bold words sit beside the original.
- **A `no-source`, a `could-not-open` and a clean `supported` get the mark alone.** There is nothing to use instead.

A short made-up example with every kind of mark:

```
Our platform cut onboarding time by 40% for Acme. [C12: not traced, your own company] A 2025 survey by Example Research found that 74% of large firms had been attacked [C13: supported, out-of-date] **Example Research's 2025 survey found 74%. Its 2026 survey gives 69%.** ([Example Research, 2026 survey](https://example.org/2026)), and Example Bank says the average loss was 3 million pounds. [C14: could-not-open] Their chief executive, Sam Lee, is a keen sailor. [C15: not traced, a named person] The firm was founded in 2011 [C16: supported] and is now part of Example Group. [C17: differs, out-of-date] **and has been part of Other Group since March 2026.** ([Other Group, announcement](https://example.org/news)) It is said to have won 15 accounts in a month. [C18: no-source]
```

**The first and last lines.** If `check.md` opens with the line saying no verdict was re-checked, put the same line at the top of `marked.md`, then a blank line, then the draft. End the file with a rule and this one line:

```
---

Marked by check-claims on <date>. A mark in square brackets follows each claim. Bold words after a mark are what to use instead, with the page they come from. The reasons, the evidence and the list to confirm with a person are in check.md.
```

**Then check your own work.** Nothing checks this file, so:

- count the marks against the claims in the claims file: one each, no more and no fewer;
- read every bold passage back against its record's Use instead line;
- take every mark, bold passage and link out in your head, and the top and bottom lines with them: what is left must be the draft exactly as given.

## The message

Short, in this order. Lead with how little there is to do.

1. **What needs nothing, then the work, least first,** from the first lines of `check.md`: "Of 14 claims, 9 need nothing from you. 1 to fix, and the words to use are given. 2 to update with a newer figure. 1 where no source was found, which is your call. 1 page to open yourself." Leave out any kind of work with a count of 0. When no claim is clean, do not say so as a headline: open with the smallest piece of work.
2. **Each fix in one line:** the draft's words, then the words to use. All of them if there are five or fewer, otherwise the first five and how many more.
3. **Where the files are:** `check.md` for the reasons and evidence, `marked.md` for the draft with every claim marked.
4. **The checker's work,** in one line: how many claims it re-checked and how many it changed.
5. **What was not checked,** if anything: the line at the top of the report if there is one, any problem the verify stage left standing and which records it is in, claims waiting for a later part and which sentences this part covered, quotes the script could not confirm (in a chat whose code sandbox could not reach the web, that is all of them), and always that comparisons between claims were not checked. If one of these applies, say it first, above the counts.

Say the counts exactly as the report gives them. Never call a `differs` minor, never say a draft is "mostly fine", and never leave a kind of work out because it is awkward. Proportion comes from the order and the counts, not from softer words.

Never rewrite the draft, offer a rewritten version, or publish or send anything.
