# check-call-summary: spec

The agreed design for `check-call-summary`, settled in two design rounds on 4 November 2026. Reviews check the skill against this file. Change it only on a new decision, and say why in a decision record.

## What it does

Checks an AI summary of a call against the call's transcript before the summary goes into a CRM, and catches the specific ways call summaries go wrong.

1. **Number.** The transcript is turned into numbered lines, so every finding cites a line you can read.
2. **Key facts.** A pass that never sees the summary reads the transcript and lists the key facts and any doubtful labels.
3. **Check.** The summary is split into claims. Each claim gets a verdict, a quote and any failure types.
4. **Verify.** A script confirms every quote is on the line it cites, word for word, and that every line of the summary was checked.
5. **Hand-back.** A report with the counts, every claim, and what to confirm with a person, plus a corrected draft with every change marked.

It checks summaries. It never writes one, and it never writes to a CRM.

## Who it's for

Anyone who puts AI summaries of calls into a CRM, or relies on them: sales, customer success, founders, recruiters. The README frames it around sales calls. Nothing in the skill assumes sales.

## What it takes in

- **A transcript.** Pasted text, or a `.txt`, `.md`, `.vtt`, `.srt`, `.docx` or `.json` file. Without a transcript there is nothing to check against, so the skill says so and stops. PDF is refused with a way round it (another format, or a paste), because it cannot be read reliably with the standard library.
- **One or more summaries of the same call.** Any written account counts: an AI summary, a CRM note, a follow-up email, meeting notes, or the recorder's own summary, copied or exported. With two or more, each is checked and the counts are shown side by side, so the user can see which tool summarises their calls best.

English transcripts only. Other languages are not tested, so not claimed.

## Where it runs

- **First, on every route**, the skill runs its own script with no arguments, which prints how to use it. If the script does not run, the skill lists its own folder, stops and tells the user why. If it can run code and the folder holds no `scripts/`, the skill was saved without its files, for example from a chat's offer to save it, and the user removes it and uploads the zip from the latest release under Customize, then Skills. Otherwise this chat cannot open the skill's files or run its script, and the user needs a normal chat (not an incognito one) with Create and edit files on. See [ADR 0017](../adr/0017-a-skill-stops-when-it-cannot-open-its-files.md).
- **The route follows what the chat can do**, not the app ([ADR 0019](../adr/0019-the-route-follows-what-the-chat-can-do.md)).
- **The subagent route** is the full version, wherever subagents can be launched: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The key facts pass is a fresh subagent (never a fork) that reads only the numbered transcript, from a folder that holds nothing else. Each summary gets its own fresh checker subagent, run in parallel.
- **The chat route**, in a chat that cannot launch subagents, needs code execution, which the first step has already shown. The skill asks for the transcript first, numbers it, and lists the key facts and doubtful labels before it asks for the summary, so the summary cannot steer what counts as a key fact. If the user gives the summary anyway, it is not read until the check, and the hand-back says the key facts were not fully independent of it. It then checks the claims in the same chat and says so; see [ADR 0011](../adr/0011-in-a-chat-the-check-runs-in-the-same-chat.md).
- **Other agents** are not tested and not claimed.

## Stage 1: Number

`scripts/transcript.py number` reads the transcript and writes `transcript-lines.md`: one numbered line per cue or turn, `[L42] 00:12:03 Priya: text`. It prints the line count and each speaker with their line count, which the skill shows the user so a wrongly parsed file is caught at once.

It reads WebVTT and SRT captions (voice tags, `Name:` prefixes, several turns in one caption), Word files, JSON (a list of turns with text and, where given, a speaker and a time), and plain-text layouts: a time then a name (`[00:01:23] Priya:`, or a range `[00:05 - 00:08] Priya:` as the Fireflies connector gives it), a name then a time (`Priya (00:01:23):`), a name alone (`Priya:`), and a name and time on a line of their own with the words below (Otter, Rev). Lines it cannot attribute are labelled `unlabelled`, never guessed.

## Stage 2: Key facts

The reader gets the numbered transcript and nothing else, in a folder that holds nothing else, and writes its list into that folder. On the subagent route the summaries are not saved anywhere until the reader has finished. It writes `key-facts.md` with two lists.

**Key facts.** What a CRM record depends on, each with its quote:

| Kind | What it covers |
|---|---|
| next-step | Something someone will do after the call, with its owner and any date |
| commitment | Something either side promised or agreed |
| date | A date or deadline that matters to the deal |
| number | Budget, price, headcount, volume, any figure that matters |
| who-decides | Who makes or signs off the decision |
| objection | A concern, blocker or reason not to buy |
| competitor | Another vendor or option mentioned |

Repeatable on purpose. "Did it miss anything important?" is not.

**Doubtful labels.** Lines where the content argues with the speaker label: someone answering their own question, "our product" said by both sides, a person addressed by name in their own line. The reader never decides who really spoke. It names the line, the label, who it more likely was, and why.

## Stage 3: Check

Each checker gets the numbered transcript, `key-facts.md` and one summary. It splits the summary into claims, one fact each. Every word of every line of the summary is covered by a claim, apart from headings, bare labels ending in a colon, and labels that are all bold.

### Verdicts

- **said**: the transcript says it. The claim carries the quote.
- **inferred**: not said in so many words, but reasonably drawn. The claim carries the quotes it rests on.
- **not-in-transcript**: nothing in the transcript supports it.
- **contradicted**: the transcript says otherwise. The claim carries the quote that contradicts it.

### Failure types

Counted by type. A claim can carry more than one, or none.

