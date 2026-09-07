# Where each harness keeps its usage numbers

All three harnesses were pointed at their own worktree; each was measured from
its own records, then the totals were priced at list rates.

## Claude Code (and GLM through the Claude Code harness)

Session transcripts: `~/.claude/projects/<project-dir>/<session>.jsonl`
(one directory per working directory, `/` → `-`). Sum tokens with
`usage.py`, or read the final assistant messages with `extract.py report`.

## ZCode

Usage tables in SQLite:

```sh
sqlite3 -header ~/.zcode/cli/db/db.sqlite "
  select session_id, model_id, count(*) requests,
         sum(input_tokens), sum(output_tokens),
         sum(cache_read_input_tokens), sum(cache_creation_input_tokens)
  from model_usage where session_id in (<your session ids>) group by 1, 2"
```

Session ids and working directories are in the `session` table. Beware: more
than one session can share a worktree (in this experiment, one lane was
accidentally launched twice; the data uses the reconciled single-run figures).

## Codex CLI

Session rollouts: `~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl`. Token totals
appear in `token_count` events (`total_token_usage`); prefer per-call deltas
over cumulative session counters, which are resume-inherited and inflate.

## The correction pass

`audit.py` is the reference extractor: it deduplicates Claude Code assistant
records by message id across files (resumed sessions repeat history; multi-block
messages repeat usage), prices each model separately — including the harness's
automatic security-review calls to Opus 4.7 — splits cache writes into
five-minute and one-hour tiers via `usage.cache_creation.ephemeral_*`, and
counts Codex's final `turn.completed` cumulative usage once. `usage.py` carries
the same message-id dedup for quick checks.
