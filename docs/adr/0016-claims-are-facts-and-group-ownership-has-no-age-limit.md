# 16. Claims are facts, and group ownership has no age limit

**Status:** accepted, 4 November 2026

## Context

Two gaps came out of the reviews of `check-account-list`.

- **The checker could see how the first pass worked.** It gets each record's claim lines (website, registered, owner, size, fit, conflicts) and never the reasons or evidence ([ADR 0002](0002-the-checker-never-sees-the-research.md)). But researchers wrote their reasoning into the claims: "the buyer, Castik, gives 250 employees", "an investor holding a minority stake, so not bought", "this is the kind of product you sell". A checker handed those confirms them instead of finding its own.
- **Older ownership by a trading group had no rule.** "Bought" covered the last five years only. The profile asks whether companies owned by a larger group are wanted, because the buying decision often moves to the owner, but a company a trading group bought six years ago fitted no problem type. One line of the record format tried to cover it and contradicted itself.

## Decision

- **Claim lines hold facts and the document each comes from**, such as "39 staff, accounts to 30 June 2025". How a fact was found, and what was concluded from it, go in Reason and Evidence, which the checker never sees. The checker opens any document a claim names and reads it itself.
- **When the profile does not want group-owned companies, a company owned by a trading group counts as bought, however long ago.** Ownership by an investor older than five years is still noted and is not a problem.

## Why

A checker that reads the first pass's reasoning marks its homework against the first pass's answers. Naming the document still helps it find the page, and costs nothing in independence, because it must read the page itself.

The five-year line exists so that old private equity ownership does not knock out companies that run independently. A trading group is different at any age: it decides what its companies buy. Calling it "bought" rather than adding a tenth problem type keeps the count of problem types the user reads short.
