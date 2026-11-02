# 4. No API keys, no paid sources

**Status:** accepted, 2 November 2026

## Context

Event databases and search APIs exist and would make discovery faster.

## Decision

Skills in this repo use only the assistant's own web search and page reading. In Claude Code, `curl` with a normal browser identity is allowed as a fallback when an organiser's site blocks the built-in fetcher.

## Why

- A skill that needs a key is a skill most people never run.
- The only source that counts is the organiser's own page, which no paid database replaces. Listing sites and databases are where inherited dates come from.
