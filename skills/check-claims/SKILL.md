---
name: check-claims
description: Check every fact in a draft before you publish or send it. Each claim is traced to its first publisher and marked current, out of date, wrongly credited or not found. Use on AI-written drafts.
license: MIT
---

# check-claims

AI makes a draft fast, and the facts in it come from the model's memory. A figure can be real and still be two editions old, linked to nothing, or credited to the wrong company. Nobody reading the draft can tell which facts those are without tracing each one. This skill does the tracing: every factual claim, back to whoever first published it, with a web address and the exact words, and a plain answer on whether the fact is still current and credited to the right publisher.

It checks a draft. It never writes one, never rewrites the prose, and never publishes or sends anything.

## The run

Six stages, in order. Each needs the one before, so never skip ahead.

1. **Number.** A script numbers every sentence of the draft, so every finding cites a sentence.
2. **Claims.** A reader lists every factual claim, one fact each, and marks every other sentence as holding none.
3. **Trace.** A researcher finds the first publisher of each claim and records what its page says now, with evidence.
4. **Verify.** The script loads every page cited and confirms each quote is on it, word for word.
5. **Re-check.** A separate checker, which never sees the researcher's sources, tries to prove each claim wrong.
6. **Hand-back.** A report that opens with what to do, and the draft marked up with a verdict beside every claim.

Read each reference file when its stage begins, not before. They are in this skill's folder, `${CLAUDE_SKILL_DIR}` (in a chat, the folder this file is in).

## Before you start

- **Check you can open this skill's files and run its script.** Every stage runs on them, not on this page, and the quote check is the script. Run `python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py"` now, with nothing after it: it prints how to use it. Those printed lines are the pass, whatever exit code the shell reports. Knowing the script's name from this page is not the same as running it. If you have no tool that runs code or opens files, or the script does not run, stop here and tell the user, in one message, that this chat cannot open the skill's files or run its script, so the skill cannot run in it, and that it needs a normal chat (not an incognito one) with **Create and edit files** turned on, under **Settings**, then **Capabilities**. Check nothing by hand instead: a check whose quotes nobody verified is the problem this skill exists to catch.
- **Check you can search the web and read pages.** Every claim is traced on the live web. If you cannot, say so and stop. A check from memory is worse than no check.
- **Work out which route you are on.** It depends on what you can do, not on which app you are in.
  - **The subagent route**, where you can launch subagents with the Agent tool and run Python: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The full version below, up to 40 traced claims a run.
  - **The chat route**, in a chat that cannot launch subagents: follow the "In a chat" notes at each stage, up to 15 traced claims a run.
- **Get the draft.** Pasted text, or a `.txt`, `.md` or `.docx` file: an article, a report, the text of a deck, a sales email. A PDF cannot be read reliably: ask for one of the other formats or a paste. The skill reads English drafts only. For another language, say it is not tested and stop.
- **Say the privacy line before anything is searched**, in your first message, in these words or close to them: "Checking a claim means searching for it, so the facts in your draft will go out as web searches. Nothing else leaves this assistant, and the files stay in your folder. If the draft is under embargo, say so now and I will stop." Then carry on. If the user objects, stop.
- **Find today's date.** Whether a figure is still current is worked out from it.
- **Make the run folder:** `check-claims/<YYYY-MM-DD>-<short-name>/` under the current working directory, with `working/` and `check-in/` inside. Copy the draft into it exactly as given. Save a pasted draft to `draft.txt` there. Use absolute paths whenever you brief a subagent.
- **Tell the user what to expect** in one line, with the privacy line: the draft is numbered, its claims are listed, each one is traced to its first publisher and re-checked, and that takes a while.

## Stage 1: Number

```
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" number "<draft file>" "<run folder>/draft-lines.md"
```

Show the user the sentence count it prints, in one line. If the count looks wrong for the draft (a page of text read as three sentences, or a file read as nothing), say so and ask before going on: every later stage cites these numbers.

**In a chat:** the same command.

