# find-events

**A shortlist of events worth your time and money, with every event checked against the organiser's own page before you see it.**

Listing sites are wrong at the edges. Dead events stay listed for years. Last year's dates get copied forward as this year's. And the price on the page is often not your price: plenty of conferences charge suppliers several times what practitioners pay, and some won't let suppliers in at all.

`find-events` interviews you, searches for events where the people you want to meet actually gather, then hands every event to a separate pass that assumes it is wrong until the organiser's own page proves otherwise. Only then does it score them and hand you a shortlist.

## An example run

A made-up brief: a 12-person UK company selling absence management software, looking to meet HR directors at employers of 200 to 2,000 staff. One person, travelling from Manchester, GBP 3,000 of tickets, December 2026 to May 2027.

Four search lanes found 26 events. The checker confirmed 18, marked 6 as not yet announced, proved 1 dead and marked 1 unverifiable. It corrected 3 of the 26 records, 6 fields in all: a gate missed on two of them, a room overstated on two, a wrong price and a wrong date. It also fixed smaller facts, such as a city the organiser hadn't actually announced yet. Those were stated in its notes but not counted, because this run came before the skill gave them their own type, `detail-wrong`.

What it found that a search would not have:

- **The price you would actually pay.** Health & Wellbeing at Work sells standard tickets from GBP 79 + VAT, but anyone selling into HR or wellbeing must buy the GBP 600 + VAT supplier ticket.
- **The doors that are shut.** Engage Employee Summit is free for practitioners and GBP 1,495 for suppliers, and its one-to-one meetings are closed to suppliers. Three senior HR rooms in the window only let a supplier in as a sponsor or with a paid supplier package, and an HR conference for schools only as an exhibitor.
- **A dead event still on listing sites.** The last edition of The Watercooler Event that could be found was May 2025. A 2026 edition was announced, nothing shows it ran, and its domain now shows unrelated content.
- **A trip.** HR Minds Summit and Health & Wellbeing at Work run on the same days at the same venue.

The [full run is here](../../docs/examples/find-events/): the [brief](../../docs/examples/find-events/brief.md), all [26 checked records](../../docs/examples/find-events/records.md) with the checker's notes, and the [shortlist](../../docs/examples/find-events/shortlist.md).

## How it works

1. **Interview.** Give it your company website, or describe what you do in a line. It drafts what you do, who you sell to or work with, and how organisers will see you (practitioner, vendor, agency, consultancy or other), and you correct it. Then a few questions, one at a time: your role, who you want to meet, what a good event looks like, what rules one out, budget and travel, dates, and events you already know. "Not sure" is always fine. You approve a written brief before anything is searched.
2. **Discovery.** Up to 4 search lanes, by region or type of event, each given the whole brief and a set of honesty rules: only the organiser's own page counts, say when a date is not announced, prove a dead event dead, never invent a price.
3. **Check.** A separate pass that never saw how the events were found checks every one against the organiser's own page, and states every correction it makes.
4. **Score.** Out of 15. Being in a room with the right people counts double. Book, consider or skip.
5. **Shortlist.** The counts from the check, every event with its organiser's link, the top 3 to check yourself before you spend, trips that combine, and what is not bookable for you and why.

## Install

See the [install steps](../../README.md#install). Then run `/find-events`, or ask Claude something like "which events should I go to next year to meet HR directors?"

**In Claude Code** the lanes and the check run as separate subagents, in parallel.

**In a Claude.ai or Claude Desktop chat** there are no subagents, so the lanes run one after another. For the check it gives you a block to paste into a new chat, and you paste the answer back. That one paste is what keeps the check honest. Turn on web search in both chats.

## What a run costs

The example run used 8 subagents: 4 to search and 4 to check. Together they used 1.9 million tokens, and the run took 30 minutes from approving the brief to the shortlist, with the subagents running in parallel. In a chat, where the lanes run one after another, expect it to take longer. If that is more than you want to spend, ask for fewer lanes when it shows you the brief.

## Tested

A fixed set of 10 event records, 5 accurate and 5 with one planted error each: last year's date, a listing site's price shown as the organiser's, a dead event shown as alive, a missed supplier gate, and an old event name. The checker passes only if it catches all 5 errors with the right type and invents no correction on the accurate 5.

On its first run it caught all 5, and it also corrected 3 of the records I had written as accurate. I checked those 3 against the organisers' own pages, and the checker was right every time. One record called a show "the largest" for in-house finance teams when the organiser's own split is 63% accountants in practice. One missed that a free logistics show asks non-exhibitors not to sell on the floor. One missed that only exhibitors can book buyer meetings. I fixed the records, and on the second run it caught all 5 planted errors and changed nothing on the 5 accurate ones.

The set, its answer key, the facts behind both and the two runs are in [`tests/find-events/`](../../tests/find-events/).

## Read it with care

- **Events change.** Every fact is as the organiser's page showed it on the day of the run.
- **"Who's in the room" is the weakest field.** It is only as good as what organisers publish about their audience.
- **The checker is an AI too.** It catches a lot, not everything. That is why the shortlist names three events for you to check yourself before you spend anything.
- **Scores are judgements against your brief**, written as their parts so you can see why.
- **It never books, registers or pays for anything.**

## Where it came from

The method behind my post ["AI doesn't know who you want to meet. Nobody told it."](https://www.linkedin.com/posts/stefancordery_ai-doesnt-know-who-you-want-to-meet-nobody-share-7521181055668600832-dXfZ/). That run found 191 events, 24 of them dead. A second set of agents checked every one against the organiser's own site and corrected more than half: 56 had the price missing or wrong. This skill packages the same brief, the same honesty rules and the same separate check, so you can run it yourself.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [More skills](../../README.md)
