# Scope

What these skills do, and what they deliberately leave out. Issues and pull requests are judged against this file.

## In

- Small skills that do one job you can check.
- Skills that run on the assistant's own tools. No API keys, no paid services, no accounts to create.
- Claude.ai and Claude Desktop first, because the readers are sales and marketing people using the Claude app. Claude Code too. A chat that can launch subagents runs the full version, as Claude Code does, and one that cannot runs a version that works honestly without them, with the difference stated. A chat that cannot open the skill's files, such as an incognito chat, gets a clear stop, never a quiet run from the summary.

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

**In:** one call at a time. A transcript as pasted text, `.txt`, `.md`, `.vtt`, `.srt`, `.docx` or `.json`, and one or more summaries of that call, including the recorder's own, copied or exported. A report and a corrected draft for each summary.

**Out, on purpose:**

- **Writing summaries.** Other tools do that, and a skill that writes and checks the same summary is marking its own homework. See [ADR 0010](docs/adr/0010-it-checks-and-never-writes.md).
- **Reading from a call recorder through a connector.** The strongest candidate for the next version, proposed in [ADR 0012](docs/adr/0012-it-reads-from-a-connected-call-recorder.md). Not in v1 because it has not been run on a real call.
- **Writing to a recorder or a CRM, or reading a CRM.**
- **PDF.** It cannot be read reliably with the standard library. Export another format, or paste.
- **Audio.** It works from the transcript. It cannot hear who spoke, which is why labels are flagged, never fixed.
- **Many calls in one go.** One call per run.
- **Transcripts in other languages.** Not tested, so not claimed.

## check-account-list

**In:** one list of up to 50 companies (15 on the chat route), pasted or as `.csv`, `.xlsx`, `.md` or `.txt`, checked against a profile the user approves. A report and two CSVs.

**Out, on purpose:**

- **Building or extending a list.** It never adds a company or suggests a replacement. See [ADR 0015](docs/adr/0015-it-checks-lists-and-never-adds-to-them.md).
- **Contacts, email addresses and enrichment.** It checks companies, not people.
- **Ranking or scoring the keeps.** A keep fits the profile; which to call first is the user's call.
- **Paid registers, register APIs that need a key or payment, and bulk reads.** Registers are read the way a person would, a few pages per company, and the script loads only the register pages a record cites, to check the quotes. Where a country's free register does not give a fact, it is marked unverified. See [ADR 0013](docs/adr/0013-any-country-registers-read-by-hand.md).
- **Paid data sources, enrichment tools and API keys.**
- **Reading or writing a CRM.**
- **Agents other than Claude.** Not tested, so not claimed.
