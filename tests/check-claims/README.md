# check-claims tests

| Folder | What it is |
|---|---|
| [`problem-test/`](problem-test/README.md) | The test of the problem, run before the skill was built: six AI-written drafts and 58 claims traced by hand |
| [`sample-a4/`](sample-a4/README.md) | A sample report built by hand from that test's records. Not a run of the skill |
| [`check-set/`](check-set/README.md) | The check set: two made-up drafts with planted problems, a hand-written answer key, and every run |

A real run on an AI-written article is in [`docs/examples/check-claims/`](../../docs/examples/check-claims/README.md).

The script's own tests are in [`../test_claims.py`](../test_claims.py) and use no network.
