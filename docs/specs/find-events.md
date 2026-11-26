# find-events: spec

The agreed design for `find-events`, settled in a design interview on 2 November 2026. Reviews check the skill against this file. Change it only on a new decision, and say why in a decision record.

## What it does

Finds events worth attending to meet a particular kind of person, and checks every one against the organiser's own page before you see it.

1. **Interview.** Builds a brief from your answers. You approve it before anything is searched.
2. **Discovery.** Research lanes look for events that fit the brief.
3. **Check.** A separate pass tries to prove each record wrong against the organiser's own page.
4. **Score.** Every event that survives is scored out of 15 and sorted into book, consider or skip.
5. **Hand-back.** A shortlist with the organiser's link on every line.

## Who it's for

Anyone choosing which events to attend to meet a particular kind of person. The README frames it around meeting B2B buyers, but nothing in the skill assumes B2B. A music producer looking for labels runs the same five stages.

## Where it runs

- **First, on every route**, the skill opens `references/interview.md` with a real tool. If it cannot, it lists its own folder, stops and tells the user why. If it can open files and the folder holds no `references/`, the skill was saved without its files, for example from a chat's offer to save it, and the user removes it and uploads the zip from the latest release under Customize, then Skills. Otherwise this chat cannot open the skill's files, and the user needs a normal chat (not an incognito one) with Create and edit files on. It never runs from `SKILL.md` alone. See [ADR 0017](../adr/0017-a-skill-stops-when-it-cannot-open-its-files.md).
- **The route follows what the chat can do**, not the app ([ADR 0019](../adr/0019-the-route-follows-what-the-chat-can-do.md)).
- **The subagent route** is the full version, wherever subagents can be launched: always in Claude Code, and in some Claude.ai and Claude Desktop chats. Lanes run as parallel subagents. The checker is a separate, fresh subagent (never a fork) that never sees how a record was found: it reads only its own records file, from a folder that holds nothing else.
- **The chat route** is the fallback, in a chat that cannot launch subagents. Lanes run one after another in the same chat. At the check stage the skill hands over a prompt for the user to paste into a fresh chat, because a check in the same chat is the research marking its own homework. The user pastes the checked records back for scoring. If the user declines the check, the shortlist is marked unchecked at the top and carries no check counts.
- **Other agents** are not tested and not claimed.

## Stage 1: Interview

One question at a time: each message asks one of the numbered questions below and nothing else, with a question's own parts in one list. Push back on vague answers ("marketers" becomes which marketers, at what size of company, doing what). Where an answer can be drafted, offer the draft to confirm rather than a blank question: correcting is easier than writing. "Not sure" is always a valid answer. The skill then uses a sensible default and marks it as an assumption.

The questions, in order:

1. **Company website, or what you do in one line.** With a website, read the homepage and up to 3 more pages from the same site (about, customers or case studies, pricing). Draft what the company sells, who buys it, and the ticket category the user falls into: practitioner, vendor, agency, consultancy or other. Show the draft; the user corrects it. Without a website, draft the same from the one line. No LinkedIn pages, no enrichment tools, no reading the whole site.
2. **Your role.**
3. **Who you want to meet.** Drafted from the company answers where possible, and always confirmed out loud. A website shows who a company markets to, which is not always who its people want to meet, and this answer counts double in scoring.
4. **What a good event looks like.** Size, format, matchmaking, talks or conversation.
5. **What rules an event out.**
6. **Budget, and travel.** Ticket budget for the period, where you travel from, how far you will go, and whether one person or more is going.
7. **The dates.** The window to search.
8. **Events you already know or go to.** The search skips them and digs deeper.

The honesty rules are fixed, not asked.

### The brief

Written to `brief.md`. It shows every answer with each assumption marked, the date window, and up to 4 proposed research lanes (by region or event type), each with a line on why. Nothing is searched until the user approves or edits it.

## Stage 2: Discovery

- Up to 4 lanes, up to 10 records each: 40 records at most by default. A wider run only when the user asks for one.
- Fifteen well-checked records beat forty thin ones. A lane returns fewer records when fewer are worth it.
- Every lane gets the whole brief, not a task description, plus the honesty rules and the record format.
- Lanes skip the events the user already knows, and stay inside their own lane.
- Search uses the assistant's own built-in web search and page reading. No API keys, and no third-party search, scraping or enrichment tools even when they are connected. In Claude Code, `curl` with a normal browser identity is the fallback when an organiser's site blocks the fetcher.

### Honesty rules

1. Only the organiser's own page is a source. Listing sites, aggregators, "top events" posts and AI summaries are not.
2. If the next edition is not announced, say so. The verdict is pattern-estimate, with what the pattern rests on.
3. If an event looks dead, prove it either way.
4. If something cannot be verified, write that it could not. Unverifiable is a real result.
5. Never invent a price. If it is behind a registration wall, say so. A third-party price is attributed to the third party.
6. Record the admission gate, and the price for the user's category, on every record.

