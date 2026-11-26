# check-call-summary

**An AI summary of a call, checked claim by claim against the transcript before it goes in your CRM.**

A lot of teams send call summaries straight into their CRM, and nobody checks them. Once a summary is in, it carries the same weight as a note someone checked, and everything downstream reads it as fact: the forecast, the follow-up, the next person to pick up the account.

Call summaries go wrong in particular ways. The recorder mixes up who said what, more often with three or more people on the call. A joke is written up as a buying signal. "I'll send it" becomes "sent". "Roughly thirty, not signed off" becomes "budget confirmed". And the thing that would have changed the deal is simply not there.

`check-call-summary` takes the transcript and the summary, splits the summary into single claims, and traces every one back to a quote on a numbered line you can read yourself. A script then checks every quote is really on that line, word for word, so the check cannot make up its own evidence.

## An example run

A made-up 4-minute discovery call: Sam sells call-scoring software at Larkspur, and Hannah (customer experience) and Raj (QA) are at Quillmarsh Home Insurance. Two summaries of it: a notetaker's bullet points and a CRM note. Everything here is fictional, the summaries included.

| | notetaker | crm-note |
|---|---|---|
| Claims | 24 | 21 |
| Said | 16 | 13 |
| Inferred | 4 | 5 |
| Not in the transcript | 1 | 2 |
| Contradicted | 3 | 1 |
| Failures on claims | 6 | 3 |
| Key facts left out (of 18) | 9 | 9 |

Neither summary is clean, and they go wrong in different places:

- **The notetaker reads well and overstates.** "There's something in next year's plan, roughly thirty thousand, but it's not signed off" became "Hannah confirmed a budget of £30k for Q1", a quarter nobody named. "I'll take ten licences on the spot", said if the tool could make Raj's team enjoy Monday mornings, became "Hannah is interested in ten licences". "I'd need to check with compliance before we share any recordings" became "Raj to share a sample of recorded calls". And it left out who signs off, the April peak and the compliance blocker.
- **The CRM note keeps the budget honest and invents a next step.** "Sam sends pricing for 220 seats this week": Hannah asked for pricing and Sam said he would put it in a proposal once he had seen the sample results. No week was mentioned. It also dropped the NDA, the data processing agreement and the follow-up date.
- **A label to confirm.** The CRM note credits Raj with wanting to wait until after the April peak. The transcript labels that line as Sam, who had just asked Raj the question, so the reader flagged the label as doubtful. Only someone on the call can settle it, so it goes on the confirm list rather than being corrected.

The [full run is here](../../docs/examples/check-call-summary/): the [transcript](../../docs/examples/check-call-summary/transcript.txt), the two [summaries](../../docs/examples/check-call-summary/summaries/), the [key facts](../../docs/examples/check-call-summary/key-facts.md), the [report](../../docs/examples/check-call-summary/check.md) and the [corrected drafts](../../docs/examples/check-call-summary/corrected.md).

## How it works

1. **Number.** The transcript (pasted, or an exported file) becomes numbered lines: `[L42] 00:12:03 Priya: ...`.
2. **Key facts.** A reader that never sees the summary lists what a CRM record depends on: next steps and their owners, commitments, dates, numbers, who decides, objections and competitors. It also flags any line whose words argue with its speaker label. Reading blind stops the summary deciding what mattered.
3. **Check.** Each summary is split into claims, one fact each. Every claim gets a verdict (said, inferred, not in the transcript, or contradicted), the quote it rests on, and any of these failure types:
   - **wrong-speaker**: credited to the wrong person
   - **tone-read-as-sincere**: a joke or aside written up as a position
   - **intention-as-done**: "I'll send it" recorded as sent
   - **owner-or-date-wrong**: a next step with the wrong owner or date
   - **made-up-detail**: a number, name or date nobody said
   - **overstated**: a hedge made firm
   - **left-out**: a key fact the summary does not carry
4. **Verify.** A script checks every quote is on the line it cites, word for word and from that speaker, and that every line of the summary was checked.
5. **Hand-back.** A report with the counts side by side, a list of what to confirm with someone who was on the call (owners, dates, doubtful labels, anything that turns on tone), every claim with its quote, and a corrected draft of each summary with every change marked and its line number.

It never decides who really spoke or what someone meant by a joke. A transcript keeps the words and loses the delivery, so those go to a person.

## Compare tools on your own calls

Give it two or more summaries of the same call, from different tools or from a tool and a person, and it checks each and shows the counts side by side. One call is not enough to choose a tool on, but a handful of your own calls will tell you more than any vendor's demo.

## What it reads

Pasted text, or a `.txt`, `.md`, `.vtt`, `.srt`, `.docx` or `.json` file. Not PDF: export another format, or paste.

