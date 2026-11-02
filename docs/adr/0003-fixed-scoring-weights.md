# 3. The scoring weights are the same for everyone

**Status:** accepted, 2 November 2026

## Context

Users care about different things: one wants a cheap local meetup, another a single flagship trip. The weights could be set from the interview.

## Decision

The weights are fixed. Right people (0 to 3) counts double, then conversation access (0 to 3), value for money (0 to 3), learning (0 to 2) and bonus (0 to 1), out of 15. The interview changes what each dimension means for the user (who the right people are, what counts as good value on their budget), not how much it weighs.

## Why

- Scores that move their own weights cannot be compared between runs, or tested.
- Being in the wrong room fails the whole trip, whatever else is true. That holds for every user, so right people always counts double.
- What users actually differ on is captured by the brief, which already shapes every judgement the scorer makes.
