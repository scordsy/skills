# Record format

Every event is one record, in exactly this shape. The shape is fixed because the check, the score and the tally all read it.

```
## 1. Official event name  [confirmed]  (lane: uk-community-meetups)
- Where: City, venue if known, country
- When: Exact dates for this edition, or the pattern and what it rests on
- Listed price: What the organiser publishes, in its own currency, and where it was seen
- Your price: The tier that applies to the user's category, or "not published"
- Meetings: Any one-to-one or matchmaking programme and what it costs, or "none seen"
- Format: one of expo, conference, meetup, summit, hosted-buyer or chapter series, with a few words in brackets if useful
- Who's in the room: Who actually attends, and how many, as specifically as the source allows
- Why: One or two sentences on why it earns a place, or why it is recorded but not bookable
- Gate: Any admission rule, for example "free for in-house teams only, agencies excluded"
- URL: The organiser's own page, for this edition where one exists
```

## Facts only

The fields carry facts and where each one came from. Do not narrate your search, and do not point to your lane notes: what you searched and what you could not find go in the lane notes, which the checker never sees. Refer to other events by name, never by record number, because numbers change when lanes are merged.

## The header line

- Number records from 1 within each file.
- Use the event's official name, as the organiser writes it.
- The verdict in square brackets is exactly one of `confirmed`, `pattern-estimate`, `dead` or `unverifiable`.
- The lane name in brackets is the short name from the brief.

## Fields

- **When.** For a `pattern-estimate`, write what the pattern rests on: "2026 edition ran 14 May, annual since 2019, no 2027 date published". Never present an estimated date as a fact.
- **Listed price.** The organiser's own figure and currency, with the tier name if there are tiers. Never convert it. If the price is behind a registration wall, write that. A price from a listing site is written as the listing site's, for example "EUR 499 per a ticket reseller; the organiser's page hides pricing".
- **Your price.** Many events charge by who you are, and a vendor or consultancy ticket can cost several times a practitioner ticket for the same days. Write the tier for the user's category. If the organiser publishes one price for everyone, that price is theirs: write it. Write "not published" only when the price that applies to them is not shown. If their category cannot attend as a delegate at all, say so and name the route in (sponsoring, exhibiting).
- **Who's in the room.** The least reliable field and the one that matters most. Say who the organiser says attends, with numbers if published, and say when a claim is your inference rather than theirs.
- **Gate.** Leave the line out only when entry is genuinely open.
- **URL.** The organiser's own page. Never a listing site.

## Added by the check

The checker adds two lines to the end of every record:

```
- Check notes: What was checked, on which page, and what was found. Corrections stated plainly, with the correct value.
- Corrections: date-wrong, price-wrong
```

`Corrections` lists the correction types that apply, separated by commas, or `none`. The seven types are `date-wrong`, `price-wrong`, `dead-not-caught`, `gate-missed`, `room-overstated`, `name-wrong` and `detail-wrong`.
