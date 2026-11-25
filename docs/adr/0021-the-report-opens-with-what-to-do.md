# 21. The report opens with what to do, least work first

**Status:** accepted, 25 November 2026

## Context

The first design put the report in the checker's order: counts by verdict, the confirm list, every claim that differs or has no source, then the clean ones. A [sample report](../../tests/check-claims/sample-a4/README.md) built from the test of the problem's records for one draft showed what that looks like to the person who wrote the draft. Nine findings sat at the same weight, a one-word fix beside a claim with no source, and the report read as nine problems.

The [test of the problem](../../tests/check-claims/problem-test/README.md) says the work is smaller than that. Of 58 claims in six drafts, 6 differed: one real fix a draft. 10 were supported and carried a problem type, most of them a figure the publisher has since updated. 25 needed nothing.

A user who has just finished a draft, and is handed a report that looks like a list of faults, will stop running the skill or skim past it. Then the one fix that mattered is missed.

## Decision

`check.md` opens with what the user has to do, least work first:

1. One line saying how many claims need nothing, then a count for each kind of work.
2. **Fix these**: every `differs`, with the words to use instead given first.
3. **Update or re-credit these**: every `supported` claim that carries a problem type.
4. **Your call**: every `no-source`.
5. **Confirm with a person**: the user's own company, named people, and every `could-not-open`.
6. **Nothing to do**: every clean `supported` claim.
7. **How this was checked**: the counts by verdict and problem type, the checker's line, and the line on comparisons.

## Why

- **The order is the user's, not the checker's.** A verdict says what was found. The user wants to know what to do about it, and how long it will take.
- **Effort sorts better than verdict.** A `differs` comes with replacement words and is a paste. A `no-source` is a judgement the user has to make. A `could-not-open` is a visit to a page. Mixed together they all look like the hardest one.
- **The clean claims are said first because they are the common case.** In the test 25 of 58 were clean. Saying so before anything else puts the fixes in proportion.

## What this does not change

- No verdict, no problem type and no count. Every claim is still listed, with its evidence.
- The line saying no verdict was re-checked still sits above everything else.
- The counts and the line on comparisons are still in the report. They move to the end, under their own heading.
- The marked draft is unchanged.
