# Interview

The goal is a brief good enough that a researcher who has never met this person could pick the right events. Everything downstream depends on it.

## How to ask

- **One question per message.** Wait for the answer.
- **Draft before you ask.** Wherever you can guess the answer, offer the guess to confirm: "From your site it looks like you sell to HR directors at firms of 200 to 2,000 staff. Right?" Correcting a draft is much easier than writing an answer, and people who would stall at a blank question keep going.
- **Push back once on a vague answer**, with an example of a sharper one. "Marketers" becomes which marketers, at what size of company, doing what. If it is still vague, accept it and mark it as an assumption.
- **"Not sure" is always a fine answer.** Use the default given below, tell them what you used, and mark it as an assumption in the brief.
- **Never ask what you already know.** If an earlier answer covered a later question, offer it as a draft instead.
- Keep it moving. The interview should take a few minutes, not a meeting.

## The questions, in order

### 1. The company

Ask: "What's your company website? Or, if you'd rather, tell me what you do in a line."

**With a website:** read the homepage and up to 3 more pages from the same site, picking the ones that best show what is offered, to whom and at what price (about, customers or case studies, pricing). Use only your built-in page reading or `curl`, never third-party scraping or enrichment tools. Do not follow links to other sites. Do not use LinkedIn pages. If the site cannot be read, say so and ask for the one line instead.

**With a line:** work from that.

Then draft three things and show them together:

- **What you do or sell**, in one line.
- **Who you sell to or work with**: their role, and the type and size of organisation. Leave this out for someone who sells nothing, such as a job seeker or a student.
- **Your category**, as the organisers of the events they want will probably see them:
  - *practitioner*: attending as a member of the profession the event serves
  - *vendor*: selling software or products to the people attending
  - *agency*: selling a service delivered by a team
  - *consultancy*: selling advice or specialist work
  - *other*: investor, student, press, job seeker, and so on

Say in one line why the category matters: organisers price and admit by it, a vendor or consultancy ticket can cost several times the practitioner price for the same days, and some events refuse vendors outright.

Ask them to correct anything wrong.

Default if not sure: keep the drafts, marked as assumptions. If no draft can be made at all, assume **vendor**, the dearer and more restricted category, so no price or gate comes as a surprise.

### 2. Their role

Ask what they do. If question 1 already made it obvious, offer it as a draft.

Default if not sure: "not stated".

### 3. Who they want to meet

Draft it from "who you sell to or work with" in question 1, and **always ask for an explicit yes**. A website shows who a company markets to, which is not always who its people want to meet in a room, and this answer counts double in the score.

Push for: job titles, company type and size, sector, and region. Ask whether there is a second group worth meeting (for example, the sales team alongside marketing).

Default if not sure: the people drafted in question 1. Say that is the default and still ask for a yes to it. If it is assumed, put it first in the brief's Assumptions.

### 4. What a good event looks like

Offer the options rather than a blank question: small rooms where people talk, big conferences with an expo floor, one-to-one matchmaking, talks they would learn from, or a mix. Ask what has worked for them before, if anything.

Default if not sure: "rooms where you can actually talk to them". A meetup of 60 of the right people talking beats a conference of 2,000 watching a stage.

### 5. What rules an event out

Offer common ones: the wrong crowd (for example founders and investors, or consumer brands), events they would not be let into, paid meeting packages, too far away, a format they dislike.

Default if not sure: wrong crowd, and events they cannot get into.

### 6. Budget and travel

Ask, together:

- Ticket budget for the whole window, and the currency.
- Where they travel from.
- How far they will go: local only, their own country, their continent, or anywhere, and how many long trips.
- Whether it is just them going, or more people.

Default if not sure: free and low-cost events, their own country, one person.

### 7. The dates

Ask for the window to search. Use today's date to make it concrete. If you are not sure of today's date, ask.

Default if not sure: the next six months from today.

### 8. Events they already know

Ask which events they already go to or already know about, so the search skips them and digs deeper.

Default if not sure: none.

## The lanes

Propose up to 4 lanes. Each lane is one slice of the search, researched on its own: by region (home country, nearby countries, long-haul), or by event type (flagship conferences, community meetups and chapters, user groups, matchmaking programmes, niche events in their sector). Pick the split that fits the brief. Give each lane a short name in lower case with hyphens, a one-line scope, and a one-line reason.

Where the brief favours conversation, include a lane for unticketed rooms: user groups, community chapters and meetup series. They rarely appear on listing sites and are often the best rooms in the year.

## The brief

Give the brief a short name in lower case with hyphens, such as `absence-software`; it becomes part of the run folder's name. Write `brief.md` in this shape, show it, and ask for approval. **Nothing is searched until they approve or edit it.**

```markdown
# Brief: <short name>

Run date: <today>. Window: <from> to <to>.

## You
- Company: <name or one-line description>
- Does or sells: <one line>
- Sells to or works with: <one line>
- Category: <category>
- Role: <role>

## Who you want to meet
<titles, company type and size, sector, region; any second group>

## A good event
<what they said>

## Ruled out
<what they said>

## Budget and travel
- Tickets: <amount and currency> for the window
- From: <place>
- Range: <how far, how many long trips>
- Going: <one person or more>

## Already known (skipped)
<list, or none>

## Assumptions
- <each answer that used a default, and the default used>

## Lanes
1. **<lane-name>**: <scope>. Why: <reason>.
2. ...

Reply "go" to start the search, or tell me what to change.
```
