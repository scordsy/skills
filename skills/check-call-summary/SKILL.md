---
name: check-call-summary
description: Check an AI call summary against the transcript before it goes in your CRM. Every claim traced to a quote, speaker mix-ups and missed next steps flagged. Use on any call summary or CRM note.
license: MIT
---

# check-call-summary

AI call summaries go into CRMs unchecked, and once they are in, everything downstream reads them as fact. They go wrong in particular ways: the recorder mixes up who said what, a joke is written up as a position, "I'll send it" becomes "sent", and the thing that would have changed the deal is simply left out. This skill checks a summary against the call's transcript, claim by claim, before anyone saves it.

It checks summaries. It never writes one, and it never writes to a CRM.

## The run

Five stages, in order. Each needs the one before, so never skip ahead.

1. **Number.** The transcript becomes numbered lines, so every finding cites a line.
2. **Key facts.** A reader that never sees the summary lists what the CRM record depends on, and any doubtful speaker labels.
3. **Check.** Each summary is split into claims, and every claim gets a verdict, a quote and any failure types.
4. **Verify.** A script confirms every quote is on the line it cites, word for word, and that every line of the summary was checked.
5. **Hand-back.** A report and a corrected draft.

Read each reference file when its stage begins, not before. They are in this skill's folder, `${CLAUDE_SKILL_DIR}` (in a chat, the folder this file is in).

## Before you start

- **Check you can open this skill's files and run its script.** Every stage runs on them, not on this page, and the quote check is the script. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/transcript.py"` now, with nothing after it: it prints how to use it. Knowing the script's name from this page is not the same as running it. If you have no tool that runs code or opens files, or the script does not run, stop here and tell the user, in one message, that this chat cannot open the skill's files or run its script, so the skill cannot run in it, and that it needs a normal chat (not an incognito one) with **Create and edit files** turned on, under **Settings**, then **Capabilities**. Check nothing by hand instead: a check whose quotes nobody verified is the problem this skill exists to catch.
- **Work out which route you are on.** It depends on what you can do, not on which app you are in.
  - **The subagent route**, where you can launch subagents with the Agent tool and run Python: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The full version below.
  - **The chat route**, in a chat that cannot launch subagents: follow the "In a chat" notes at each stage.
- **Get the transcript.** A file (`.txt`, `.md`, `.vtt`, `.srt`, `.docx` or `.json`) or pasted text. No transcript, no check: say there is nothing to check against, and stop. A PDF cannot be read reliably: ask for one of the other formats or a paste. The skill reads English transcripts only; for another language, say it is not tested and stop.
- **Not from a connector, in this version.** If the user asks to pull the call from a connected call recorder, say this version works from an exported file or a paste, and ask for one of those. Reading through a connector is planned for a later version.
- **On the subagent route, also get the summaries now.** One or more written accounts of the same call: an AI summary, a CRM note, a follow-up email, meeting notes. Ask for a short name for each (the tool or the person, such as `tool-a` or `rep-note`), used to label its column in the report. A recorder's own AI summary counts, copied or exported from the recorder like any other.
- **On the chat route, ask for the transcript only,** and say why in one line: the key facts are listed before the summary is read, so the summary cannot decide what mattered. If the user has already given a summary with the transcript, do not read it until Stage 3, and put one line at the top of the hand-back: "The key facts were listed with the summary already in the chat, so they are not fully independent of it."
- **Make the run folder:** `check-call-summary/<YYYY-MM-DD>-<short-name>/` under the current working directory, with `summaries/`, `reader-in/` and `working/` inside. Save a pasted transcript to `working/transcript-raw.txt`. On the subagent route, use absolute paths whenever you brief a subagent, and **do not save the summaries until the reader has finished** (Stage 2): until then nothing the reader could reach holds a summary.
- **Tell the user what to expect** in one line: the transcript is numbered, read for key facts, then each summary is checked claim by claim.

## Stage 1: Number

```
python3 "${CLAUDE_SKILL_DIR}/scripts/transcript.py" number "<transcript file>" "<run folder>/transcript-lines.md"
```

Show the user the line count and the speakers it prints, in one line. If the speakers look wrong (one speaker for a whole call, names split in two, or lines with no label), say so and ask whether to go on: every later stage leans on the labels. Then copy `transcript-lines.md`, and only that file, into `reader-in/`.

**In a chat:** save the transcript to a file, run the same command, and show the line count and speakers.

## Stage 2: Key facts

Launch one **fresh general-purpose subagent** as the reader, never a fork (a fork would carry this conversation, summaries included). Brief it with this, filling in the angle brackets:

