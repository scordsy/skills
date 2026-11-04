# 9. The key facts are listed before the summary is read

**Status:** accepted, 4 November 2026

## Context

The most expensive summary error is an omission: the thing that would have changed the deal is simply not there. A reader who has already seen the summary judges the transcript through it, and tends to agree that what the summary left out did not matter. "Did it miss anything important?" invites that.

## Decision

A separate pass reads only the numbered transcript and lists the key facts against a fixed set of kinds (next steps, commitments, dates, numbers, who decides, objections, competitors), plus any doubtful speaker labels. It never sees the summary. In Claude Code it is a fresh subagent reading from a folder that holds only the transcript. In Claude.ai and Claude Desktop, the skill asks for the transcript first and writes the list before it asks for the summary.

The checker then marks each key fact as carried, carried wrongly, or missing.

## Why

Same principle as [ADR 0002](0002-the-checker-never-sees-the-research.md): the separation is the method. A fixed list makes the omission check repeatable, and reading blind stops the summary deciding what mattered. The chat version is weaker than a separate context, since the same chat later sees the summary, but the list is written down before it does, so it cannot be bent to fit.
