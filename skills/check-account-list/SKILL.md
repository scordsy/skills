---
name: check-account-list
description: Check every company on a target account list before you spend on it. Website, still trading, bought, size, fit and competitors, each with evidence. Use on AI-made, exported or bought lists.
license: MIT
---

# check-account-list

Ask an AI assistant for "fifty companies like my best customer" and you get a list that looks fine. In a test of exactly that, none of the companies was made up, and most were still wrong: bought by someone else, too small or too big, based in another country, selling to the wrong buyer, or a competitor of the person asking. The assistants even said to check the list before using it. This skill does the checking: every company, against the user's own profile, with evidence a person can click.

It checks a list. It never builds one, and it never adds companies.

## The run

Six stages, in order. Each needs the one before, so never skip ahead.

1. **Profile.** An interview builds the profile every company is checked against. The user approves it.
2. **Load.** A script reads the list, loads every website and splits the list into batches.
3. **Research.** Each batch is checked against the profile, with evidence from primary sources.
4. **Verify.** The script loads every page cited and checks each quote is on it, word for word.
5. **Re-check.** A separate checker re-checks every keep, and every drop the script could not confirm.
6. **Hand-back.** A report and two CSV files.

Read each reference file when its stage begins, not before, apart from the first check below. They are in this skill's folder, `${CLAUDE_SKILL_DIR}` (in a chat, the folder this file is in).

## Before you start

- **Check you can open this skill's files.** Every stage runs on them, not on this page. Open `references/profile.md` now with a tool that reads files. Stage 1 needs it next. Knowing its name from this page is not the same as opening it. If it will not open, list the folder this file is in, then stop here and tell the user, in one message, the one of these that fits. Run nothing from this page alone.
  - **The skill was saved without its files.** You can open files, and the folder holds no `references/` folder. Tell the user the skill was saved without its files, for example when a chat offered to save it to their account, so it cannot run in any chat. They should remove it under **Customize**, then **Skills**, and upload `check-account-list.zip` from the latest release in its place: https://github.com/scordsy/skills/releases/latest
  - **Anything else, such as no tool that opens files.** Tell the user this chat cannot open the skill's files, so the skill cannot run in it, and that it needs a normal chat (not an incognito one) with **Create and edit files** turned on, under **Settings**, then **Capabilities**.
- **Find today's date.** "Bought in the last five years" is worked out from it.
- **Any country.** The checks are the same everywhere. How much can be proven depends on each country's free company register, listed in `references/registers.md`.
- **Work out which route you are on.** It depends on what you can do, not on which app you are in.
  - **The subagent route**, where you can launch subagents with the Agent tool and run Python: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The full version below.
  - **The chat route**, in a chat that cannot launch subagents: follow the "In a chat" notes at each stage. The run needs web search. If you cannot search the web, say so and stop.
- **The list comes after the profile.** Ask for it at Stage 2, once the profile is approved, never alongside a profile question. The profile is built from the user's answers alone. If the user has already given the list, say you will check it once the profile is agreed, and take nothing from it for the profile: no competitor, no customer, no draft.
- **Make the run folder** once the profile has a short name: `check-account-list/<YYYY-MM-DD>-<short-name>/` under the current working directory, with `working/` and `check-in/` inside. Use absolute paths whenever you brief a subagent.
- **Tell the user what to expect** in one line: a few questions to build the profile, then the list (up to 50 companies on the subagent route, 15 on the chat route), then the checks, which take a while. From the tests, each batch of 10 companies takes a researcher 10 minutes or more.

## Stage 1: Profile

Follow `references/profile.md`: one numbered question per message and nothing else in it, drafts before questions, "not sure" always accepted, and competitors and customers only from the user's answers. End with `profile.md` in the run folder, shown to the user. **Check nothing before the user approves it.**

**In a chat:** show the profile in your reply instead of writing a file.

## Stage 2: Load

**Get the list**, in a message of its own, unless the user has already given it. A `.csv`, `.xlsx`, `.md` or `.txt` file, or a paste. A company name per row is enough; a website column helps. For `.xls`, `.numbers` or PDF, ask for a `.csv` or `.xlsx` export, or a paste. Save a pasted list to `working/list.txt`.

**Size.** Up to 50 companies a run on the subagent route, 15 on the chat route. For more, say so and offer to run it in parts.

```
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" load "<list file>" "<run folder>/companies.md"
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" web "<run folder>/companies.md" "<run folder>/web.md"
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" split "<run folder>/companies.md" "<run folder>/web.md" "<run folder>/working"
```

Show the user, in one or two lines, what `load` and `web` printed: how many companies, how many websites load, any that redirect to another domain, and any likely duplicates. If the profile names a customers file, copy it into the run folder as `customers.csv`. If the company names look wrong (a header read as a company, two columns run together), say so and ask before going on.

**In a chat:** with code execution on, save the list to a file and run the same three commands. If `web` cannot reach the internet from the code sandbox, load each website with your own web tools instead and say so in one line. Without code execution, number the companies yourself (A01, A02 and so on).

## Stage 3: Research

Launch one **fresh general-purpose subagent** per batch file, never a fork (a fork would carry this conversation). Launch them **all in one message** so they run in parallel. Brief each with this, filling in the angle brackets:

