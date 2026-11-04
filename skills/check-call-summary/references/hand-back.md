# Hand-back

Two files: `check.md`, which the script builds, and `corrected.md`, which you write.

## check.md

Built by the `report` command, in this order:

1. Any claims whose quote could not be verified, to check by hand. Only present when there are some.
2. Counts: claims, verdicts and failure types, one column per summary. `left-out` counts key facts the summary does not carry.
3. **Confirm with a person before saving:** every next step and commitment (owner and date) with how each summary carried it, every key fact or claim resting on a doubtful label, every claim flagged `tone-read-as-sincere`, and every claim flagged `intention-as-done` or `owner-or-date-wrong`.
4. Doubtful labels.
5. Each summary's claims, in full.
6. The key facts, and how each summary carried them.

Do not reorder it or change what the script wrote. The only thing you add is one line at the very top for each of these that applies: a problem the verify stage left standing; in a chat, that the check ran in the same chat; in a chat, that the key facts were listed with the summary already in the chat.

## corrected.md

Each summary, rewritten so it could be saved, with every change visible. One section per summary, headed `# <name>`, so the summary's own headings sit under it.

- **Keep everything the check found sound,** word for word.
- **Removed text** is struck through: `~~sent the pricing~~`.
- **Added text** is in bold, followed by the line it comes from, outside the bold: `**will send the pricing by Friday** (L118)`.
- **A claim that is not in the transcript** is struck through, with nothing added. It is the one change with no line behind it, because nothing in the transcript supports it.
- **A contradicted or failed claim** is struck through and replaced with what the transcript says, in bold, with its line. This includes next steps: a next step the summary got wrong is corrected like any other claim.
- **A claim flagged `tone-read-as-sincere`, or resting on a doubtful label,** is not changed. Mark it `[confirm: <reason>]` at the end, for example `[confirm: rests on a doubtful label, L57]` or `[confirm: may have been said for effect, L203]`. Only someone who was on the call can settle these.
- **A left-out key fact** is added in bold with its line, on the line or field it belongs with if there is one, otherwise at the end of the section it belongs in (usually next steps). If it rests on a doubtful label, mark it `[confirm: ...]` too.
- **Use the transcript's words for anything you add.** Keep its hedges ("would rather", "roughly", "probably"), and add no unit, currency or date it does not say.

Every change comes from a claim or a key fact in `check.md`. Nothing checks this file, so add nothing the check does not support: no new facts, no rewording of sound lines for style, no tidying. When it is written, read every change back against its claim or key fact, and against the transcript line it cites, and remove or fix any that the check and the line do not support.

The confirm list in `check.md` is where owners and dates of next steps get confirmed. `corrected.md` does not mark every next step: it fixes the wrong ones and marks only what turns on a label or on tone.

End the file with one line: "Checked against the transcript by check-call-summary. Confirm the marked lines, and the confirm list in check.md, with someone who was on the call before saving."
