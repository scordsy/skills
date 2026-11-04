# 8. Quotes are checked by code, not by the model

**Status:** accepted, 4 November 2026

## Context

Skills that read transcripts make up plausible detail. A checker is no exception: asked to back a claim with a quote, it can produce a quote that sounds right and is not in the transcript, or put the right words in the wrong mouth. If the checker's evidence is invented, the whole check is.

## Decision

`check-call-summary` numbers every transcript line before anything else, and every quote a checker gives cites the lines it comes from. A standard-library script then confirms each quote is on those lines word for word (ignoring case, spacing, quote marks and punctuation), and that the speaker named is the one the line carries. The same script confirms every `From` line is really in the summary, and that every line of the summary was checked.

A claim that fails goes back to the checker once. If it still fails, the report lists it as "quote could not be verified, check by hand".

## Why

A model marking another model's work is still a model. String matching cannot be talked round. It is the one part of the check that is certain, so it carries the evidence, and the model carries the judgement.
