# Glossary

The words these skills use in their instructions, their output and their docs. One meaning each within a skill. Where two skills share a word, such as verdict, each skill's section gives its meaning there. When a skill's output uses one of these words, it means exactly this.

## find-events

**Brief**:
The written summary of the interview: every answer, each assumption marked, the date window and the proposed lanes. Nothing is searched until the user approves it.
_Avoid_: profile, requirements

**Assumption**:
An answer the skill filled in because the user said "not sure" or did not know. Always marked in the brief so the user can see every guess.
_Avoid_: default (that is how the value was chosen, not what it is)

**Category**:
How an organiser is likely to classify the user when pricing tickets or deciding who gets in: practitioner, vendor, agency, consultancy or other. Drafted in the interview, confirmed by the user.
_Avoid_: persona, segment

**Right people**:
The people the user wants to meet, as confirmed in the brief. The R in the score.
_Avoid_: ICP, audience, buyers (unless the user's right people are buyers)

**Lane**:
One slice of the search, by region or by event type, researched on its own so no ground is covered twice. Up to 4 per run by default.
_Avoid_: agent, track, stream

**Record**:
One event, written in the record format. A record has exactly one verdict.
_Avoid_: entry, listing, result

**Organiser's page**:
The event organiser's own website, and the page for the specific edition where one exists. The only source that counts.
_Avoid_: official listing (a listing is never the organiser's page)

**Listing site**:
Any page that lists other people's events: aggregators, ticket resellers, "top events" posts, directories. Useful for finding events. Never a source for a fact.
_Avoid_: source

**Edition**:
One occurrence of a recurring event, such as the 2027 edition.
_Avoid_: instance, year

**Inheritance**:
Last year's date or price, repeated by a listing site and written down as this year's. The commonest error in event research.
_Avoid_: stale data

**Discovery**:
The stage where the lanes search and write records.
_Avoid_: calling this stage "research" (the whole skill is research)

**Check**:
The stage where a separate pass tries to prove each record wrong against the organiser's page. Done by the checker.
_Avoid_: verification, review, QA

**Checker**:
Whatever runs the check: a subagent in Claude Code, a fresh chat in Claude.ai. Never the same context that found the record.

**Verdict**:
What the check concludes about a record. Exactly one of:
- **confirmed**: the organiser's page supports the dates and the substance.
- **pattern-estimate**: the event is real and recurring, but the next edition is not announced. The record says what the pattern rests on.
- **dead**: it is not running, with the evidence.
- **unverifiable**: it could not be established either way, and the record says what could not be seen.
_Avoid_: status, valid, verified

**Correction**:
A field the checker changed, stated openly in the record's check notes. Each is one of seven types: **date-wrong**, **price-wrong**, **dead-not-caught**, **gate-missed**, **room-overstated**, **name-wrong**, and **detail-wrong** for any other stated fact that was wrong. A detail filled in where the record said nothing is not a correction, except a missed gate or a missing price for the user's category.
_Avoid_: fix, edit, error (an error is what a correction corrects)

**Gate**:
An admission rule, such as "free for in-house teams only, agencies excluded".
_Avoid_: restriction, eligibility

**Listed price**:
What the organiser publishes, in the organiser's currency, with where it was seen.

**Your price**:
The tier that applies to the user's category, or "not published". Often not the listed price.

**Score**:
2R + A + V + L + B, out of 15: right people (counted double), conversation access, value for money, learning, bonus.

**Tier**:
Where a score puts an event: **book** (12 or more), **consider** (9 to 11), **skip** (below 9).
_Avoid_: rating, rank

**Trip**:
Events in the same city in the same week, grouped so one journey covers them.

**Shortlist**:
The hand-back: `shortlist.md`, ordered as the spec sets out.
_Avoid_: report, calendar

## check-call-summary

**Transcript**:
The record of what was said on the call, line by line, with speaker labels. The only source a claim is checked against.
_Avoid_: recording (the skill never hears audio), notes

**Summary**:
Any written account of the call being checked: an AI summary, a CRM note, a follow-up email, meeting notes.
_Avoid_: recap, minutes

**Numbered transcript**:
`transcript-lines.md`: the transcript with every line numbered, `[L42] 00:12:03 Priya: text`. Every quote cites these numbers.

**Claim**:
One fact from a summary. A summary line often holds several claims.
_Avoid_: point, bullet, statement

**Quote**:
The words from the numbered transcript that a claim rests on, with the lines they are on and the speaker. Checked word for word by the script.
_Avoid_: evidence (a quote is the evidence; say which)

**Verdict**:
What the check concludes about a claim. Exactly one of:
- **said**: the transcript says it.
- **inferred**: not said in so many words, but reasonably drawn from what was.
- **not-in-transcript**: nothing in the transcript supports it.
- **contradicted**: the transcript says otherwise.

A verdict says where a claim comes from. Whether it went wrong is the failure type's job, so a claim can be inferred and overstated at once.

**Failure type**:
A way the claim went wrong. A claim carries none, one or several of: **wrong-speaker**, **tone-read-as-sincere**, **intention-as-done**, **owner-or-date-wrong**, **made-up-detail**, **overstated**. The seventh, **left-out**, belongs to a key fact the summary does not carry.
_Avoid_: error, issue, correction

**Key facts**:
What a CRM record depends on, listed from the transcript by a reader that never sees the summary. Each is one kind: next-step, commitment, date, number, who-decides, objection, competitor.
_Avoid_: highlights, takeaways, action items

**Reader**:
Whatever lists the key facts and doubtful labels: a subagent in Claude Code, the first part of the chat in Claude.ai. Never sees a summary before its list is written.

**Checker**:
Whatever splits a summary into claims and checks each one: a subagent per summary in Claude Code, the chat itself in Claude.ai.

**Doubtful label**:
A transcript line whose content argues with its speaker label. Flagged with who it more likely was and why, never corrected.
_Avoid_: wrong label (the skill cannot hear the audio, so it cannot know)

**Confirm list**:
The part of the report to settle with someone who was on the call before saving: owners and dates of next steps and commitments, claims resting on a doubtful label, and claims flagged tone-read-as-sincere.

**Report**:
`check.md`: the counts, the confirm list, the doubtful labels, every claim and the key facts.
_Avoid_: audit, review

**Corrected draft**:
`corrected.md`: each summary rewritten with removed text struck through, added text in bold, and the line number behind every change.
