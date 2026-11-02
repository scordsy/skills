# 1. One repo and one plugin for every skill

**Status:** accepted, 2 November 2026

## Context

More skills are planned. Each could live in its own repo, or all of them in one.

## Decision

Every skill lives in this repo, in its own folder under `skills/`, and ships in one Claude Code plugin, `stefancordery-skills`. Tools with real code, tests and their own install (such as `list-decay`) keep their own repos. A skill that grows into one moves out.

## Why

- One install covers every skill, and new skills reach people who installed the plugin earlier.
- A repo holding a single skill file is thin. One repo keeps the work, and its history, in one place.
- A post can still link straight to a skill's folder, which has its own README.

## Cost

One version number for the whole plugin, so a broken skill is everyone's release. Acceptable at this size.
