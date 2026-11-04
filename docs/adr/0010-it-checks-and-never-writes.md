# 10. It checks summaries, never writes them, and never touches a CRM

**Status:** accepted, 4 November 2026

## Context

Plenty of tools write call summaries, and some write them straight into a CRM. The failure this skill exists for is the step in between: nobody checks the summary before it becomes the record everyone downstream trusts.

## Decision

`check-call-summary` takes a transcript and one or more summaries someone or something else wrote, and checks them. It does not write a summary from scratch, and it does not read from or write to a call recorder or a CRM. It hands back a report and a corrected draft with every change marked. Owners, dates, doubtful labels and anything resting on tone go on a list to confirm with a person before saving.

## Why

Writing summaries is done well elsewhere, and a skill that both writes and checks a summary is marking its own homework. Connectors to recorders and CRMs need keys and accounts, which [ADR 0004](0004-no-api-keys.md) rules out. Keeping a person at the point where the summary becomes the record is the whole argument of the post the skill came from.
