# The task prompt

One prompt was given to every agent, verbatim; only the placeholders differed
per run: `{WORKTREE}` / `{BRANCH}` (an isolated git worktree per agent, all cut
at the same base commit), `{RUN}` (a short run id used in commit messages),
`{PORT}` (a per-run port for the live end-to-end check), and the commit trailer
(naming the model that authored the run).

> You are working in the git worktree `{WORKTREE}` (branch `{BRANCH}`) of a private Node app (a solar-quote platform). cd there first; never touch the main checkout. Live sibling sessions exist, so: right after your first coherent edit run `git commit -qam "WIP chat estimator ({RUN})"` and keep committing; never touch the main tree. Another agent is redesigning the widget CSS/markup in `modules/nimba/widget.js` and copy in `support-copy.js`: do NOT edit those two files. Your lane is `modules/nimba/responder.js`, `modules/nimba/chat-routes.js`, `modules/nimba/store.js`, `modules/nimba/guardrails.js`, new files under `modules/nimba/`, and tests.
>
> PROBLEM: the public chat bot ignores our product. Asked "i want to install solar, how much?" it dumps the three reference plans with prices and then offers a site visit "morning or afternoon", like every other installer. The product IS the AI estimator: the wizard at /quote/* that takes address, ownership, consumption/bill, intent and contact, then produces a report at `/quote/results/<id>?t=<access>` with panels on the roof and prices. The chat must do the same thing in conversation form and end by showing the report in the thread.
>
> Read first: the CRM/deals/contacts requirements doc section D, `modules/nimba/responder.js` (system prompt, facts(), answer()), `modules/nimba/chat-routes.js`, the server handlers for `/api/quote/addresses`, `/api/quote/contact`, `/api/quote/analysis`, and `lib/customer-leads.js`, `lib/customer-quote.js` (preliminaryQuote), `lib/quote-sessions.js`, and the wizard client to see which fields each step collects (intent/ownership/bill/location/roof/contact are rendered there).
>
> DESIGN (make it deterministic, not prompt-only):
> 1. Add an intent gate before the LLM: when a message asks about price/cost/quote/panels/installing ("cuánto cuesta", "cuánto sale", "precio", "presupuesto", "quiero paneles", "quiero instalar", "how much", "quote", "price", and reasonable variants, both languages), start or continue an `estimate` flow stored on the thread (`thread.estimate = { step, data }` via the atomic store, with a normalizer default).
> 2. Flow steps, one question per message, short voseo Spanish (English mirrored): address → resolve via the same geocoder `/api/quote/addresses` uses (call the lib directly, not HTTP); if several matches, ask which one with a numbered list of at most 3; → owner/renter/planning → monthly consumption in kWh OR monthly bill amount (accept either; parse "$45.000", "45 mil", "300 kwh") → what they are after (ahorrar / respaldo ante cortes / ambos) → name → email or WhatsApp (whichever they give; validate). Skip any step whose data is already known (name from thread, whatsapp from a verified thread, address mentioned in the message). Allow "no sé" on consumption: fall back to the published residential sample size exactly as the wizard does (never fill the roof just because area exists).
> 3. On completion: create the lead server-side using the same libs as `/api/quote/contact` and `/api/quote/analysis` (customerLeads.create → setContact → run the same roof/analysis path → setAnalysis) WITHOUT requiring a password or customer account (the results page is protected by the `?t=` access token; that is the judgment call, note it in your report). Reuse the pricing libs through the existing analysis function; never add a chat-only price formula. Then post an assistant message with a 2-sentence summary (panel count, kWp, best plan price in USD with natural formatting, yearly savings if available) and a link `{ label: 'Ver mi informe', href: <absolute https result URL on the request host> }` using the thread's existing `links` shape. Analysis can take several seconds: post "Estoy armando tu informe…" first if the route's response model allows, otherwise just await.
> 4. The LLM prompt: remove the "reference options" price dump behaviour. Prices only after the report or when the visitor explicitly asks for plan prices, and even then one line and an invitation to estimate. Never offer a visit before the report exists; after the report, one soft offer. Speak as "nosotros", never name team members; 1–2 sentences per reply.
> 5. If the flow is interrupted by an unrelated question, answer it via the LLM and then repeat the pending question in the same reply.
>
> TESTS: extend the chat test suites with the demo data pack: each of these openers must enter the flow and get the address question, never a visit or price list: "quiero instalar solar, cuánto sale?", "cuánto cuesta", "precio para mi casa", "quiero paneles", "how much", "i want to install solar, how much?", "me pasás un presupuesto?". Then a full happy path through to a message containing a `/quote/results/` link, an "I don't know consumption" path, an interruption path, and an ambiguous-address path. Stub the geocoder and the LLM in tests (look at how existing tests stub `fetchImpl`).
>
> Gate before finishing:
> ```
> BRUNO_DATA_PACK=demo node --test test
> BRUNO_DATA_PACK=demo node build.js
> node scripts/publication-scan.js --manifest docs/publication-manifest.json
> node scripts/publication-scan.js dist
> ```
> Also run one real end-to-end conversation against a throwaway server from your worktree on port {PORT} with the private runtime pack (loads the repo's private .env; redacted here), and drive the public chat API with curl using a real-looking address in the service area, and paste the resulting transcript (text only) in your report. Kill the server after.
>
> Commit on your branch with a trailer naming the model that authored the run. Do NOT merge to the main branch. Report: branch, worktree path, commits, gate output summary, the e2e transcript, judgment calls, anything left undone.

## Redactions

The published prompt is lightly redacted from the ones actually sent. Local
absolute paths became placeholders or repo-relative paths; the private runtime
pack and `.env` sourcing instructions were summarized; a team member's name in
the voice rule was replaced with "team members"; the per-run commit trailer and
private session URL were removed. The substance — task, design constraints,
test requirements, gate — is unchanged.
