# 7. A seventh correction type: detail-wrong

**Status:** accepted, 2 November 2026

## Context

The check counted six correction types, carried over from the method this skill packages: date-wrong, price-wrong, dead-not-caught, gate-missed, room-overstated and name-wrong. In the first live run the checkers also fixed facts none of the six covers: a 2027 city the organiser had not announced, a quote put on the wrong page, a stage count, a missing price tier. They stated each fix in their notes, as told, but the tally could not count them, so the headline ("3 of 26 records needed a correction") understated what the check did.

## Decision

Add a seventh type, `detail-wrong`: any other stated fact that was wrong. Filling in a detail the record left out stays uncounted and goes in the check notes, except a missed gate (`gate-missed`) or a missing price for the user's category (`price-wrong`), which already have types because they decide whether the user can go and what it costs.

## Why

- Every wrong fact the check catches is now counted, so the headline is honest in both directions.
- Keeping the original six separate keeps the counts that matter most (dates, prices, dead events, gates) readable on their own.
- Additions stay out of the count, so a checker cannot pad the numbers by adding detail. The check instructions already say that inventing a correction is the same failure as missing one.
