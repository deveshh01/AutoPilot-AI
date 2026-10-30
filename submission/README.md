# TalentFlow PM exercise — submission

| File | What |
|---|---|
| `MEMO.md` | One document with the D5 memo, D1 verdicts, D2 roadmap, D3 metric spec and D4 data audit |
| `findings.csv` | Findings table: claim, metric, value, method, confidence |
| `code/pull.py` | Pulls all 8 tables once (paginated, rate-limited) into `data/` |
| `code/analyze.py` | Produces every number in the memo |
| `analysis_output.txt` | Output of `analyze.py` as run for this submission |
| `PROCESS.md` | Session process notes (from the submission prompt) |

## Re-run

Create a `.env` file in the repo root with these two lines (it is git-ignored):

```
AIRTABLE_TOKEN=...
AIRTABLE_BASE=appYePRAI75PMbQNQ
```

Then run:

```bash
python3 submission/code/pull.py
```

```bash
python3 submission/code/analyze.py
```

You need Python 3.9+ and nothing else (standard library only).
