# Skills

[![CI](https://github.com/scordsy/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/scordsy/skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

My skills for Claude. Each one does a single job, and each one is built so you can check its work before you act on it.

## The skills

| Skill | What it does |
|---|---|
| [**find-events**](skills/find-events/) | A shortlist of events worth attending to meet the people you want, with every event checked against the organiser's own page before you see it. |

## Install

### Claude Code

```bash
claude plugin marketplace add scordsy/skills
claude plugin install stefancordery-skills@stefancordery
```

Or in one step:

```bash
claude plugin install stefancordery-skills --marketplace scordsy/skills
```

Then run a skill by name, for example `/find-events` (or `/stefancordery-skills:find-events` if another skill shares the name), or just ask Claude for what you need: "which events should I go to next year to meet HR directors?"

**Get new skills as they land.** Plugins from outside Anthropic's own marketplace don't update on their own by default. Turn it on once: `/plugin`, then **Marketplaces**, select **stefancordery**, then **Enable auto-update**. Or update by hand with `claude plugin update stefancordery-skills@stefancordery`.

### Claude.ai and Claude Desktop

1. Download the skill's zip from the [latest release](https://github.com/scordsy/skills/releases/latest), for example `find-events.zip`.
2. Make sure **Code execution and file creation** is on, under **Settings**, then **Capabilities**.
3. Go to **Customize**, then **Skills**, then **+**, **Create skill**, **Upload a skill**, and choose the zip.
4. Turn on web search in the chat where you use it.

Each skill's own page says what works differently outside Claude Code.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [list-decay](https://github.com/scordsy/list-decay): find the dissolved and closing companies on your UK prospect list before you pay to enrich, verify or email them.

MIT licensed.