| Recorder | How to get the transcript in | Layout checked against |
|---|---|---|
| Microsoft Teams | the `.vtt` download | [Microsoft's documentation](https://github.com/microsoftgraph/microsoft-graph-docs-contrib/blob/main/api-reference/v1.0/api/calltranscript-get.md) |
| Otter | the `.txt` export | [an Otter export in a published script](https://gist.github.com/th0rgall/d627140fc072725d098363604d239923) |
| Rev | the `.txt` export | [a published Rev transcript](https://www.rev.com/transcripts/tren-de-aragua-press-conference) |
| Zoom | the cloud recording `.vtt` | standard captions, not yet a real Zoom file |
| Fireflies | the `.docx`, `.srt` or `.json` export | not yet a real file |
| Fathom, tl;dv | copy the transcript and paste it | not yet a real copy |
| Google Meet | download the transcript Doc as `.txt` | not yet a real file |
| Gong, Grain, Avoma, Read.ai, Granola | a `.txt`, `.vtt` or `.docx` export where offered | not yet a real file |

Where a layout is not yet checked against a real file, it will usually still work, because it shares a shape with one that is. If it doesn't, the first stage shows you straight away: it prints each speaker and how many lines they have, and marks any line it could not put a name to as `unlabelled` rather than guessing.

## Next

Reading the call straight from your call recorder through its Claude connector, so it can check the recorder's own summary against the recorder's own transcript with nothing to export. It is designed but not in this version, because it has not yet been run on a real call.

## Install

See the [install steps](../../README.md#install). Then ask Claude something like "check this call summary against the transcript before I put it in the CRM", or run `/check-call-summary`.

**In a Claude.ai or Claude Desktop chat** turn on **Create and edit files**, and use a normal chat, not an incognito one: the skill opens its own files and the quote check is a script, and it stops without them. A chat that can run subagents runs the same full version as Claude Code: on 19 November 2026 Claude.ai did, on my account, for both tests below. A chat that can't asks for the transcript first and writes the key facts down before it asks for the summary. The check then runs in the same chat, which is weaker than a fresh checker, and the report says so. The script still checks every quote. That second way has not yet been run end to end.

**In Claude Code** the reader and each checker run as separate subagents, the checkers in parallel.

## What a run costs

The example run used 3 subagents: one reader and two checkers. Together they used 333,000 tokens. The reader took 49 seconds, and the two checkers, running in parallel, took 82 and 103 seconds. A longer call costs more. The longest call tested so far is the check set's, 48 lines timestamped across 20 minutes.

## Tested

A made-up call with three speakers, 48 lines timestamped across 20 minutes, two of its lines carrying a planted mislabel, and a summary carrying one planted failure of each type, a line resting on one of the mislabelled lines, and nine clean lines. The answer key was written by hand before any run. It passes only if every quote verifies, every planted failure is caught with the right type, both labels are flagged, the line resting on a mislabel is marked to confirm rather than called the wrong speaker, and no clean line gets a failure.

It passed on its first run, and again after the skill was tightened following two independent reviews. The first run also flagged one more fair catch on a planted line ("probably Doncaster and Wakefield" written as settled). The set, its answer key and both runs are in [`tests/check-call-summary/`](../../tests/check-call-summary/).

**On Claude.ai, 19 November 2026**, in a normal chat with memory off, the same call and summary passed every rule in the key, graded by hand. It asked for the transcript first and said why the summary had to wait. That chat could run subagents, so it took the same route as Claude Code, with a separate reader and a fresh checker. All 29 quotes in its report were checked afterwards against the numbered transcript, and each is on its line. That run's working files weren't saved, so it is not in the repo.

**A second check set**, written after that run: a made-up follow-up call with four speakers, 48 lines timestamped across 9 minutes 38 seconds, as a plain-text export rather than captions. It has no mislabels, but four lines that look like them. It comes with two summaries: one with a new planted failure of each type, and one fully accurate, so any failure on it is a false alarm. The answer key was written by hand before the run. On Claude.ai, on the same route, it passed every rule: all 6 planted failures caught with the right type, no failure on any clean line, none on any of the accurate summary's 23 claims, the left-out audit committee rule marked as carried wrongly, which the key accepts, and no line flagged as a doubtful label. All 54 quotes in its report were checked afterwards against the numbered transcript. The run's key facts and per-summary check files weren't saved, so the full grader can't run on it. It was graded by hand, and a unit test now re-checks every quote in the saved report and reads each rule in the key off it. The set, its key and the saved report are in [`tests/check-call-summary/check-set-2/`](../../tests/check-call-summary/check-set-2/).

## Read it with care

- **It checks against the transcript, and transcripts are wrong too.** If the recorder misheard a word, the check inherits it. Doubtful labels are flagged, but a mislabel that reads naturally will not be.
- **The reader and the checker are AI too.** The script makes sure every quote is real. Whether a claim is overstated, or a fact mattered, is still a judgement, written down with its reason so you can disagree.
- **Key facts are deliberately thorough.** The left-out count will often be higher than a short summary was ever meant to carry. Read the list and decide which ones your CRM needs.
- **Your company's rules on call recordings still apply.** The skill sends nothing anywhere beyond the assistant you are already using, and its files stay in your folder. Try it on the example call first if you want to see what it does.

## Related

Other skills write or tidy meeting notes, such as [`meeting-minutes-taker`](https://github.com/daymade/claude-code-skills) and the call summary in Anthropic's [sales plugin](https://github.com/anthropics/knowledge-work-plugins). Checking notes against a transcript is not a new idea either. What this skill adds is the list of specific ways call summaries go wrong, each one counted, and a script that checks every quote.

## Where it came from

My post [Lots of teams now send call summaries direct to their CRM. No one touches them.](https://www.linkedin.com/posts/stefancordery_lots-of-teams-now-send-call-summaries-direct-share-7517988790150471681-wPoZ/), and the mistakes behind it: call recorders mixing up who said what, the same call run through two tools with very different results, and summaries saved with nobody checking. The failure types are the ones I have caught myself.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [More skills](../../README.md)
