# find-events: example run

A real run of `find-events` on 2 November 2026, for a made-up brief: a 12-person UK company selling absence and leave management software, looking to meet HR directors at employers of 200 to 2,000 staff.

| File | What it is |
|---|---|
| [`brief.md`](brief.md) | The brief the run searched from. The company is made up; no website was given, so the drafts came from a one-line description |
| [`records.md`](records.md) | All 26 events after the check, each with the checker's notes and corrections |
| [`shortlist.md`](shortlist.md) | The hand-back |

The events, dates, prices and gates are real, as the organisers' pages showed them on the day. They will go out of date.

Three notes on how this example was made:

- **One event was found by two lanes.** Health & Wellbeing at Work 2027 came back from both the conferences lane and the payroll lane. The merge flagged it, and the second copy was dropped, leaving 26 of 27.
- **Smaller fixes are not counted.** The checkers also corrected facts outside the six types the skill counted at the time, such as a 2027 city the organiser had not announced. They are stated in each record's check notes. The skill now counts them as `detail-wrong` ([ADR 0007](../../adr/0007-a-seventh-correction-type.md)); this run came before that.
- **The shortlist was scored again after review.** A review of the skill tightened two rules after this run: value for money scores 1 at most when the record says your price is not published, and the shortlist follows the spec's order. The shortlist here follows the current rules, applied to the records exactly as the run wrote them. That is why Trust: Beyond the Paradox says "not published" next to a listed price of GBP 60: its record says no supplier tier is stated.
