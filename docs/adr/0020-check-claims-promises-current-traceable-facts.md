# 20. check-claims promises current, traceable facts, and has ten problem types

**Status:** accepted, 25 November 2026

## Context

The first design of `check-claims` rested on a worry it had not measured: that an AI-written draft carries wrong facts. Its spec said a test was owed. The [test of the problem](../../tests/check-claims/problem-test/README.md) ran on 25 November 2026: six drafts written by Claude with web search off, and 58 claims traced to their first publishers.

- 40 were supported, 6 differed, 4 had no findable first publisher and 8 sat on pages nobody could open.
- Of the 46 claims whose first publisher could be read, none misstated a figure.
- 10 claims were out of date, and in 7 of them the publisher had since given a different figure.
- 4 of the 6 that differed described the source wrongly. 3 of those credited one vendor's case study to its rival.
- No draft gave a web address for any claim.
- The researchers and checkers wrote down 12 kinds of error that fitted none of the nine problem types, or only half fitted one.

## Decision

**The promise changes.** The skill tells the user where each fact comes from, whether it is still current, and whether the draft credits the right publisher. It does not claim that AI drafts are full of wrong numbers. A wrong figure is still caught and counted.

**The problem types change, from nine to ten:**

1. All nine are kept. Five were not seen in the test, and three of those could not have been, because no draft gave a link or a quotation.
2. Out-of-date gets a rule for its verdict: supported when the draft dates the figure or states it as a past finding, differs when the draft states it as the present position.
3. A new type, `publisher-disagrees`, for a first publisher that gives two figures for the same thing. The record carries both quotes.
4. `overstated` is widened to work both ways and renamed `strength-changed`: a plan, a hedge, a range or a single case made firm, or a qualifier dropped.
5. `source-mislabelled` is widened from who published a study to how it was done: the data, the sample, the method.
6. `wrong-subject` is widened to a fact true of one subject and pinned on several.
7. `dead-link` is widened from the draft's link to the first publisher's own page, and renamed `page-gone`.

The spec also says which verdict each type can sit on, and how to tell neighbouring types apart. Page-gone is the only type a claim can carry without a page that was read.

## Why

- **A skill should promise what its own test found.** A pitch built on wrong numbers would be contradicted by the first user whose draft has none. Age and credit are what the test found, and they are faults a reader cannot see: a stale figure is real, and it was once right.
- **One writer is thin ground, so the promise is narrow.** The test used one model on one day with no web search. No second writer is tested before the build, so the skill says where its evidence stops. If a later test of another writer finds different faults, this record is revisited.
- **Out-of-date needed a rule because it was the commonest type** and the two passes in the test each had to make one up. The rule follows what the draft asserts. "The 2025 survey found 74%" is true whatever came later. "Is now part of" is false once the owner changes.
- **A type that only inflates misses half the error.** A dropped qualifier shrank a claim in the test as surely as a firmed-up plan would swell one. The old name could not carry both, so the type is renamed for what it describes.
- **Two figures from one publisher is not the draft's fault**, and no other type says so. Without it a checker must pick one figure and call the other wrong.
- **A page that has gone matters whoever linked to it.** Four publishers in the test had moved or replaced a page. The old type covered only a link the draft gave, and no draft gave one.
- **The count stays readable at ten.** Widening four types was chosen over adding a type for each of the 12 kinds of error. The cost is that neighbouring types now overlap, which the spec's rules for telling them apart are there to settle.

## What this does not change

The verdicts in the test stand as given. They were made before the out-of-date rule was written, and some might fall differently under it: A1-08, for one, states a figure as the present position and was called supported. The test is a record of what was found on the day, and it is not re-scored.
