# 19. The route follows what the chat can do, not the app

**Status:** accepted, 19 November 2026

## Context

Every skill was written with two versions: the full one for Claude Code, where fresh subagents do the separate jobs, and a fallback for Claude.ai and Claude Desktop, which were taken to have no subagents. [ADR 0002](0002-the-checker-never-sees-the-research.md) and [ADR 0011](0011-in-a-chat-the-check-runs-in-the-same-chat.md) were written on that basis.

On 19 November 2026 all three skills were run on Claude.ai, in normal chats with memory off, on my account. Every run launched subagents and followed the full version: find-events ran 2 finders and 2 fresh checkers whose briefs match `SKILL.md`'s templates word for word, check-call-summary ran a separate reader and a fresh checker, and check-account-list ran 2 research batches and separate checkers. One account is not proof that every chat can, and the fallback has still never been run in a chat whose files were readable.

## Decision

The skills name two routes and pick one by what the chat can do:

- **The subagent route**, wherever subagents can be launched: always in Claude Code, and in some Claude.ai and Claude Desktop chats. The full version.
- **The chat route**, in a chat that cannot launch them: the "In a chat" notes at each stage, as before.

The docs say both routes exist and which route each test covered. They do not claim either that chats have no subagents or that every chat has them.

## Why

The separation that makes the check worth having is the same on either route: a fresh subagent where one can be launched, and a fresh chat the user pastes into, or a stated weaker check, where not. Routing by what the chat can do means a chat that can launch subagents gets the stronger version, and one that cannot still gets an honest one.
