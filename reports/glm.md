**Done — chat estimator shipped on `eval-glm`.**

- **Estimator flow** (`modules/nimba/estimate-flow.js`, ~450 lines): price/install gate → address (same `lib/geocode`, numbered pick of ≤3 on ambiguity) → ownership → consumption (kWh / `$45.000` / `45 mil` / «no sé»→published 14-panel sample) → intent → name → contact, one voseo question per message, es/en. Completion runs the exact `/api/quote/analysis` path (`customerLeads.create`→`setContact`→`studyFor`→`reportAnalysis`→`setAnalysis`), now shared via extracted `lib/quote-analysis.js`, then posts summary (panels, kWp, plan US$, yearly savings) + `Ver mi informe` link to the thread. No chat-only price formula anywhere.
- **Prompt/guardrails**: no reference-plan dump (one-line plan price only on explicit ask), never a visit before the report, «nosotros» voice ([installer] removed from prompt, escalated note, canned replies untouched), 1–2 sentences; unrelated mid-flow questions answered with the pending step re-asked in the same reply.
- **Tests**: new `test/chat-estimate.test.js` (7 openers, full happy path to `/quote/results/` link + `preliminary-ready` lead, «no sé», interruption, ambiguous pick, parser units); caught and fixed two real bugs (`\b` after accented char never matches «no sé»; US `45,000` parsing). Updated 5 price-openers in `chat-replay` + 1 assertion in `chat-web-thread`. Fixed my own regressions: `privateRoofFrame` import left behind in server.js, and publication-scan hits (literal phone/email in test/copy, symlinked `private-pack` breaking the `.gitignore` pattern).

**Gate**: tests 1062/1076 pass — the 14 fails pre-exist at base `ad1feac` (verified in a temp worktree; homepage/dawn-asset tests whose fixes landed on master after this branch was cut). Build OK; scans pass (900 source files, 199 dist).

**E2E on :6596, private pack** (no Places/OpenRouter key on this machine; geocode served from the production cache — real-looking address, private store only):

```
IN : hola, quiero instalar paneles solares en mi casa, cuánto sale?
OUT: ¡Dale, Sofía! Te lo estimo acá mismo, con los paneles sobre tu techo. ¿En qué dirección está la casa?
OUT: Por si se corta esta charla: tocá Seguir por WhatsApp … (continuity ask)
IN : Retiro 512, Cariló → OUT: No encontré esa dirección. Pasamela como «Calle 123, Pinamar» y sigo.
IN : es mía → OUT: ¿Cuánto consumís por mes? …
IN : pago como 45 mil por mes → OUT: ¿Qué buscás principalmente: ahorrar en la factura o respaldo ante los cortes?
IN : ahorrar en la factura → OUT: Último paso: ¿a qué mail o WhatsApp te mando el informe?
IN : sofia@ejemplo.invalid
OUT: Estoy armando tu informe con los paneles sobre tu techo…
OUT: ¡Listo, Sofía! Para Calle Ejemplo 123, B7167 Cariló … entran 2 paneles (1,2 kWp). El plan Económico sale US$ 1.995 y ahorrarías unos $ 671.220 por año; el informe completo queda acá:
     LINK: Ver mi informe → https://…/quote/results/b14af8a9…?t=R4mkT9…
IN : cuánto sale el plan con baterías? → OUT: (fallback — no model key on this machine; prompt's reportReady rule governs with one)
```

2 panels is correct math: 45 mil ARS ÷ grid price → 136 kWh/month over the real catalog. Server killed.

**Judgment calls**: no password/account — report protected by `?t=` token like the wizard's share link; `followupConsent:true` (visitor asked for the report in-thread), `marketingConsent:false`; `source:'site-chat'`, conversationMode on; name step auto-skipped from thread name (visible in transcript); widget rendering of the result link left to the widget agent (it rides the API `links` payload, same shape as the WhatsApp action link).

**Commits** (`eval-glm`, worktree `bruno-eval-glm`, both trailers on all three): `6c63025` WIP · `f182a09` flow+tests · `7139ff1` fixes. Not merged to master.

**Bottom line**
**Why**: the bot sold like every installer (price list + visit offer); now it sells Bruno's actual product — the estimator — and finishes with the report in-thread.
**Open questions (Q/A)**: Q — pull master into `eval-glm` to clear the 14 pre-existing homepage-test fails? A — recommended no (eval isolation; they're fixed on master).
**Done**: flow, prompt, wiring, store, 6 new tests, gate 4/4, live private-pack e2e, server killed.
**Links**: [report page from e2e](https://127.0.0.1:6596/quote/results/b14af8a9-c8c0-4d40-a19a-748aececfb68) (throwaway, now down) · worktree `bruno-eval-glm`.

**Summary:** Conversational estimator shipped end-to-end on `eval-glm` (3 commits, gate green except 14 pre-existing base fails, live e2e transcript above); nothing needed from you.
