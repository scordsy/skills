# Releasing

The steps for a release, in order. Written after 0.4.2, so each step comes from something that went wrong or nearly did.

## 1. Decide whether the check sets run again

- **A change a check set exercises** (a stage's instructions, its reference files or its script): run that set again, after re-reading the sources behind its answer key. Each set's README says how.
- **A change no check set reaches** (how a skill starts, its description, the docs): don't rerun, if Stefan agrees. Record it in each set's README, as for 0.3.2 and 0.4.2, and test the changed behaviour directly instead (step 2).
- **Say the size first.** The check-account-list and check-claims sets each use close to a million tokens a run. Each set's README gives its last figures.

## 2. Test the change itself

Test what changed, the way a user would meet it. For a change to a skill's first step, make a scratch folder holding the skill under `.claude/skills/<name>/` and run it headless:

```bash
claude -p "/<name>" --setting-sources project --allowedTools "Bash(python3:*)" "Bash(ls:*)" "Read" "Glob" --max-turns 8
```

`--setting-sources project` keeps the installed plugin out of the test. Run it once with only `SKILL.md` in the folder, as a chat's save shortcut leaves it, and once with the full folder, to confirm the normal path still passes.

## 3. Branch, bump, check

1. Branch from the latest `origin/main`.
2. Bump `version` in `.claude-plugin/plugin.json`.
3. Run the four commands in [`CLAUDE.md`](../CLAUDE.md).
4. Build the zips with `scripts/package_skill.py` and confirm each one carries the change.

## 4. Merge and tag

1. Open a pull request and wait for CI to pass.
2. Squash-merge it.
3. Tag the merge commit and push the tag:

   ```bash
   git tag -a vX.Y.Z <merge-commit> -m "vX.Y.Z: what changed"
   git push origin vX.Y.Z
   ```

The release workflow refuses a tag that doesn't match `plugin.json`, runs the checks again, builds the four zips and publishes the release.

**Confirm every push with `git ls-remote origin`.** A push that fails can still look like it worked, for example when its output is piped through `tail`.

## 5. Check what a stranger gets

- **The zips.** Download each from `https://github.com/scordsy/skills/releases/latest/download/<name>.zip`, signed out, and confirm it carries the change.
- **Claude Code.** Install on an empty config and check the version:

  ```bash
  CLAUDE_CONFIG_DIR="$(mktemp -d)" claude plugin install stefancordery-skills --marketplace scordsy/skills
  ```

- **Before a post sends people to the repo,** give a fresh Claude chat the README and follow the install as a stranger would. Use the raw file pinned to the commit: `https://raw.githubusercontent.com/scordsy/skills/<commit>/README.md`. A chat can't open GitHub's `/tree/` pages, and its web tool can serve a copy of a page up to 15 minutes old.

## What people get, and when

- **Claude app users** keep the version they uploaded until they upload the new zip. Nothing updates them.
- **Claude Code users** get it only with auto-update turned on for the marketplace, or by running `claude plugin update stefancordery-skills@stefancordery`.
- **The Claude app has no install from a link.** People upload a zip. A chat's own save shortcut keeps only `SKILL.md` and drops the scripts, which the README warns about and each skill now detects.
- **Some network settings block GitHub's download host,** so Claude may not be able to fetch a zip in a chat. The README puts the direct links first for that reason.
