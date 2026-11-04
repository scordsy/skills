# File formats

A script reads these files and checks every quote in them, so keep each shape exactly. A block whose header is out of shape stops the run.

## The numbered transcript

`transcript-lines.md`, written by the script. One line per turn or caption:

```
[L42] 00:12:03 Priya Shah: We've got forty people in support right now.
```

The line number, the time if the transcript had one, the speaker label as the transcript gave it, then the words. `unlabelled` means the transcript had no label for that line.

## Quote lines

Every quote, in either file, is one line in this shape:

```
- Quote: [L42] Priya Shah: "We've got forty people in support"
- Quote: [L42-L43] Priya Shah: "forty people in support right now, maybe sixty by the summer"
```

- The words are copied from the cited lines exactly. The script ignores case, spacing, quote marks and punctuation, and nothing else. No paraphrase, no "...", no words left out of the middle.
- The speaker is the label on the cited lines, exactly as written there, even if you think it is wrong.
- A range covers consecutive lines with the same label, six at most. The words must be whole words: a quote that starts or ends part-way through a word fails. Words from two speakers are two quotes.
- Use the shortest stretch that proves the point.
- `- Quote: none` when there is nothing to quote.

## key-facts.md

Written by the reader. Two sections, each numbered from 1 in transcript order.

```
# Key facts

## K1. Ben sends the pricing by Friday  (kind: next-step)
- Quote: [L118] Ben: "I'll get the pricing over to you by Friday"

## K2. CFO signs off anything over twenty thousand  (kind: who-decides)
- Quote: [L64] Dan: "anything over twenty thousand goes to our CFO"

# Doubtful labels

## D1. [L57] labelled Priya, more likely Dan
- Quote: [L57] Priya: "That would be me"
- Why: Priya asks who signs off in L56, and L57 answers her.
```

The kinds are: `next-step`, `commitment`, `date`, `number`, `who-decides`, `objection`, `competitor`. A fact may carry more than one quote. A doubtful label header names one line, its label, and who it more likely was (or `more likely unclear`). If there are none, write the `# Doubtful labels` heading with nothing under it.

## A check file

Written by a checker, one per summary.

```
# Summary: tool-a

## C1. Support team is 40 people  [said]
- From: "Support team is 40 people, growing to 60 by summer."
- Quote: [L42] Priya Shah: "We've got forty people in support"
- Label: ok
- Failures: none

## C2. Ben sent the pricing  [contradicted]
- From: "Ben sent pricing and is waiting on feedback."
- Quote: [L118] Ben: "I'll get the pricing over to you by Friday"
- Label: ok
- Failures: intention-as-done
- Note: Ben said he would send it by Friday. Nothing in the call says it was sent.

## Key facts
- K1: carried wrongly (C2)
- K2: missing
```

- **Header:** `## C<n>. <the claim in a few words>  [<verdict>]`, numbered from 1 in summary order. Verdicts: `said`, `inferred`, `not-in-transcript`, `contradicted`.
- **From:** the summary line the claim comes from, copied exactly, in double quotes. Claims from the same line repeat the same From.
- **Quote:** one or more, as above. Needed for said, inferred and contradicted.
- **Label:** `ok`, or `doubtful (D1)` when a quote cites a line in the doubtful labels.
- **Failures:** `none`, or one or more of `wrong-speaker`, `tone-read-as-sincere`, `intention-as-done`, `owner-or-date-wrong`, `made-up-detail`, `overstated`, separated by commas.
- **Note:** optional. One or two sentences on what is wrong and what the transcript says instead. Needed whenever Failures is not none.
- **Never write a `Quote check` line.** The skill adds one, after the one send-back, to a quote that still cannot be found.
- **Key facts:** every K from `key-facts.md`, once each: `carried (C<n>)`, `carried wrongly (C<n>)` or `missing`. A missing key fact is counted as `left-out`.
