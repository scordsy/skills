# 6. Prices stay in the organiser's currency

**Status:** accepted, 2 November 2026

## Context

A run can cover several countries, and users think in their own currency.

## Decision

Every record carries the price exactly as the organiser publishes it, in the organiser's currency. Records are never converted. Where value for money needs a comparison across currencies, the score uses a rough conversion and the shortlist says so.

## Why

A converted price looks like a fact the organiser published, and it goes out of date with the exchange rate. The checker can only check what the organiser's page actually says.
