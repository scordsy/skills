# Record format

One record per traced claim, in exactly this shape. The script reads these records, so the labels, the order of the evidence parts and the straight double quotes matter. A researcher and a checker write the same shape.

```
## C02
- Verdict: supported
- Problems: out-of-date
- First publisher: ITSMA, with the ABM Leadership Alliance
- Published: 19 July 2017
- Finding: ITSMA's post of 19 July 2017 gives 87% of B2B marketers. Its 2020 study gives 76%.
- Use instead: In 2017 ITSMA reported 87%. Its 2020 study gives 76%.
- Evidence:
  - E1 | page | https://example.org/2017-post | "with a full 87% of B2B marketers agreeing"
  - E2 | newer | https://example.org/2020-study | "76% of respondents reported seeing higher ROI"
```

## Lines every record has

- **Heading:** `## <claim number>`, the number from the claims file, such as `## C02`.
- **Verdict:** exactly one of `supported`, `differs`, `no-source`, `could-not-open`.
- **Problems:** `none`, or every problem type that applies, separated by commas. The ten are `second-hand`, `number-wrong`, `base-dropped`, `wrong-subject`, `strength-changed`, `source-mislabelled`, `misquoted`, `out-of-date`, `publisher-disagrees` and `page-gone`.
- **Finding:** one line a busy person can act on: what the first publisher's page says now, or what was and was not found. The user reads this line in the report, so write it for them, not as a note to yourself.

## Lines some records have

| Line | When | What it holds |
|---|---|---|
| First publisher | supported, differs, could-not-open | Who first published it |
| Published | supported, differs | The date the first publisher published it, or `not shown` |
| Use instead | differs, and a supported with a problem type | The words to use: the corrected fact, the newer figure or the right source |
| Still supported | a supported carrying number-wrong, base-dropped, wrong-subject, strength-changed, source-mislabelled or misquoted | Why the claim is still true as the draft words it |
| Page gone | page-gone | The address that has gone, and what loads there now |
| Address | could-not-open | The web address a person should open, starting `https://` or `http://` |
| In the way | could-not-open | What stood in the way: a paywall, a sign-up form, a bot check, a file that cannot be read |
| Look for | could-not-open | What to look for on the page: the figure, who it counts, and the date |
| Searches | no-source | One search per line, indented under it |
| Evidence | any record with a page that was read | One quote per line, indented under it |
| Check notes | a checker's record | What the checker found, in a line |

Write each as `- <Line>: <value>`, with the label spelled as in the table.

## Evidence lines

```
  - E<n> | <page or newer> | <web address> | "<quote>"
```

- **`page`** marks the first publisher's words on the claim. **`newer`** marks its newer figure or fact.
- **The web address** is the full address of the page the words are on, starting `https://` or `http://`.
- **The quote** is two or more words copied exactly, in one unbroken run, in straight double quotes. Never paraphrase and never join two passages. The script loads the page and looks for the words in order, ignoring case, spacing, quote marks and punctuation, and nothing else.
- Number them `E1`, `E2` and so on within each record.

## Records of each verdict

A `differs`:

```
## C05
- Verdict: differs
- Problems: source-mislabelled
- First publisher: RollWorks, case study on PayScale
- Published: not shown
- Finding: The case study is RollWorks' own. It says PayScale used the RollWorks platform. The draft credits Demandbase, a rival.
- Use instead: PayScale used RollWorks to serve advertising to chosen job roles in its target accounts
- Evidence:
  - E1 | page | https://example.com/case-studies/payscale | "PayScale then turned to the RollWorks Account-Based Platform"
```

A `no-source`:

```
## C03
- Verdict: no-source
- Problems: none
- Finding: No first publisher's page was found for "15 Fortune 500 target accounts". It appears only on pages that repeat it without a link to an origin.
- Searches:
  - LiveRamp ABM 15 Fortune 500 accounts 33% conversion
  - LiveRamp "Named Account Marketing" case study source
  - LiveRamp marketing director interview account-based 15 accounts
```

A `could-not-open`:

```
## C11
- Verdict: could-not-open
- Problems: none
- First publisher: Gartner
- Address: https://example.com/insights/b2b-buying-journey
- In the way: every request met a "verify you are human" check
- Look for: the number of people in a typical B2B buying group, whether it is 6 to 10, and the year of the research
- Finding: Gartner is the publisher the draft names, and its page would not open. Nothing is known either way.
```

A `supported` that departs from the page in a small way and is still true as worded:

```
## C14
- Verdict: supported
- Problems: strength-changed
- First publisher: Greggs plc
- Published: 4 March 2026
- Finding: Greggs says it sees room for "significantly more than 3,000 shops". The draft says it is heading for 3,000.
- Still supported: The draft's "heading for 3,000" is true as worded. It errs on the small side.
- Use instead: Greggs says it has room for significantly more than 3,000 shops
- Evidence:
  - E1 | page | https://example.com/results-2025 | "significantly more than 3,000 shops"
```

The addresses and dates in these examples are made up to show the shape.

## What the script refuses

`verify` fails on any of these, and the record comes back to be fixed.

About the verdict and the problem types:

- a `differs` with no problem type;
- a `supported` with no quote marked `page`;
- a `no-source` with no searches listed;
- a problem type that is not one of the ten;
- an `out-of-date` with no quote marked `newer`;
- a `publisher-disagrees` with fewer than two different quotes marked `page`, one for each figure;
- a `page-gone` with no Page gone line that holds an address;
- a `supported` carrying one of the six types that say the draft departs from the page, with no Still supported line;
- a `could-not-open` or `no-source` carrying any type other than page-gone;
- a `could-not-open` with no In the way line.

About what the report needs:

- a record with no Finding line;
- a `supported`, `differs` or `could-not-open` with no First publisher line;
- a `supported` or `differs` with no Published line;
- a `differs` with no evidence, or with no Use instead line;
- a `could-not-open` with no Address line or no Look for line.

About the file itself:

- a verdict that is not one of the four;
- an evidence line with no `page` or `newer`, no web address, or a quote of one word;
- a record for a claim that is not in the claims file, a second record for one claim, or a record for a claim marked not to be traced.

One thing the script does not refuse and you must still write: **a Use instead line on a `supported` claim that carries a problem type.** The report and the marked draft are built from it.

**A quote the script does not find on its page is not refused.** It is noted, and the claim goes to the checker.
