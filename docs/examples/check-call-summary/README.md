# check-call-summary: example run

A real run of the skill on a made-up call. Everything in it is fictional: Larkspur, Quillmarsh Home Insurance, Callgrade, the people and the numbers. The two summaries were written for this example, to look like a notetaker's bullet points and a rep's CRM note.

| File | What it is |
|---|---|
| `transcript.txt` | The call, in the export style that puts each speaker and time on a line of their own |
| `summaries/` | The two summaries, as given to the skill |
| `transcript-lines.md` | The transcript as numbered lines, written by the script |
| `key-facts.md` | The reader's key facts and doubtful labels, written before it saw either summary |
| `working/` | Each checker's file, as written |
| `check.md` | The report, built by the script |
| `corrected.md` | Both summaries with every change marked |

Run on 4 November 2026 in Claude Code: 3 subagents, 333,000 tokens. The reader took 49 seconds (105,357 tokens). The two checkers ran in parallel and took 103 seconds (notetaker, 115,424 tokens) and 82 seconds (crm-note, 112,203 tokens). Every quote verified on the first pass.

The companies were first written as Kestrel and Cartwheel, which turned out to be real company names, so they were renamed after the run. The names changed in every file at once. The run itself did not.
