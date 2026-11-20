---
name: find-events
description: Find events worth attending to meet the people you want, with every event checked against the organiser's own page. Use when choosing conferences, meetups, trade shows or communities to attend.
license: MIT
---

# find-events

Listing sites cannot be trusted at the edges. Dead events stay listed for years, and last year's dates get copied forward as this year's. This skill finds events worth a person's time and money, then has a separate pass try to prove every one wrong against the organiser's own page before the person sees it.

## The run

Five stages, in order. Each needs the one before, so never skip ahead.

1. **Interview.** Build a brief. The user approves it.
2. **Discovery.** Research lanes write event records.
3. **Check.** Every record is checked by a context that did not find it.
4. **Score.** Every open event is scored out of 15.
5. **Hand-back.** A shortlist with the organiser's link on every line.

Read each reference file when its stage begins, not before, apart from the first check below. They are in this skill's folder, `${CLAUDE_SKILL_DIR}` (in a chat, the folder this file is in).

## Before you start

- **Check you can open this skill's files.** Every stage runs on them, not on this page. Open `references/interview.md` now with a tool that reads files. Stage 1 needs it next. Knowing its name from this page is not the same as opening it. If you have no tool that opens files, or it will not open, stop here and tell the user, in one message, that this chat cannot open the skill's files, so the skill cannot run in it, and that it needs a normal chat (not an incognito one) with **Create and edit files** turned on, under **Settings**, then **Capabilities**. Run nothing from this page alone.
- **Find today's date.** Every date window is worked out from it. If you are not sure of it, ask.
- **Work out which route you are on.** It depends on what you can do, not on which app you are in.
  - **The subagent route**, where you can launch subagents with the Agent tool and write files: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The full version below.
  - **The chat route**, in a chat that cannot launch subagents: follow the "In a chat" notes at each stage. The run needs web search. If you cannot search the web, say so and stop.
- **On the subagent route, the run folder** is `find-events/<YYYY-MM-DD>-<short-name>/` under the current working directory, with `working/` and `check-in/` folders inside it. Create it once the brief has a short name. Use absolute paths whenever you brief a subagent.
- **Tell the user what to expect** in one line: a few minutes of questions, then the search and the check, which take a while.

## Stage 1: Interview

Follow `references/interview.md`: one numbered question per message and nothing else in it, drafts before questions, "not sure" always accepted.

End by writing `brief.md` in the run folder and showing it. Wait for the user to approve or edit it. **Search nothing before approval**, apart from reading the user's own website in the first question.

If the user asks for a wider run than the default, set more lanes or more records per lane as they ask, and tell them it will take longer and cost more.

**In a chat:** show the brief in your reply instead of writing a file.

## Stage 2: Discovery

Read `references/discovery.md` and `references/record-format.md`.

Launch one **fresh general-purpose subagent** per lane, never a fork (a fork would carry this conversation). Launch them **all in one message** so they run in parallel. Brief each one with this, filling in the angle brackets:

```
You are researching one lane of an event search.
Read these files first, in this order:
1. ${CLAUDE_SKILL_DIR}/references/discovery.md
2. <run folder>/brief.md
3. ${CLAUDE_SKILL_DIR}/references/record-format.md
Your lane: <lane-name>: <scope from the brief>.
Write up to 10 records to <run folder>/working/lane-<n>-<lane-name>.md.
Do not launch further agents.
Reply with one line only: the number of records written and the path.
```

Tell the user the lanes are running. Do not read the lane files into this conversation: the strip step below counts their records for you.

**In a chat:** research the lanes one after another yourself, following `discovery.md`, and tell the user which lane you are on. Keep the records in the record format.

## Stage 3: Check

Read `references/check.md`, but only to brief the checker. **Never check the records yourself.** You know how they were found, and that is exactly what the check must not know.

Each checker gets the records and three facts from the brief: the user's **category**, the **date window**, and **who they want to meet**. Nothing else: not the brief, not the lane notes, nothing about how the records were found.

Check each lane as soon as it reports. There is no need to wait for the others. First copy its records, and only its records, into the `check-in/` folder, which holds nothing else:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/records.py" strip "<run folder>/working/lane-<n>-<lane-name>.md" "<run folder>/check-in/to-check-<n>-<lane-name>.md"
```

Note the count it prints. If it finds no records, the lane found nothing worth recording: tell the user and move on. Otherwise launch a **fresh general-purpose subagent** as that lane's checker, never a fork, briefed with this:

```
You are checking event records that someone else found.
Read ${CLAUDE_SKILL_DIR}/references/check.md first, then the records in <run folder>/check-in/to-check-<n>-<lane-name>.md.
Read only those two files. Do not list or open anything else in the run folder.
The person these events are for:
- Category: <category>
- Date window: <from> to <to>
- Who they want to meet: <one line>
Write every record, rewritten as check.md says, to <run folder>/working/check-<n>-<lane-name>.md.
Do not launch further agents.
Reply with one line only: the counts of verdicts and corrections by type.
```

When every checker has reported, merge their files:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/records.py" merge "<run folder>/records.md" "<run folder>"/working/check-*.md
```

The merge prints how many records came from each file. Compare each with the count the strip printed, and if a checker returned fewer than it was sent, run that check again before going on. The merge also warns about likely duplicates (the same URL or name found by two lanes). Remove the weaker copy of each, which renumbers the rest:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/records.py" drop "<run folder>/records.md" <number>
```

**In a chat:** you cannot check your own discovery honestly, so the user carries it to a fresh chat. Build one block that starts with this line:

> You are the checker in a find-events run. Do not start the find-events skill or any other skill. Follow only the instructions below.

Then the full text of `references/check.md`, then the three facts, then every record without the lane notes. Tell the user: "Open a new chat with web search on (an incognito chat is best, so it cannot see this one), paste everything in the box below, and paste its answer back here. A check in this chat would be me marking my own homework." When the answer comes back, count its records against the number you sent, and if any are missing, ask the user to have the checker finish them. If you can create files, save the checked records as `records.md` in the working directory; otherwise work from them in the chat.

If the user declines the check, carry on, but follow the "unchecked" rule in `references/shortlist.md`.

## Stage 4: Score

Read `references/scoring.md` and score every record in `records.md` that is open to the user. Write each score as its parts, such as `13 (R3 A3 V2 L1 B1)`.

## Stage 5: Hand-back

Read `references/shortlist.md`. Get the counts from the records, never from memory:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/records.py" tally "<run folder>/records.md"
```

Write `shortlist.md` in the run folder, in the order the reference sets out, then read every line back against its record.

Then finish with a short message: where the three files are, the headline from the check (for example "the checker corrected 19 of 34 records"), and the top 3 to check before spending anything.

**In a chat:** if you can run Python and saved `records.md`, run `python3 <this skill's folder>/scripts/records.py tally records.md`. Otherwise count the verdict headers and `Corrections:` lines by hand, twice. Then show one document holding the brief, the checked records and the shortlist.

## Throughout

- **Only the organiser's own page is a source of fact.** Listing sites help you find events, never confirm them.
- **Use only your built-in web search and page reading**, plus `curl` in a shell. Do not use third-party search, scraping or enrichment tools, even if they are connected.
- **Never invent a date, a price or an attendance figure.** Write what could not be seen.
- **Never book, register or spend anything.** The shortlist says what to check. The money stays with the person.
- **Write in the user's language and spelling.**
- **Keep the user posted** with one line at each stage. Discovery and the check take a while.
