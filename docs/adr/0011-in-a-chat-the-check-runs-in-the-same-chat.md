# 11. In a chat, the check runs in the same chat

**Status:** accepted, 4 November 2026. Amended 19 November 2026: this covers the chat route, a chat that cannot launch subagents. A Claude.ai or Claude Desktop chat that can launch them runs fresh checkers, as Claude Code does ([ADR 0019](0019-the-route-follows-what-the-chat-can-do.md)).

## Context

find-events hands its check to a fresh chat in Claude.ai and Claude Desktop, because a check in the chat that did the research is the research marking its own homework ([ADR 0002](0002-the-checker-never-sees-the-research.md)). check-call-summary could do the same, at the cost of two pastes per summary.

## Decision

In a chat, `check-call-summary` checks each summary in the same chat, after the key facts are written down and verified. The hand-back says in one line that the check ran in the same chat and is weaker for it. In Claude Code every checker is a fresh subagent, as before.

## Why

The risk is different. find-events' checker has to go and find the facts, so a checker that already believes the research can look in the wrong place and agree with it. Here the evidence is fixed: one transcript, and a script that confirms every quote is on the line it cites, word for word ([ADR 0008](0008-quotes-are-checked-by-code.md)). What a same-chat check could bend is the judgement (whether a claim is overstated, whether a fact mattered), and the key facts are listed and verified before the summary is read ([ADR 0009](0009-key-facts-are-read-blind.md)). Two pastes per summary, each carrying the whole transcript, would cost more than that weakness, so the skill names it instead of hiding it.
