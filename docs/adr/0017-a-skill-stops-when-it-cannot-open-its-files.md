# 17. A skill stops when it cannot open its own files

**Status:** accepted, 19 November 2026

## Context

Each skill's `SKILL.md` is a map. The work lives in its reference files and scripts, read at each stage. On 19 November 2026 find-events was run in an incognito chat on Claude.ai, which had no tool to open a file or run code. It did not say so. It ran on `SKILL.md` alone: it asked 3 of its 8 interview questions, left Category, Role and Assumptions out of the brief, proposed 5 lanes where the cap is 4, and wrote its own checker instructions. The same skill, in a normal chat with **Create and edit files** on, opened its files and ran as written.

check-call-summary already stopped when it could not run Python. find-events and check-account-list had no such rule.

## Decision

Before anything else, every skill opens one of its own files with a real tool: find-events opens `references/interview.md`, check-account-list opens `references/profile.md`, and check-call-summary runs its script with no arguments, which prints how to use it. Each is the first thing the skill needs anyway. If the skill has no tool that opens files or runs code, or the file will not open, it tells the user in one message that it cannot run in this chat, that it needs a normal chat (not an incognito one) with **Create and edit files** on, and stops. It runs nothing from `SKILL.md` alone.

The paste-in check that find-events and check-account-list hand to a fresh chat is not a skill run. The block carries its own instructions, so it still works in an incognito chat, which is still the best place for it, because that chat cannot see the one that did the research.

check-claims, added on 25 November 2026, follows the same rule: it runs its script with no arguments, as check-call-summary does, and stops if the script does not run.

On 26 November 2026 a test found a second way to fail. In a Claude.ai or Claude Desktop chat, Claude may offer to save a skill to the user's account. That saves `SKILL.md` alone, with no `references/` or `scripts/`. The first check fails, as it should, but the stop message sent the user to turn on **Create and edit files**, which cannot help, because the files were never installed. So when the first check fails, every skill now lists its own folder before it stops. If a tool works and the folder holds no `references/` (or `scripts/` for the two skills whose first check runs a script), the message says the skill was saved without its files, and tells the user to remove it and upload the skill's zip from the latest release, under **Customize**, then **Skills**. Anything else gets the message above. The case rests on what the listing shows, because a failed open alone cannot tell the two apart: a wrong path fails the same way as a missing file.

## Why

A skill that quietly runs from its summary looks like a working run and is not one: the questions, limits and checker instructions it drops are the ones the method depends on. Stopping costs the user one switch of chat. Asking for a real open, rather than a statement that the files are there, matters because the incognito chat listed the skill's files from their names in `SKILL.md` without opening any.
