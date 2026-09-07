# The grading rubric

Ten items, each scored 0 to 2 (half points allowed) by one reviewer who read every
full diff with file-level evidence and re-ran the chat test suites in every
worktree. Raw scores (max 20) are halved to the 0–10 scale used in the article.
Per-run item scores are in `data/experiment-data.json` under `runs[].rubric`.

1. Intent gate catches all 7 openers in both languages
2. Step machine, parsers, skips known data
3. Reuses the wizard's geocoder, numbered pick of at most 3
4. 'no sé' falls back to the published sample size
5. Lead and report through the real libraries, correct money
6. Prompt cleanup: no price dump, no early visit, 'nosotros'
7. Interruption answered, then the pending question repeated
8. Tests: openers, happy path, unknown consumption, interruption, ambiguity
9. Gate green, lane respected, trailer, not merged
10. Real end-to-end transcript and an honest report
