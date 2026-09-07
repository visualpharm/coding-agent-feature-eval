## 11:57:41 153
Addressing the security finding first — dropping my duplicate origin builder for the repo's single existing helper (no `x-forwarded-host`, always https):

## 12:07:16 233
Both Google server keys are IP-locked to the production host, so Places refuses this machine. I'll run the real server with only that one network call stubbed — everything else (private pack, lead, analysis, pricing, report page) stays real:

## 12:12:23 164
Key hit its OpenRouter daily cap (402), so that last turn fell back. The earlier live run already showed the duplication and the fix is covered by test. Final gate:

## 12:13:28 4739
Server killed, temp base worktree removed. Branch not merged, as instructed.

## Report

**Branch** `eval-opus-low` · **worktree** `bruno-eval-opus-low` · **3 commits** on top of `ad1feac` (`60f216f` WIP, `6932763` the estimator, `30b88bc` two fixes found in the live run). Not merged to master.

**What changed** — new `modules/nimba/estimate.js` (pure state machine + parsers) and `modules/nimba/estimate-deps.js` (the wiring to geocoder/leads/analysis). A deterministic intent gate runs *before* the LLM in `responder.js`; `store.js` persists `thread.estimate` in the same mutation as the reply; `chat-routes.js` passes the request context and posts "estoy armando tu informe…" before the slow analysis. The prompt lost its plan-price dump and its pre-report visit offer, speaks as "nosotros", and never names anyone.

**Gate**
```
node --test test    1065 pass / 14 fail — all 14 verified pre-existing on ad1feac
node build.js       exit 0
publication-scan --manifest docs/publication-manifest.json   passed (900 files)
publication-scan dist                                         passed (199 files)
```
The manifest scan was *broken before I started*: a worktree mounts `private-pack` as a symlink and `.gitignore` only had `/private-pack/`, so the scan died reading it (EISDIR). One line in `.gitignore` fixes it.

**E2E transcript** (port 6594, private pack, real libs):
```
visitante > hola, quiero instalar solar en mi casa, cuánto sale?
bruno     > Dale, lo armamos ahora mismo: te damos un informe con los paneles
            dibujados sobre tu techo y el precio. ¿Cuál es la dirección de la
            propiedad? Calle, número y localidad.
visitante > Avenida Ejemplo 456, Pinamar
bruno     > ¿La casa es tuya, la alquilás, o todavía la estás proyectando?
visitante > sí, la casa es mía
bruno     > ¿Cuánto consumís por mes en kWh, o cuánto te viene la factura de luz?
visitante > pago como 95 mil por mes
bruno     > ¿Qué buscás: ahorrar en la factura, tener respaldo cuando se corta la luz, o las dos cosas?
visitante > las dos cosas, ahorrar y no quedarme sin luz
bruno     > ¿Cómo te llamás?
visitante > Martín
bruno     > ¿A qué mail o WhatsApp te mandamos el informe?
visitante > martin.pruebas@example.com
bruno     > Dame un momento que medimos el techo y armamos el informe.
bruno     > Listo: en tu techo entran 4 paneles, 2,3 kWp. El plan Óptimo sale
            USD 6.923 y en el informe podés cambiar la cantidad de paneles.
            [Ver mi informe] https://…/quote/results/49b559ba-…?t=vDbBjB6N…
```
That URL returns **200** with the token, **404** with a wrong one and **404** with none. The "no sé" run produced exactly 14 panels — the published residential sample — and the backup-intent run recommended Autonomía. The ambiguous-address run offered 3 numbered options and continued on "la 1".

**Two real bugs the live run caught** (both fixed + tested): "la 1" didn't select a candidate, and on an interruption the model re-asked the pending question on top of the one my code appends, so the visitor read it twice.

**Judgment calls**
- **No account, no password.** `/api/quote/contact` forces a customer account; the chat doesn't. The report is protected by the lead's `?t=` token — the same capability that already protects the emailed report. Flagging it because it's the one place the chat is weaker than the wizard.
- The report link is built with `server.js#absoluteQuoteUrl`, not my own host builder. A background review flagged host-header injection on my first version; the link carries a lead token, so it now goes through the repo's single existing helper — no `x-forwarded-host`, always https.
- No price formula anywhere in the chat: everything routes through `reportAnalysis` → `lib/pricing.js` / `installer-pricing.js`.

**Left undone** — Bruno's Google Places and Solar server keys are IP-restricted to the production host, so this machine can't call them. The e2e ran with **only `geocode.searchAddress` stubbed** (via `node -r`, never committed); the private pack, lead creation, roof path, pricing and report page were all real. Because Solar was unreachable, the roof study fell back — the panel counts above are the fallback sizing, not a measured Pinamar roof. Worth one run on the prod host to confirm the measured path. Also: the live re-check of the duplicate-question fix fell back to the canned reply because the `bruno-experiments` OpenRouter key returned 402 (daily cap); the fix itself is asserted by test.

**Summary:** the chat now runs Bruno's estimator in conversation and ends with the report in the thread, on branch `eval-opus-low` with the gate green — nothing needed from you unless you want the geocoder/Solar path re-verified on the production host.

