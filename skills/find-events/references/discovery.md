# Discovery instructions

You are researching one lane of an event search. Read this whole file, then the brief, then `record-format.md`, before you search anything.

## Read the brief first

The brief tells you who this person is, who they want to meet and why. It describes the person, not a task. When you are deciding whether an event counts, the answer is in the brief. If it is not, say so in your lane notes rather than guessing.

## What a good find looks like

A room where this person can talk to the people they want to meet. That is the whole objective, and format matters as much as the guest list:

- A meetup where 60 of the right people stand around talking beats a conference where 2,000 of the wrong people watch a stage.
- A one-to-one matchmaking programme is worth a lot, but only if the user's category is allowed to use it.
- An expo floor is good if the right people walk the aisles, and worthless if the aisles are full of other vendors.
- The most useful rooms are often not on listing sites at all: user groups, community chapters, meetup series, membership networks with local events. Nobody sells a ticket to them, so look for them deliberately.

## The honesty rules

These are the point of the whole exercise. Listing sites cannot be trusted at the edges. Dead events stay listed for years, and dates for editions that have not been announced are copied forward from last year.

1. **Go to the organiser's own page.** A listing site, an aggregator, a "top 50 events" post or an AI summary is not a source. Use them to find events, then read the organiser's site.
2. **If the next edition has not been announced, say so.** Mark the record `pattern-estimate` and say what the pattern rests on.
3. **If an event looks dead, prove it either way.** Check the organiser's site, the last dated post, and whether the organiser still exists. Events get renamed: before you call one dead, search the organiser's domain, not just the name you hold.
4. **If you cannot verify something, write that you could not.** `unverifiable` is a useful result. A confident guess is not.
5. **Never invent a price.** If it is behind a registration wall, write that. Attribute any third-party figure to the third party.
6. **Find the price and the gate for this user's category.** The brief gives the category. Many events charge vendors, agencies or consultancies several times the practitioner price, and some refuse them outright. A free event the user cannot get into is not a free event.
7. **A separate checker will re-check every record against the organiser's own page.** A record that cannot survive that check is worse than no record. Do not pad.

## Stay in your lane

- Your lane is given in your instructions. Other lanes are being covered at the same time, and duplicated work is wasted.
- If you find something that clearly belongs to another lane, note it in one line under `## Belongs to another lane` at the end of your file and move on.
- Skip every event the brief lists as already known. If your lane's obvious answer is on that list, go deeper instead.
- Stay inside the brief's date window. An event outside it does not belong, however good it is.

## How many

Up to 10 records, unless your instructions say otherwise. **Fifteen well-checked records beat forty thin ones.** If your lane holds only five events worth this person's time, return five and say so.

## Searching

- Use only your built-in web search and page reading, plus `curl` in a shell. Do not use third-party search, scraping or enrichment tools, even if they are connected.
- Search broadly first, then go to each organiser's own site for the facts.
- Read the page for the specific edition where one exists.
- Some organiser sites block automated fetchers. If you can run shell commands, try `curl -sL` with a normal browser user agent before concluding a page cannot be read. Never try to get past a bot check. A search engine's saved copy of the organiser's own page may stand in for a page that cannot be read at all; say so in the record.
- Search the organiser's domain for renamed or merged events.

## Output

Write your records, in the record format, to the file path in your instructions. At the end of the file add:

```
## Lane notes
- What you searched, and how
- What you deliberately left out, and why
- Where you ran out of road, or what a follow-up search should chase
```

When you are running as a separate agent, reply with one line only: the number of records written and the path. Never paste the records into your reply.

In a chat, where there is no file path, show the lane's records in your reply instead, and keep the lane notes apart from them.
