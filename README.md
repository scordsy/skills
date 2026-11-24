![Claude skills for B2B sales and marketing teams. Every finding checked before you rely on it. By Stefan Cordery.](docs/assets/banner.png)

# Skills

[![CI](https://github.com/scordsy/skills/actions/workflows/ci.yml/badge.svg)](https://github.com/scordsy/skills/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

Claude skills for B2B sales and marketing teams. Each one does an everyday job, and every finding is checked before you rely on it.

## Why these exist

AI makes everyday sales and marketing jobs fast: a list of target accounts, a summary of a sales call. The output looks right, so it goes straight into the CRM or the outbound sequence. Often it is quietly wrong.

When I asked ChatGPT for "50 companies like our best customer" and checked a sample (15), only 1 was usable. None were made up. They were real companies, just the wrong ones: some had been taken over, some were too big or too small, some sold to a different kind of customer, and some were direct competitors of the company asking for the list.

ChatGPT even told me to check the list before using it: confirm each company's headcount, confirm where it's based, check it actually sells its own software. Good advice. It just didn't do any of it. That checking is the slow, tedious part that gets skipped when you're busy, and it's the part these skills do for you.

Two of the skills here check work you already have: a target account list, or an AI summary of a call. The third, find-events, does the research for you: a structured search for the events worth attending to meet the people you want. All three work the same way:

- **It starts from what you give it**: a list, a call transcript, the people you want to meet.
- **Every finding comes with its source**: a link and the exact words, so you can see why without taking it on trust.
- **The part that does the work never checks it.** A separate checker tries to prove each finding wrong.
- **No API keys, no paid tools, no accounts to create.** Install it and run it.

## The skills

| Skill | For | What it does |
|---|---|---|
| [**check-account-list**](skills/check-account-list/) | Sales and marketing | Every company on a target account list checked before you spend on it: website, still trading, bought, size, fit and competitors, each with evidence you can click. Checks companies in any country, as far as each country's free register allows. |
| [**check-call-summary**](skills/check-call-summary/) | Sales and customer success | An AI summary of a call, checked claim by claim against the transcript before it goes in your CRM. Every claim traced to a quote, with speaker mix-ups, jokes taken literally and missed next steps flagged. |
| [**find-events**](skills/find-events/) | Marketing and sales | A shortlist of events worth attending to meet the people you want, with every event checked against the organiser's own page before you see it. |

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
2. Make sure **Create and edit files** is on, under **Settings**, then **Capabilities**. In the older Settings layout it is called **Code execution and file creation**. The skills open their own files and run small scripts, so they need it.
3. Go to **Customize**, then **Skills**, then **+**, **Create skill**, **Upload a skill**, and choose the zip.
4. For find-events and check-account-list, turn on web search in the chat where you use it.
5. **Use a normal chat, not an incognito one.** An incognito chat can't open a skill's files, so the skill tells you it can't run there and stops. The one exception is the block find-events and check-account-list may ask you to paste into a fresh chat for their check. It carries its own instructions, so an incognito chat is fine for that, and best, because it can't see the chat that did the research.

Some Claude.ai and Claude Desktop chats can run subagents, as Claude Code does, and a skill then runs its full version. A chat that can't gets a version without them, and the skill says what is different. Each skill's own page says which version its tests covered.

## About

Built by **Stefan Cordery**. Marketing leader turned builder, 14+ years in B2B marketing, now building GTM systems in Claude Code.

- [Follow me on LinkedIn](https://www.linkedin.com/in/stefancordery/)
- [list-decay](https://github.com/scordsy/list-decay): find the dissolved and closing companies on your UK prospect list before you pay to enrich, verify or email them.

MIT licensed.