```
You are checking one batch of companies on a target account list.
Read these files first, in this order:
1. ${CLAUDE_SKILL_DIR}/references/research.md
2. ${CLAUDE_SKILL_DIR}/references/registers.md
3. ${CLAUDE_SKILL_DIR}/references/record-format.md
4. <run folder>/profile.md
5. <run folder>/working/batch-<n>.md
6. <run folder>/customers.csv, if the profile names one
The skill folder is ${CLAUDE_SKILL_DIR}.
Write one record per company to <run folder>/working/research-<n>.md.
Do not launch further agents.
Reply with one line only: the number of records and the count of each verdict.
```

Tell the user the batches are running and roughly how long they take. Do not read the research files into this conversation: the script reads them.

**In a chat:** read `references/research.md`, `references/registers.md` and `references/record-format.md` and research the companies yourself, in batches of 5, telling the user which batch you are on. Keep every record in the record format, and save them to `working/research-1.md` if you can create files.

## Stage 4: Verify

```
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" verify "<run folder>" "<run folder>"/working/research-*.md
```

It prints how many quotes it confirmed, how many sit in PDFs it cannot read, and how many pages would not load. Then any problems: a record in the wrong shape, a keep missing evidence for a check, a quote not on the page it cites. If there are problems, launch one fresh researcher per affected file with the same brief plus the problems, told to fix only what the problems name, and verify again. If problems remain, carry on, and list them at the top of the hand-back.

**In a chat:** run the same command if code execution can reach the web. If it cannot, say in one line at the top of the hand-back that quotes were not checked by code.

## Stage 5: Re-check

Read `references/checker.md`, but only to brief the checker. **Never check the records yourself.** You have seen how they were found, which is exactly what the re-check must not know.

For each research file, copy the records that need a check, and only those, into `check-in/`, which holds nothing else, plus the profile:

```
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" strip "<run folder>" "<run folder>/working/research-<n>.md" "<run folder>/check-in/to-check-<n>.md"
cp "<run folder>/profile.md" "<run folder>/check-in/profile.md"
cp "<run folder>/customers.csv" "<run folder>/check-in/customers.csv"   # only if there is one
```

`strip` sends every keep and every drop whose evidence the script could not confirm, with the claims only: never the reasons or the evidence. Note the count it prints. If it is 0, that batch needs no checker. Otherwise launch one **fresh general-purpose subagent** per file, all in one message, never forks, briefed with this:

```
You are checking companies on a target account list that someone else researched.
Read these files first, in this order:
1. ${CLAUDE_SKILL_DIR}/references/checker.md
2. ${CLAUDE_SKILL_DIR}/references/research.md
3. ${CLAUDE_SKILL_DIR}/references/registers.md
4. ${CLAUDE_SKILL_DIR}/references/record-format.md
5. <run folder>/check-in/profile.md
6. <run folder>/check-in/to-check-<n>.md
7. <run folder>/check-in/customers.csv, if the profile names one
Do not list or open anything else in the run folder.
The skill folder is ${CLAUDE_SKILL_DIR}.
Write every record, rewritten as checker.md says, to <run folder>/working/check-<n>.md.
Do not launch further agents.
Reply with one line only: how many you checked, agreed with and changed.
```

Then verify the checkers' files the same way as Stage 4, with `working/check-*.md`.

**In a chat:** you cannot check your own research honestly, so the user carries it to a fresh chat. Build one block that starts with this line:

> You are the checker in a check-account-list run. Do not start the check-account-list skill or any other skill. Follow only the instructions below.

Then the full text of `references/checker.md`, `references/research.md`, `references/registers.md` and `references/record-format.md`, then the profile and any customers list, then the records that need a re-check (every keep, and every drop resting on evidence you could not confirm), with the claims only and no reasons or evidence. With code execution, run `verify` and `strip` as on the subagent route and paste the `to-check` file; without it, copy the claim lines by hand. Tell the user: "Open a new chat with web search on (an incognito chat is best, so it cannot see this one), paste everything in the box below, and paste its answer back here. A check in this chat would be me marking my own homework." When the answer comes back, count its records against the number you sent and ask for any missing ones. If you can create files, save it as `working/check-1.md` and run `verify` on it as on the subagent route. If the user declines the re-check, carry on, and follow the "Unchecked" rule in `references/hand-back.md`.

## Stage 6: Hand-back

```
python3 "${CLAUDE_SKILL_DIR}/scripts/accounts.py" report "<run folder>"
```

Then read `references/hand-back.md` and finish as it says.

**In a chat:** run the same command if you saved the files. Otherwise count the verdicts and problems by hand, twice. Then show one document holding the counts, the check-by-hand list and every company, and offer the CSV as a file if you can create one.

## Throughout

- **Only primary sources are evidence**: the company's own site, the official company register for its country, and the buyer's or the company's own announcement of a takeover. Listing sites, LinkedIn and search summaries can point the way, never prove anything.
- **Use only your built-in web search and page reading**, plus `curl` and the script. Do not use third-party search, scraping or enrichment tools, even if they are connected.
- **Read registers the way a person would**: a few pages per company, never in bulk. If a register refuses or asks you to slow down, stop using it. Nobody should be blocked because of this skill.
- **Never guess a fact.** `unverified` is a correct answer, and a reason to check by hand.
- **Never add a company**, suggest a replacement, or contact anyone.
- **Write in the user's language and spelling.**
- **Keep the user posted** with one line at each stage. The research and the re-check take a while.