## Stage 2: Claims

Launch one **fresh general-purpose subagent** as the reader, never a fork. Brief it with this, filling in the angle brackets:

```
You are the reader in a check of the factual claims in a draft.
Read these files, in this order, and nothing else:
1. ${CLAUDE_SKILL_DIR}/references/reader.md
2. <run folder>/draft-lines.md
Write your list to <run folder>/claims.md.
Do not search the web. Do not launch further agents.
Reply with one line only: the number of claims by kind, how many are not to be traced, and how many claims each story became.
```

Then check its list against the numbered draft:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" verify "<run folder>" --claims
```

If it prints problems, launch one fresh reader with the same brief plus the problems, told to fix only what they name, and verify again. If problems remain, stop and show them to the user: everything after this rests on the list.

Show the user, in two or three lines: how many claims, how many will be traced, any claim that goes to a person instead (about their own company or a named person) and why, and how many claims each story became.

**Over the cap.** The command says when more than 40 claims are to be traced (15 on the chat route). Then this run traces the first 40 (or 15) in claim order, and stops there. Tell the user which sentences this part covers, such as "this part covers S1 to S64", and that the rest can be run as a next part afterwards. See "A draft in parts" below.

**In a chat:** read `references/reader.md` and write `claims.md` yourself from the numbered draft, then run the same command and fix what it names.

## Stage 3: Trace

Split the claims to trace into batches of 10, in claim order. Launch one **fresh general-purpose subagent** per batch, never a fork (a fork would carry this conversation). Launch them **all in one message** so they run in parallel. Brief each with this:

```
You are tracing a batch of factual claims from a draft to whoever first published each one.
Read these files first, in this order:
1. ${CLAUDE_SKILL_DIR}/references/research.md
2. ${CLAUDE_SKILL_DIR}/references/record-format.md
3. <run folder>/draft-lines.md
4. <run folder>/claims.md
Your batch is these claims and no others: <C01, C02, ...>.
Today's date is <date>.
Write one record per claim to <run folder>/working/research-<n>.md.
Do not open anything else in the run folder. Do not launch further agents.
Reply with one line only: the number of records and the count of each verdict.
```

Tell the user the batches are running. Do not read the research files into this conversation: the script reads them.

**In a chat:** read `references/research.md` and `references/record-format.md` and trace the claims yourself, in batches of 5, telling the user which batch you are on. Save every record to `working/research-1.md` in the run folder (for a later part of a draft in parts, `working/research-2.md` and so on, one file a part).

## Stage 4: Verify

```
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" verify "<run folder>" "<run folder>"/working/research-*.md
```

It loads every page cited, once, and prints how many quotes it found, how many it did not, how many sit in PDFs it cannot read, and how many pages would not load. Two things can come back:

- **Problems**, and the command fails: a record in the wrong shape, such as a `differs` with no words to use instead. Launch one fresh researcher per affected file with the same brief plus the problems, told to fix only what the problems name, and verify again. If problems remain, carry on, and say what is left at the top of the hand-back message.
- **A quote not found on its page.** This is not a problem to fix. Never send it back to a researcher and never change the record yourself. The claim goes to the checker in the next stage.

**In a chat:** the same command. If the code sandbox cannot reach the web, every quote comes back as not loaded. Carry on, and say in one line at the top of the hand-back message that no quote was checked by code.

## Stage 5: Re-check

Read `references/checker.md`, but only to brief the checker. **Never re-check a claim yourself.** You have seen where the first pass looked, which is exactly what the re-check must not know.

Write the checker's files:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" report "<run folder>"
```

This first `report` writes one file per research file into `check-in/`, named to match it (`working/research-2.md` gives `check-in/to-check-2.md`). Each holds every supported claim, and every claim resting on a quote the script could not confirm, with the claim and the verdict only: never the first publisher, the evidence, the reasons or the problem types. A `differs` whose every quote the script found goes straight to the report. Note the count it prints. If it is 0, no checker is needed.

