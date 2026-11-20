# 18. check-account-list asks for the list after the profile

**Status:** accepted, 19 November 2026

## Context

The profile is what every company on the list is checked against, so it has to come from the user, not from the list. On 19 November 2026 check-account-list was run on Claude.ai with 12 of its check-set companies. Two things went wrong in the profile interview, both because the list arrived first:

- It asked for the list and the profile's first question in the same message, where the rule is one question per message.
- After seeing the list, it added Feefo, a company on it, to the profile's named competitors. The check set leaves Feefo unnamed on purpose, so the check has to catch it by the kind of product. Naming it would have turned that test into a giveaway. It was taken out before the profile was approved.

## Decision

The skill asks for the list at Stage 2, in a message of its own, once the profile is approved. If the user gives the list earlier, the skill says it will check it once the profile is agreed and takes nothing from it for the profile. Named competitors and existing customers come only from the user's answers, or from the user's own website with the user's yes, never from the list being checked.

check-call-summary does the same with its summaries in a chat: the key facts are listed before the summary is read, so the summary cannot decide what mattered.

## Why

A competitor named from the list is caught because it was named, not because the check worked, and the user cannot tell the difference. The same goes for a customer. Asking for the list later also keeps each message to one ask. The cost is small: the user who arrives with a list in hand is asked to wait a few questions before it is used.