## Record format

```
## N. Official event name  [verdict]  (lane: lane-name)
- Where: city, venue, country
- When: dates, or the pattern and what it rests on
- Listed price: what the organiser publishes, in its currency, and where it was seen
- Your price: the tier for your category, or "not published"
- Meetings: any one-to-one or matchmaking programme, or "none seen"
- Format: expo, conference, meetup, summit, hosted-buyer or chapter series
- Who's in the room: who actually attends, and how many, as specifically as the source allows
- Why: one or two sentences on why it earns a place, or why it is recorded but not bookable
- Gate: any admission rule (left out when entry is open)
- URL: the organiser's own page
- Check notes: what the checker checked, on which page, and what it found
- Corrections: correction types, or "none"
```

The last two lines are added by the checker. Prices stay in the organiser's currency and are never converted in a record. Your price is the price for the user's category: the one price everyone pays where there is only one, "not published" only when the price that applies to them is not shown. Fields hold facts and their sources; how the lane searched goes in its lane notes, which the checker never sees.

## Stage 3: Check

- Every record is checked, by a pass that did not find it.
- The posture: each record is wrong until the organiser's own page says otherwise. The commonest failure is inheritance: last year's date, repeated by a listing site, written down as this year's.
- Verdicts: confirmed, pattern-estimate, dead, unverifiable.
- Correction types: date-wrong, price-wrong, dead-not-caught, gate-missed, room-overstated, name-wrong, and detail-wrong for any other stated fact that was wrong (a place, a time, a quote, a figure that is not the price or the room). Filling in a detail the record left out is not a correction, except a missed gate or a missing price for the user's category. See [ADR 0007](../adr/0007-a-seventh-correction-type.md).
- Every correction is stated, never made silently. Inventing a correction to look diligent is the same failure as rubber-stamping.
- A correction needs an organiser's page that says something different about the same thing. A field the checker cannot confirm is left as it is and noted as unverified in the check notes, never corrected from a page about a different service. Added for 0.3.1 after the v0.3.0 release check, where the checker twice replaced a matchmaking rule with a different service's rule.
- A dead verdict is re-checked under the organiser's domain before it stands, because events get renamed.

## Stage 4: Score

| Code | Dimension | Range |
|---|---|---|
| R | Right people in the room | 0 to 3, counted double |
| A | Conversation access | 0 to 3 |
| V | Value for money | 0 to 3 |
| L | Learning | 0 to 2 |
| B | Bonus | 0 to 1 |

Score = 2R + A + V + L + B, out of 15. **Book** at 12 or more, **consider** at 9 to 11, **skip** below 9.

- The weights are the same for everyone. The brief decides what each dimension means for this user.
- Dead, unverifiable and sold-out events are not scored. Nor is an event whose next edition falls outside the window, which is left off the shortlist.
- An event whose gate keeps the user out is recorded, not scored as bookable. So is one they can only enter by sponsoring or exhibiting, with the route named.
- When the user's price is not published, value for money scores 1 at most, and the shortlist says to ask the price first.
- When value for money needs a currency conversion, the shortlist says the conversion is rough.

## Stage 5: Hand-back

`shortlist.md`, in this order:

1. The checker's correction counts by type, and the verdict counts.
2. Events sorted by score into book, consider and skip, with the organiser's link on every line.
3. The top 3 (the three highest scores in book and consider) marked "check this yourself before you spend".
4. Book or consider events in the same city within 7 days grouped as one possible trip.
5. Events not bookable for the user at the bottom: gated, sold out, dead and unverifiable.

## Files

On the subagent route, a folder `find-events/<YYYY-MM-DD>-<short-name>/` in the working directory:

- `brief.md`, `records.md` (every record after the check) and `shortlist.md`.
- `working/`, holding the raw lane files and the check files, so every correction can be traced.
- `check-in/`, holding only the stripped records each checker reads.

On the chat route, the same three as one document in the chat.

Every fact on the shortlist comes from `records.md`. Nothing checks the hand-back, so it adds nothing the records do not say.

## Not in this version

Re-checking an old list later, calendar export, booking or registering, and agents other than Claude.

## Tests

- **Check set.** 10 records: 5 clean, and 5 each with one planted error (last year's date, a listing-site price presented as official, a dead event shown as alive, a missed gate, a renamed event). It passes when all 5 errors are caught with the right correction type and no correction is invented on the clean 5. The set is re-confirmed against the organisers' pages before each release.
- **Live run.** One real end-to-end run, published as the README example.
- **Structure checks** in CI: the manifests are valid, every skill's frontmatter is valid, and every file a skill points to exists.

## Packaging

- Repo `scordsy/skills`, one plugin `stefancordery-skills` holding every skill. Claude Code installs through the repo's own marketplace. Claude.ai and Desktop users get a zip of the skill on each GitHub release.
- MIT licence. UK English. No em-dashes.
