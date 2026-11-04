# 12. Reading a call from a connected call recorder

**Status:** proposed, 4 November 2026. Not in v1. Accept it only once the conditions below are met and it has been run on a real call through at least one connector.

## Context

Version 1 works from an exported file or a paste. Many call recorders now have Claude connectors, among them Fireflies, Otter, Fathom, Granola, tl;dv, Grain, Read.ai and Zoom, and several return both the transcript and the recorder's own AI summary. That is exactly the pair the skill checks, with nothing to export or paste. The user connects their own account in Claude, so the skill would never hold a key, and [ADR 0004](0004-no-api-keys.md) is not the obstacle [ADR 0010](0010-it-checks-and-never-writes.md) assumed.

A connector version was drafted and reviewed on 4 November 2026, then taken out of v1 because it had never been run on a real call and the review found risks the skill cannot yet rule out.

## Proposed decision

When the user names a call and a recorder's connector is connected, fetch the transcript through it and number it; fetch the recorder's own summary only when the check begins, never before the key facts are written ([ADR 0009](0009-key-facts-are-read-blind.md)). Connectors are read-only: nothing is written, shared or deleted. The hand-back says when the transcript came through a connector.

## Conditions before it is accepted

- **The summary must never reach the reader.** Some connectors have a tool that returns the transcript together with the summary, action items and keywords. The skill must use the transcript-only tool where there is one, keep only the conversation when there is not, and say in the hand-back when it could not.
- **No retyping a long transcript.** Copying a connector's response into a file by hand can drift on a long call without the quote check noticing. Where the environment saves the full response to a file, copy that file; otherwise say the transcript is a copy.
- **Metadata is not speech.** Titles, organisers and durations in a response must not be numbered as turns.
- **A response the parser cannot read** (one long string, an unknown shape) needs a stated next step, not a dead end.
- **The README names only connectors that have been run.**

## Why

Checking a recorder's own summary against its own transcript is the scenario the skill exists for, so this is the strongest next step. Shipping it untested would break the repo's promise that every skill can be checked, so it waits.
