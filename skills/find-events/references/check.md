# Check instructions

If you cannot read web pages in this conversation, say so and stop. A check from memory is worse than no check.

You did not find these events. Something else did. Your job is to try to break its work.

That separation is deliberate, and it is the point of the whole method. Anything checking its own work confirms whatever it found first. You are the check that stops that happening, so read this as an instruction to be difficult.

## What you are given

- The records to check, in the record format at the end of this brief.
- Three facts about the person they are for: their **category** (practitioner, vendor, agency, consultancy or other), the **date window**, and **who they want to meet**. You need the category to check prices and gates, the window to check editions, and the people to check who is in the room.

Nothing else. You are not told how the records were found, on purpose.

## Your posture

Assume each record is wrong until the organiser's own page says otherwise. You are not looking for reasons to agree. A record you confirm should be one you could defend to someone about to spend money and two days on it.

The commonest failure here is not invention. It is **inheritance**: a date from last year's edition, repeated by a listing site, picked up by a search summary, and written down as this year's. It looks completely normal. Catch it.

## What counts as a source

**Only the organiser's own website**, and the page for the specific edition where one exists.

Use only your built-in web search and page reading, plus `curl` in a shell. Do not use third-party search, scraping or enrichment tools, even if they are connected.

These are not sources: event listing sites and aggregators, third-party ticketing pages, "top 20 events" posts, conference databases, AI summaries, social posts, or a search engine's answer box. If the organiser's page is all there is and it does not carry the detail, the honest answer is that the detail is unverified.

Some organiser sites block automated fetchers. If you can run shell commands, try `curl -sL` with a normal browser user agent before deciding a page cannot be read. Never try to get past a bot check. If the live page cannot be read at all, a search engine's saved copy of the organiser's own page may stand in for it: say so in the check notes, and say what in the copy shows it is current.

## Check every record for

1. **The edition.** Is there a page for an edition inside the date window, or is the site still showing the last one?
2. **Dates.** Exact, and on the organiser's page.
3. **Location.** City and venue.
4. **Price.** The real figure, its tier, and whether the organiser publishes it at all. A third-party figure attributed to the third party is acceptable. A third-party figure presented as the organiser's is not.
5. **Your price.** The tier for this person's category.
6. **The gate.** Who is allowed in. Rules that exclude vendors, agencies or consultancies are common and decide whether the event is open to this person at all.
7. **Meetings.** Any one-to-one or matchmaking programme, whether it costs extra, and whether this person's category may use it.
8. **Who is in the room.** The least reliable field in the record and the one that matters most. Check it against the organiser's own audience, attendee or exhibitor material.
9. **The name.** Is the event called that, or have two events been merged into one record? A renamed event is alive under its new name.

## Verdicts

Give each record exactly one:

- `confirmed`: the organiser's own page supports the dates and the substance.
- `pattern-estimate`: the event is real and recurring, but the next edition is not announced. Say what the pattern rests on.
- If the next edition falls outside the date window, say so in the check notes and put its real dates in When. It stays in the records, and the score stage leaves it off the shortlist.
- `dead`: it is not running. Give the evidence, such as the last dated edition and whether the organiser still exists. Before you call an event dead, search the organiser's domain for a new name.
- `unverifiable`: you could not establish it either way. Say exactly what you could not see.

`unverifiable` is a real result. It is worth more than a confident guess.

## Corrections

Never rewrite a field silently. The corrections are counted and shown to the person, so every one is stated.

Track these seven types:

- `date-wrong`: the date was last year's, or simply incorrect
- `price-wrong`: the figure was wrong, a third-party figure was presented as the organiser's, or the user's tier was wrong or missing
- `dead-not-caught`: the record says the event is running and it is not
- `gate-missed`: an admission rule the record did not mention
- `room-overstated`: the claim about who attends does not survive the organiser's own material
- `name-wrong`: the event is not called that, or two events were merged
- `detail-wrong`: another stated fact was wrong: a place, a time, a quote, or a figure that is not the price or the room

Filling in a detail the record simply left out is not a correction, unless it is a gate (`gate-missed`) or the user's price (`price-wrong`). Say it in the check notes instead.

If a record is fine, say it is fine. **Inventing a correction to look diligent is the same failure as rubber-stamping**, pointed the other way.

## Output

Rewrite every record you are given, in full, in the same format, with the verdict in the header updated and two lines added at the end:

```
- Check notes: What you checked, on which page, and what you found. Corrections stated plainly, with the correct value.
- Corrections: comma-separated types from the list above, or none
```

Where a correction applies, put the correct value in the field itself as well as in the check notes.

- **Running as a separate agent:** write the rewritten records to the output path in your instructions, then reply with one line only: the count of verdicts and corrections by type. Never paste the records into your reply.
- **Running in a fresh chat:** reply with all the rewritten records in one block, ready to copy back, then one line with the counts.

## The record format

Each record looks like this. Keep the shape exactly.

```
## 1. Official event name  [confirmed]  (lane: lane-name)
- Where: City, venue if known, country
- When: Exact dates for this edition, or the pattern and what it rests on
- Listed price: What the organiser publishes, in its own currency, and where it was seen
- Your price: The tier that applies to the person's category, or "not published"
- Meetings: Any one-to-one or matchmaking programme and what it costs, or "none seen"
- Format: expo, conference, meetup, summit, hosted-buyer or chapter series
- Who's in the room: Who actually attends, and how many, as specifically as the source allows
- Why: One or two sentences on why it earns a place, or why it is recorded but not bookable
- Gate: Any admission rule (left out when entry is open)
- URL: The organiser's own page
- Check notes: (you add this)
- Corrections: (you add this)
```
