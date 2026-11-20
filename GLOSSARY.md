# Glossary

The words these skills use in their instructions, their output and their docs. One meaning each within a skill. Where two skills share a word, such as verdict, each skill's section gives its meaning there. When a skill's output uses one of these words, it means exactly this.

## Every skill

**Subagent route**:
The full version of a skill, where fresh subagents do the separate jobs. Taken wherever subagents can be launched: always in Claude Code, and in some Claude.ai and Claude Desktop chats.
_Avoid_: Claude Code version (the route follows what the chat can do, not the app)

**Chat route**:
The version for a chat that cannot launch subagents: the "In a chat" notes at each stage.
_Avoid_: Claude.ai version

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
Whatever runs the check: a fresh subagent on the subagent route, a fresh chat the user pastes into on the chat route. Never the same context that found the record.

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
Whatever lists the key facts and doubtful labels: a fresh subagent on the subagent route, the first part of the chat on the chat route. Never sees a summary before its list is written.

**Checker**:
Whatever splits a summary into claims and checks each one: a fresh subagent per summary on the subagent route, the chat itself on the chat route.

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

## check-account-list

**List**:
The companies the user wants checked, as given: a paste, a CSV, an Excel sheet or a markdown table. Each company gets an ID, `A01` onwards.
_Avoid_: leads, prospects, accounts (unless the user says so)

**Profile**:
The approved summary of the interview: what the user sells, their best customers and why, the hard limits, and who to drop on sight. Every check measures against it. Nothing is checked before the user approves it.
_Avoid_: ICP, brief, persona

**Best customer**:
A customer the user wants the list to look like. One to three, named by the user.

**Hard limits**:
The parts of the profile a company must meet: countries, staff range, buyer, and whether a company owned by a larger group counts.

**Check**:
One of the six things looked at for every company: website, still trading, owner, size, fit, conflicts.
_Avoid_: test, criterion

**Primary source**:
The company's own website, the official company register for its country, or the buyer's or company's own announcement of a takeover. The only evidence that counts.
_Avoid_: source (a listing site is a source of leads, never of facts)

**Evidence**:
A primary source's web address and two or more words copied exactly from it, recorded against one check. The script confirms the words are on the page.
_Avoid_: proof, citation

**Record**:
One company, in the record format: what each check found, the verdict, the problems, the reason and the evidence.

**Verdict**:
What the research, or the checker's re-check, concludes about a company. Exactly one of:
- **keep**: every check passed, with evidence for website, still trading, owner, size and fit.
- **drop**: at least one problem type, with evidence.
- **check-by-hand**: the evidence is missing or contradicts itself, and no problem is proven.
_Avoid_: status, score, valid

**Unverified**:
No primary source gives the fact. Never a problem on its own; a reason to check by hand.

**Problem type**:
Why a company is dropped. One or several of: **wrong-website**, **closed**, **bought**, **not-in-country**, **wrong-size**, **wrong-fit**, **competitor**, **customer**, **duplicate**. **Bought** means a takeover, merger or change of control in the last five years. When the profile does not want group-owned companies, it also covers a company owned by a trading group, however long ago. Ownership by an investor older than five years is noted but is not a problem. **Customer** includes a company owned by the same group as a best customer or an existing customer.
_Avoid_: error, issue, flag

**Name trap**:
A company on a register with the same or a similar name as the one on the list, but unrelated. Caught by matching the website, address or directors, never the name alone.

**Researcher**:
Whatever writes the first records: a fresh subagent per batch on the subagent route, the chat itself on the chat route.

**Checker**:
Whatever re-checks every keep and every drop the script could not confirm: a fresh subagent per batch on the subagent route, a fresh chat the user pastes into on the chat route. Sees the claims and verdicts, never the reasons or the evidence.

**Re-check**:
The stage where the checker tries to prove the first pass wrong. Not to be confused with a check, which is one of the six things looked at for every company.

**Report**:
`checks.md`, with `checked.csv` (every company) and `keepers.csv` (the keeps).