```
You are the reader in a call summary check.
Read these files, in this order, and nothing else:
1. ${CLAUDE_SKILL_DIR}/references/reader.md
2. ${CLAUDE_SKILL_DIR}/references/formats.md
3. <run folder>/reader-in/transcript-lines.md
Do not list or open anything outside <run folder>/reader-in/.
Write your list to <run folder>/reader-in/key-facts.md.
Do not launch further agents.
Reply with one line only: the number of key facts by kind, and the number of doubtful labels.
```

When it reports, copy `reader-in/key-facts.md` to `<run folder>/key-facts.md` and verify its quotes:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/transcript.py" verify "<run folder>/transcript-lines.md" "<run folder>/key-facts.md"
```

If it prints problems, launch one fresh reader with the same brief plus the problems, told to fix only those blocks, and copy and verify again. If problems remain, stop and show them to the user: everything after this rests on the key facts.

**In a chat:** Read `references/reader.md` and `references/formats.md`, write `key-facts.md` from the numbered transcript alone, and verify it with the same command. Show the user the key facts in a short list. Only then ask for the summaries, with a short name for each.

## Stage 3: Check

Save each summary exactly as given to `summaries/<n>-<name>.md`. Then launch one **fresh general-purpose subagent** per summary, all **in one message** so they run in parallel, never forks. Brief each with this:

```
You are checking a call summary that someone else wrote, against the call's transcript.
Read these files, in this order, and nothing else:
1. ${CLAUDE_SKILL_DIR}/references/checker.md
2. ${CLAUDE_SKILL_DIR}/references/formats.md
3. <run folder>/transcript-lines.md
4. <run folder>/key-facts.md
5. <run folder>/summaries/<n>-<name>.md
The summary's name is <name>.
Write your check to <run folder>/working/check-<n>-<name>.md.
Do not launch further agents.
Reply with one line only: the counts of verdicts and failure types.
```

Never check a summary yourself on the subagent route. You have seen every summary and talked to the user about them, and a checker should come to each one cold.

**In a chat:** save each summary to `summaries/<n>-<name>.md`, read `references/checker.md`, and check each summary in turn, writing `working/check-<n>-<name>.md` for each. Tell the user which summary you are on. This check runs in the same chat that has seen everything, which is weaker than a fresh checker: say so in one line at the top of the hand-back. It is accepted here because the evidence is a fixed transcript and the script checks every quote, so the judgement is what the chat could bend, not the facts.

## Stage 4: Verify

For each check file:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/transcript.py" verify "<run folder>/transcript-lines.md" "<run folder>/key-facts.md" "<run folder>/summaries/<n>-<name>.md" "<run folder>/working/check-<n>-<name>.md"
```

If it prints problems, launch one fresh checker with the same brief plus the problems, told to fix only what the problems name and to leave every other claim as it is. A summary line not checked needs new claims: they go in summary order, and every later claim is renumbered, along with every `(C<n>)` in the key facts list. Verify again. Then:

- **A quote still not on its line:** add `- Quote check: failed` to that claim, and verify once more with `--by-hand` at the end of the command. The report lists the claim as "quote could not be verified, check by hand". Never delete the claim or change its verdict yourself. Without `--by-hand`, verify refuses that line, so a checker can never mark its own quote.
- **Any other problem still standing** (a summary line not checked, a key fact not marked): fix nothing yourself. Tell the user plainly what is left, and put it at the top of the hand-back.

**In a chat:** run the same command. If it prints problems, fix what it names by going back to the transcript, once, and verify again. Then apply the two rules above.

## Stage 5: Hand-back

Build the report:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/transcript.py" report "<run folder>/check.md" "<run folder>/key-facts.md" "<run folder>"/working/check-*.md
```

Then read `references/hand-back.md` and write `corrected.md` as it says, and read every change back against its claim.

Finish with a short message: where `check.md` and `corrected.md` are; the headline counts for each summary, from the counts table (for example "14 claims: 9 said, 2 inferred, 2 not in the transcript, 1 contradicted; 5 failures on claims; 2 key facts left out"); and the confirm list, in full if it is short, otherwise its first five lines and how many more. With more than one summary, say which carried the fewest failures and left out the fewest key facts, and that one call is not enough to choose a tool on.

**In a chat:** run the same command, then show one document holding the report and the corrected draft.

## Throughout

- **The transcript is the only source.** Not the meeting invite, the booking message, the CRM, or what anyone expects a call like this to contain.
- **Quote, never paraphrase, in a Quote line.** The script checks every quote word for word.
- **Never decide who really spoke.** Labels are flagged, never corrected. Only someone who was on the call can settle them.
- **Never decide what someone meant when it turns on tone.** A transcript loses delivery. Flag it for a person.
- **Never write to a CRM, a recorder or anywhere else.** The hand-back is files in the run folder.
- **Write in the user's language and spelling.**
- **Keep the user posted** with one line at each stage.
