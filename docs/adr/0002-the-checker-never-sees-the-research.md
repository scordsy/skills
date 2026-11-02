# 2. The checker never sees how a record was found

**Status:** accepted, 2 November 2026

## Context

Anything that checks its own work tends to confirm whatever it found first. In event research the usual error is not invention but inheritance: last year's date, repeated by a listing site, looks completely normal, and the context that wrote it down has already accepted it.

## Decision

The check runs in a separate context that receives only the records, the check instructions, and three facts from the brief: the user's category (to check prices and gates), the date window (to check editions) and who they want to meet (to check who is in the room). It is never told how the records were found. In Claude Code that is a subagent. In Claude.ai and Claude Desktop, which have no subagents, the skill hands the user a prompt to paste into a fresh chat, and the checked records are pasted back.

The checker is told each record is wrong until the organiser's own page says otherwise, and that inventing a correction is the same failure as missing one.

## Why

The separation is the method. Without it the check is a second read by the same reader. The fresh-chat step in Claude.ai costs the user one paste, which is cheaper than a shortlist nobody should trust.
