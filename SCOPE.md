# Scope

What these skills do, and what they deliberately leave out. Issues and pull requests are judged against this file.

## In

- Small skills that do one job you can check.
- Skills that run on the assistant's own tools. No API keys, no paid services, no accounts to create.
- Claude Code first. Claude.ai and Claude Desktop where the skill can work honestly without subagents, with the difference stated.

## find-events

**In:** one full run, start to finish. Interview, brief, discovery, check, score, shortlist. Any kind of event, anywhere, for anyone who knows (or can be helped to say) who they want to meet.

**Out, on purpose:**

- **Re-checking an old list.** Event dates go stale, so this is the strongest candidate for a later version. Not in v1.
- **Calendar export.** The shortlist is markdown with a link on every line. An `.ics` file adds a format to maintain for little gain.
- **Booking or registering.** The skill hands back what to check. Spending money stays with the person.
- **Contact lookups.** It finds rooms, not attendee lists.
- **Paid data sources.** Event databases and enrichment tools are out, for the same reason as API keys.
- **Agents other than Claude.** Not tested, so not claimed.

## check-call-summary

**In:** one call at a time. A transcript as pasted text, `.txt`, `.md`, `.vtt` or `.srt`, and one or more summaries of that call. A report and a corrected draft for each summary.

**Out, on purpose:**

- **Writing summaries.** Other tools do that, and a skill that writes and checks the same summary is marking its own homework. See [ADR 0010](docs/adr/0010-it-checks-and-never-writes.md).
- **Reading from a call recorder or writing to a CRM.** Both need connectors and keys.
- **Audio.** It works from the transcript. It cannot hear who spoke, which is why labels are flagged, never fixed.
- **Many calls in one go.** One call per run.
- **Transcripts in other languages.** Not tested, so not claimed.

