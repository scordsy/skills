# The shortlist

The hand-back. Write it to `shortlist.md` in this exact order. Every event line carries the organiser's link.

```markdown
# Events shortlist: <short name>

<Date of run>. Window: <from> to <to>. For: <who they want to meet, in one line>.

## What the check found

<N> records found across <N> lanes. The checker, which never saw how they were found, checked every one against the organiser's own page. <n> of <N> needed at least one correction:

| Correction | Count |
|---|---|
| date-wrong | <n> |
| price-wrong | <n> |
| dead-not-caught | <n> |
| gate-missed | <n> |
| room-overstated | <n> |
| name-wrong | <n> |
| detail-wrong | <n> |

| Verdict | Count |
|---|---|
| confirmed | <n> |
| pattern-estimate | <n> |
| dead | <n> |
| unverifiable | <n> |

## Book (12 or more)

| Event | When | Where | Your price | Score | Why |
|---|---|---|---|---|---|
| [Event name](organiser URL) | <dates> | <city> | <your price> | 13 (R3 A3 V2 L1 B1) | <one line> |

## Consider (9 to 11)

<same table>

## Skip (below 9)

<same table>

## Check these yourself before you spend

1. **[Event name](organiser URL)**, <dates>, <city>. <Score with parts>. <Your price>. <One line: why it is here, and the one thing to confirm>.
2. ...
3. ...

## Possible trips

- **<City>, <dates>:** [Event A](url) and [Event B](url). <One line on why they combine.>

## Not bookable for you

| Event | Why not | Link |
|---|---|---|
| <name> | gated: <the rule, and the route in if there is one> | <url> |
| <name> | sold out | <url> |
| <name> | dead: <evidence in a few words> | <url> |
| <name> | unverifiable: <what could not be seen> | <url> |

---

Every fact above is from the organiser's own page on the date of this run. Events change. Confirm the date, the price and the gate before you spend anything.
```

## Notes

- **Every fact on the shortlist comes from `records.md`.** Nothing checks this stage, so add nothing the records do not say: no travel times you have not been given, no "the biggest", no topics the organiser did not name. Where a record marks something as the researcher's inference, keep it marked "(inference)". Read each line back against its record before you hand over.
- **The counts come from `records.md`, never from memory.** Run the tally command in `SKILL.md`. In a chat with no Python, count the verdict headers and `Corrections:` lines by hand, twice.
- **Your price** is copied from the record's Your price line. Where it says "not published", the row says "not published: ask the price first".
- **Pattern-estimates** carry "(est)" after the name in every table, and their Why says "confirm the date before booking travel".
- **Within a tier**, sort by score, then cheaper first. An unpublished price counts as dearer than any published one.
- **The top 3** are the three highest-scoring events in Book and Consider, ties broken the same way. If fewer than three events score 9 or more, list only those.
- **Possible trips** are Book or Consider events in the same city within 7 days of each other. Leave the section out if there are none.
- **The link** is the organiser's own page. For a dead event whose domain no longer belongs to it, link the page that shows it is dead instead, and say so.
- **Leave out empty sections** rather than writing "none".
- **Rough conversions:** if any value for money score used a currency conversion, add one line under the tables saying which rate was used and that it is rough.
- **If the user skipped the check:** replace "What the check found" with this line, and keep every verdict as discovery wrote it: "**Unchecked.** No separate pass has checked these records against the organisers' pages. Expect wrong dates, prices and gates."
- **In a chat**, show the brief, the checked records and this shortlist together as one document.