- **wrong-speaker**: a statement or position credited to the wrong person.
- **tone-read-as-sincere**: a joke, aside or line said for effect, written up as a real position. A transcript records words and loses delivery, so the fix is always "confirm with someone who was on the call", never a ruling on what was meant.
- **intention-as-done**: "I'll send it" recorded as sent.
- **owner-or-date-wrong**: a next step or commitment with the wrong owner or the wrong date.
- **made-up-detail**: a number, name or date nobody said.
- **overstated**: a hedge made firm. "We might look at it in Q2" becomes "interested, Q2".
- **left-out**: a key fact the summary does not carry. Counted from the key facts list, one per missing fact.

A claim is checked against what was said on the call, never against the meeting invite, the booking message or anything else outside the transcript. A purpose or agenda that does not come from the transcript is not-in-transcript.

Every key fact is marked as carried by the summary (with the claim that carries it), carried wrongly (with that claim), or missing.

Any claim resting on a doubtful label is marked doubtful and goes on the confirm list. A label is never corrected silently.

Inventing a failure to look thorough is the same failure as missing one.

## Stage 4: Verify

`scripts/transcript.py verify` checks each checker's file against the numbered transcript, the key facts and the summary. It fails on:

- a quote that is not on the line it cites, word for word and in whole words (case, spacing, quote marks and punctuation are ignored, nothing else), or a Quote line out of shape;
- a quote credited to a speaker the cited line does not carry;
- a `From` line that is not in the summary;
- a word of the summary that no claim covers;
- a verdict, failure type or key fact the formats do not allow, or a key fact left unmarked or marked twice;
- a claim with failures and no note, a key fact `carried wrongly` by a claim with no failure or `carried` by one with failures, and a doubtful label on a claim that cites no doubtful line;
- a `Quote check: failed` line, unless the skill runs verify with `--by-hand` after the one send-back.

Claims that fail are sent back to the checker once. A quote that still fails gets a `Quote check: failed` line from the skill, and is listed in the report as "quote could not be verified, check by hand". The skill never quietly drops or passes them.

## Stage 5: Hand-back

`scripts/transcript.py report` builds `check.md` from the checkers' files, in this order:

1. Any quotes to check by hand, when there are some.
2. Counts: verdicts and failure types, one column per summary.
3. **Confirm with a person before saving**: every next step and commitment (owners and dates), every key fact or claim resting on a doubtful label, every claim flagged tone-read-as-sincere, and every claim flagged intention-as-done or owner-or-date-wrong.
4. Doubtful labels.
5. Each summary's claims, in full.
6. The key facts, and which summary carried each.

The skill adds a line at the top only to say what is weaker than usual: a problem verify left standing, a check run in the same chat, or key facts listed with the summary already in the chat.

Then the skill writes `corrected.md`: each summary rewritten with removed text struck through, added text in bold, and the line number behind every change, except a claim struck because nothing in the transcript supports it. Wrong next steps are corrected like any other claim. A left-out key fact is added in bold with its line. Claims that turn on a doubtful label or on tone are marked, not changed. Nothing checks the corrected draft, so every change is read back against its claim and its line before it is shown.

## Files

On either route, a folder `check-call-summary/<YYYY-MM-DD>-<short-name>/` in the working directory:

- `transcript-lines.md`, `key-facts.md`, `check.md` and `corrected.md`.
- `summaries/`, each summary saved as given.
- `reader-in/`, holding only the numbered transcript the reader reads, and the list it writes.
- `working/`, each checker's file.

On the chat route, the report and the corrected draft as one document in the chat, as well as the files.

## Not in v1

Writing summaries, reading from a call recorder through a connector (proposed for a later version in [ADR 0012](../adr/0012-it-reads-from-a-connected-call-recorder.md)), reading from or writing to a CRM, audio, checking many calls in one go, and transcripts in languages other than English.

## Tests

- **Script tests** for every transcript format, the quote check, the coverage check and the counts.
- **Check set.** A made-up call of 48 lines across 20 minutes, with three speakers, as a `.vtt` file, with two lines carrying a planted mislabel, and one summary carrying one planted failure of each type plus clean lines. It passes when all 7 are caught with the right type, both mislabels are flagged as doubtful labels and no other line is, and no clean line gets a failure. The answer key is written by hand before any run.
- **Second check set**, added in 0.3.2. A made-up follow-up call of 48 lines across 9 minutes 38 seconds, with four speakers, as a plain-text export, with no mislabels and four lines that only look like them, and two summaries: one carrying a new planted failure of each type plus clean lines, and one fully accurate, so any failure on it is a false alarm. It passes when all 6 planted failures are caught with the right type, no clean line and no line of the accurate summary gets a failure, the audit committee rule is marked missing or carried wrongly, and no line is flagged as a doubtful label. The answer key was written by hand before any run. Graded by hand until a run is saved with its working files.
- **Formats.** Every layout above has a made-up sample in the script tests. The README claims a recorder's export only where its layout was confirmed from a cited source or a real export.
- **Live run.** A separate made-up discovery call between two fictional companies, with two summaries in different styles, run end to end and published as the README example.

## Privacy

A transcript holds other people's words. The skill sends nothing anywhere beyond the assistant it runs in, and its files stay in the user's folder. The README says the user's own company rules on call recordings still apply, and suggests trying the made-up example first.

## Packaging

Ships in the `stefancordery-skills` plugin with find-events, plugin version 0.2.0. The Claude.ai zip is attached to each GitHub release. UK English. No em-dashes.
