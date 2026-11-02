# CLAUDE.md

The brief for any agent working in this repo. Read [`GLOSSARY.md`](GLOSSARY.md) first and use its words exactly, in skills and in docs.

## What this is

Stefan Cordery's public Claude skills, shipped as one Claude Code plugin, `stefancordery-skills`, from this repo's own marketplace, `stefancordery`. One skill so far: [`find-events`](skills/find-events/SKILL.md).

## Commands

```bash
python3 scripts/check_repo.py                 # structure and house style
python3 -m unittest discover -s tests -v      # script tests, no network
python3 scripts/package_skill.py find-events  # the Claude.ai zip, into dist/
claude plugin validate .                      # the official manifest check (needs Claude Code)
```

Run all four before every commit. CI runs the first three. The validator gives one expected warning: this `CLAUDE.md` sits at the plugin root because the repo is the plugin. It is for working on the repo and is not shipped as context, which is what the warning says.

## Layout

| Path | Holds |
|---|---|
| `.claude-plugin/` | `plugin.json` and the repo's own `marketplace.json` |
| `skills/<name>/SKILL.md` | The skill. Claude Code finds every skill folder on its own |
| `skills/<name>/references/` | Files the skill reads at each stage |
| `skills/<name>/scripts/` | Standard-library Python the skill runs |
| `skills/<name>/README.md` | For people browsing GitHub. Never read by the skill, left out of the zip |
| `docs/specs/<name>.md` | The agreed design. Reviews check the skill against it |
| `docs/adr/` | One short record per decision a reader would question |
| `tests/` | Script tests, plus each skill's check set |
| `scripts/` | Repo tooling: checks and packaging |

## Rules

- **The spec is the agreement.** Change a skill's behaviour only with a matching change to its spec, and a decision record when a reader would ask why.
- **No API keys and no paid services**, in any skill. See [ADR 0004](docs/adr/0004-no-api-keys.md).
- **Frontmatter is `name`, `description` and `license` only.** Claude.ai rejects most other keys. Descriptions stay under 200 characters until an upload proves the real limit.
- **Every skill gets a line in the top-level `README.md`** linking to its folder.
- **Version.** Bump `version` in `plugin.json` for every release, and tag the release `v` plus that version. Installed copies only update when it changes, and the release workflow refuses a tag that does not match.
- **Before a release,** re-confirm each skill's check set against the organisers' pages and run it again (see [`tests/find-events/README.md`](tests/find-events/README.md)).
- **Writing.** UK English. No em-dashes, en-dashes or curly quotes. No "about" or "around" before a number: state it, or say where it comes from. Plain words over jargon.
- **No email address anywhere**, metadata included. LinkedIn is the contact route.
- **Expected values in tests come from outside the code.** The check set's answer key is written from the organisers' own pages, never from a checker's output.
