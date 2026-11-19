# 17. A skill stops when it cannot open its own files

**Status:** accepted, 19 November 2026

## Context

Each skill's `SKILL.md` is a map. The work lives in its reference files and scripts, read at each stage. On 19 November 2026 find-events was run in an incognito chat on Claude.ai, which had no tool to open a file or run code. It did not say so. It ran on `SKILL.md` alone: it asked 3 of its 8 interview questions, left Category, Role and Assumptions out of the brief, proposed 5 lanes where the cap is 4, and wrote its own checker instructions. The same skill, in a normal chat with **Create and edit files** on, opened its files and ran as written.

check-call-summary already stopped when it could not run Python. find-events and check-account-list had no such rule.

## Decision

Before anything else, every skill opens one of its own files with a real tool: find-events opens `references/interview.md`, check-account-list opens `references/profile.md`, and check-call-summary runs its script with no arguments, which prints how to use it. Each is the first thing the skill needs anyway. If the skill has no tool that opens files or runs code, or the file will not open, it tells the user in one message that it cannot run in this chat, that it needs a normal chat (not an incognito one) with **Create and edit files** on, and stops. It runs nothing from `SKILL.md` alone.

The paste-in check that find-events and check-account-list hand to a fresh chat is not a skill run. The block carries its own instructions, so it still works in an incognito chat, which is still the best place for it, because that chat cannot see the one that did the research.

## Why

A skill that quietly runs from its summary looks like a working run and is not one: the questions, limits and checker instructions it drops are the ones the method depends on. Stopping costs the user one switch of chat. Asking for a real open, rather than a statement that the files are there, matters because the incognito chat listed the skill's files from their names in `SKILL.md` without opening any.