It also writes a first `check.md`. That file holds the first pass's publishers and evidence. **Do not show it to the user yet, and never give it to a checker.**

Launch one **fresh general-purpose subagent** per file in `check-in/`, all in one message, never forks. For a later part of a draft in parts, launch one only for the files that match this part's research files: `report` writes the earlier parts' files again, and those claims already have a checker's record. Brief each with this:

```
You are re-checking factual claims from a draft that someone else has already traced.
Read these files first, in this order:
1. ${CLAUDE_SKILL_DIR}/references/checker.md
2. ${CLAUDE_SKILL_DIR}/references/research.md
3. ${CLAUDE_SKILL_DIR}/references/record-format.md
4. <run folder>/check-in/to-check-<n>.md
Do not list or open anything else in the run folder.
Today's date is <date>.
Write one record per claim, as checker.md says, to <run folder>/working/check-<n>.md.
Do not launch further agents.
Reply with one line only: how many you checked, agreed with and changed.
```

Then verify the checkers' files as in Stage 4, naming `working/check-*.md`. A checker's record in the wrong shape goes back to a fresh checker once, with the same brief plus the problems.

**In a chat:** you cannot re-check your own research honestly, so the user carries it to a fresh chat. Run the same `report` command, then build one block as `references/checker.md` sets out under "The block to paste". Tell the user: "Open a new chat with web search on (an incognito chat is best, so it cannot see this one), paste everything in the box below, and paste its answer back here. A check in this chat would be me marking my own homework." When the answer comes back, count its records against the number you sent and ask for any missing ones. Save it as `working/check-1.md` (numbered to match the research file) and verify it as above. If the user declines the re-check, carry on: the report says at the top, by itself, that no verdict was re-checked.

## Stage 6: Hand-back

Verify once more, then build the report:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" verify "<run folder>"
python3 "${CLAUDE_SKILL_DIR}/scripts/claims.py" report "<run folder>"
```

`verify` with no files named checks the whole run, and fails if a claim to be traced has no record. For a draft in parts it will name the claims waiting for a later part: that is expected, and the report lists them as not checked.

Then read `references/hand-back.md`, write `marked.md` as it says, and send the message it sets out. The script writes `check.md`. You write `marked.md`: the script does not.

**In a chat:** the same commands, then show the report and the marked draft in one document if you cannot hand over files.

## A draft in parts

A run traces up to 40 claims on the subagent route and 15 on the chat route. A longer draft is run in parts, in the same run folder:

1. The reader lists every claim in the whole draft, once.
2. Each part traces the next 40 (or 15) claims in claim order, writing research files numbered on from the last part's.
3. Each part re-checks only its own claims: the files in `check-in/` whose numbers match that part's research files. Never send an earlier part's file to a checker again.
4. Each part ends with its own `report`, which lists the claims still waiting under "Not checked: no record", and its own `marked.md`, which marks them as not yet checked.
5. Say which sentences each part covered, and ask before starting the next part. Never start one unasked.

## Throughout

- **The first publisher's own page or document is the only evidence.** Search results, AI answers, listing sites and pages that repeat a figure help find it. They never stand in for it.
- **Use only your built-in web search and page reading**, plus `curl` and the script. Do not use third-party search, scraping or enrichment tools, even if they are connected. No logins, no sign-up forms, no API keys.
- **A page that refuses is left alone.** Never get past a bot check, a paywall or a sign-up form, and never go to a web archive or another copy for it. The claim is `could-not-open`, and a person settles it in one visit.
- **Never guess a verdict.** `no-source` and `could-not-open` are correct answers. Not finding a source is not proof there is none, so never say a source was made up.
- **Never soften a verdict and never invent a problem.** The report puts the least work first. It does not make a `differs` sound smaller, and a clean claim stays clean.
- **Never rewrite the draft.** The marked draft adds marks and the words to use. It changes nothing else.
- **Write in the user's language and spelling.**
- **Keep the user posted** with one line at each stage. The trace and the re-check take a while.
