# Which agent is the best subagent?

The protocol, prompt, rubric, data and session-log scripts behind the article
[Which agent is the best subagent?](https://aiandtractors.com/coding-agent-feature-eval/):
one real task from a private repo was given to six agent configurations —
Claude Code on Fable 5.1 (low), Opus 5 (low) and Sonnet 5 (medium), GLM 5.3
through the Claude Code harness, GLM 5.3 through ZCode, and Codex CLI on
GPT-6 Astra (low) — each in its own git worktree cut at the same base commit,
same prompt, same gate. One reviewer graded all branches on a 10-item rubric
with file-level evidence and re-ran the tests; token burn was measured from
each harness's own session logs and priced at list rates. A
[dated addendum](#addendum-2026-09-08) below adds two more runs on the same
base commit and prompt: GLM 5.3 Flash via ZCode and Meta's Muse Spark 1.3
Contributor via Muse Code.

The feature under test lives on [Bruno](https://usabruno.com/), a solar-quote
platform; the host repository is private and is **not** part of this repo.

## Results (2026-09-07)

| Run | Score /10 | Wall time | API-equivalent $ | Subscription $ | Share of a week |
|---|---:|---:|---:|---:|---:|
| Fable 5.1 low · Claude Code | 9.75 | 29 min | $15.85 | $0.85 | 3.7% |
| Opus 5 low · Claude Code | 9.50 | 29 min | $18.81 | $1.07 | 4.7% |
| GLM 5.3 · Claude Code (default, thinking on) | 9.00 | 41 min | $5.64 | $0.24 | 1.9% |
| GLM 5.3 · ZCode (default, reasoning: max) | 8.75 | 36 min | $4.39 | $0.19 | 1.5% |
| Codex GPT-6 Astra low · Codex CLI | 7.75 | 14 min | $6.05 | $0.17 | 0.4% |
| Sonnet 5 medium · Claude Code | 7.00 | 41 min | $13.57 | $0.78 | 3.4% |
| GLM 5.3 Flash · ZCode *(addendum)* | 8.75 | 59 min | $0.66 | $0.03 | 0.2% |
| Muse Spark 1.3 Contributor · Muse Code *(addendum)* | 9.00 | 33 min | $0.09 | $0.09 | — pay as you go |

Full per-run data — deduplicated token counts, per-model cost components with
cache-TTL split, list prices, plan allowances, per-item rubric scores, grader
notes — is in [`data/experiment-data.json`](data/experiment-data.json), the
same file the article's charts are built from.

**Measurement correction (2026-09-07).** The first published numbers
double-counted usage: Claude Code transcripts repeat assistant records with the
same message id (session resumes, multi-block messages) — 248 duplicated
records for Sonnet, 118 for Fable, 162 for Opus, 192 for GLM; the harness's
automatic security-review calls to Opus 4.7 were folded into the main model and
priced at its rates; all cache writes were priced at the five-minute rate when
the primary runs wrote one-hour cache; and Codex/ZCode input totals were
treated as fresh input although they include cached input. The corrected table
above deduplicates by message id, prices every model (including the automatic
reviews) at its own rates, splits cache writes by TTL, subtracts cached from
input for Codex/ZCode, and counts Codex's final cumulative usage once. The
cost-quality frontier on these numbers is Codex Astra low → GLM 5.3 via ZCode
→ GLM 5.3 via Claude Code → Fable 5.1 low. Plan allowances are inherited estimates, not remeasured
by the correction — subscription dollars are modeled allocations, not observed
charges. `scripts/audit.py` reproduces the correction from the original logs.

## Addendum (2026-09-08)

Two more runs, same base commit (`ad1feac`), same prompt, same rubric and the
same Fable 5.1 reviewer; full evidence in the last two sections of
[`grading.md`](grading.md).

- **GLM 5.3 Flash via ZCode: 17.5/20 (8.75/10), $0.03 of subscription per
  task.** It ties full GLM 5.3 on the same harness at roughly a quarter of the
  cost and becomes the cheapest point on the chart. The prompt cleanup was
  half-done (six surviving name mentions, no "nosotros" rule), which is most
  of the gap to the full model's 18.
- **Meta Muse Spark 1.3 Contributor via Muse Code: 18/20 (9.00/10), $0.09 —
  pay as you go.** An external-provider run, so the prompt was redacted (no
  team names; the live end-to-end check ran on the demo data pack with no
  private keys, and the missing geocoder key is disclosed, not faked). It ties
  GLM 5.3 via Claude Code on score at about a third of the cost — with the
  deepest test suite of the eight runs — so GLM via Claude Code leaves the
  cost-quality frontier. Cost accounting: usage from the Muse Code session
  export, cache semantics verified by a live probe (a repeated call keeps
  `prompt_tokens` unchanged and reports the cached share separately — the
  Anthropic/OpenAI subset convention), priced at list rates with no
  subscription to amortize.
- A third addendum run, GLM 5.3 Flash through the Claude Code harness, was
  attempted twice and died both times inside the GLM plan's request-rate and
  five-hour usage limits; its final attempt and this README's frontier wording
  settle after that resolves.

The frontier after the addendum: GLM 5.3 Flash via ZCode → Muse Spark 1.3 via
Muse Code → Fable 5.1 low.

## Caveats — what you cannot reproduce from this repo

These matter, so they lead the README. **We did not run the test on anything
you can download here.**

1. **The code under test is private and not included.** The task prompt targets
   a private repository (a bilingual solar-quote platform). You cannot run
   exactly this test from this repo — there is no `git clone` that reproduces
   the experiment. What is published: the prompt, the rubric, the results data,
   and the scripts that turned harness session logs into comparable token
   counts.
2. **The prompt is lightly redacted** from the ones actually sent: absolute
   local paths, private runtime-pack and `.env` instructions, and a team
   member's name were removed or replaced; per-run identifiers (worktree,
   branch, port, commit trailer) were lifted into placeholders. See
   [prompts/task-prompt.md](prompts/task-prompt.md) for the redaction notes.
3. **One graded branch per configuration.** ZCode cost and token usage are
   the arithmetic mean of two sessions: $0.21 and $0.17 become $0.19 per
   session. The 8.75 score and 36-minute wall time describe their shared final
   branch, not independently graded attempts. The other configurations each
   have one measured run. There is no statistical reliability claim.
4. **Scores are one grader's judgment** on a fixed rubric, with file-level
   evidence, spot-checked by a second pass that re-ran each branch's test gate
   and reviewed the diffs. A different grader would land within a point or two
   on most runs; the ordering at the top and bottom was stable across both
   passes.
5. **Harnesses count tokens differently.** Numbers come from each harness's
   own session counters (Claude Code JSONL transcripts, ZCode's SQLite usage
   tables, Codex session rollouts). Cache accounting differs slightly between
   them; cross-harness comparisons are honest but not metrological.
6. **Everything drifts.** Models, harness versions, quota mechanics and list
   prices were as of 7 September 2026. The subscription dollars depend on plan
   allowances that providers change without notice.
7. **The live end-to-end checks depended on third-party APIs** (geocoding,
   LLM endpoints) with machine-local keys; some runs hit rate limits or
   IP-locked keys during their live check, which the grader took into account.

## Run your own

The pattern transfers to any repo you own:

1. Pick one real, graduated task — hard enough to score in halves, with an
   existing test gate. Write it as one deterministic prompt (see
   [prompts/task-prompt.md](prompts/task-prompt.md)): lanes that must not be
   touched, libs that must be reused, the exact gate commands, a live
   end-to-end check, and a report format.
2. Cut one worktree per configuration at the same base commit; give each its
   own port. Launch all runs in parallel.
3. Grade every diff against a fixed rubric with file-level evidence, and re-run
   the gate yourself — treat the agents' self-reports as claims, not evidence.
4. Measure burn from session logs, not from vibes:
   `scripts/usage.py` sums a Claude Code session JSONL (message-id deduplicated), `scripts/audit.py` is the reference correction pass, and the README in
   `scripts/` has the ZCode SQLite query and the Codex rollout scan.
5. Price tokens at list rates and convert to subscription dollars through your
   plan's measured monthly allowance — the formula is one line, in the article.

## Contents

```
prompts/task-prompt.md     the prompt every agent received (redacted; see notes)
rubric.md                  the 10-item grading rubric
data/experiment-data.json  per-run tokens, prices, scores, notes (powers the article)
scripts/usage.py           token usage from a Claude Code session JSONL
scripts/extract.py         same, plus a long-report extraction mode
scripts/generate-chart.py  standalone PNG, SVG and PDF from the published data
charts/                   downloadable graph
data/cost-audit.json       accounting evidence and preserved session observations
scripts/README.md          where each harness's session logs live + queries
```

Generate the chart with `python3 scripts/generate-chart.py` (requires NumPy and
Matplotlib). The log audit requires the original local logs and adapted paths;
they are not distributed with this public repository.

## License

[MIT](LICENSE) © Ivan Braun. The article and charts are at
[aiandtractors.com/coding-agent-feature-eval](https://aiandtractors.com/coding-agent-feature-eval/).
