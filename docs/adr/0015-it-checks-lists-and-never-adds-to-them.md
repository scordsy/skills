# 15. It checks lists and never adds to them

**Status:** accepted, 4 November 2026

## Context

A skill that has just researched 50 companies against a profile could easily suggest better ones. Users would ask for it.

## Decision

`check-account-list` never adds a company, suggests a replacement, ranks the keeps, finds contacts or contacts anyone. It hands back the same list with a verdict on every row.

## Why

Building a list and checking it are different jobs, and a skill that does both is marking its own homework: the companies it added would be checked by the same run that found them. Keeping to checking also keeps it clear of list-building, which is other people's product, and keeps the skill small enough to test.
