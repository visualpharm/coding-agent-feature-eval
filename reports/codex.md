Implemented on `eval-codex` in `bruno-eval-codex`. No merge or push; widget and support-copy files untouched.

- **Commits:** `369bf6e`, `a3fe787`, `20a0e0e`, `2b841f1`.
- **Implemented:** persistent estimator intake, address choices, consumption parsing, interruptions, canonical report analysis, and token-protected report links.
- **Verification:** 38 focused tests pass. Full suite: **1,068 passed, 15 failed**—14 homepage/media failures reproduced on the starting revision; one publication test fails on the existing `private-pack` symlink. Build and `dist` scan pass; source scan fails with `EISDIR`.
- **Judgment calls:** no account/password required; contact capture grants no marketing/follow-up consent; unknown consumption uses canonical sample sizing; recommended plan supplies the summary price.
- **Still open:** successful private E2E. Google rejects this Mac’s IP for both stored server keys. Server stopped; no live report was produced.

Actual private-run transcript:

```text
Visitor: quiero instalar solar, cuánto sale?
Bruno: ¿Cuál es la dirección de la casa, con localidad?
Visitor: Avenida Ejemplo 456, Pinamar, Buenos Aires, Argentina
Bruno: No pudimos buscar la dirección. Probá escribirla de nuevo.
```

**Summary:** Estimator committed and focused tests pass; full gate and private E2E remain blocked as detailed above.


USAGE {"input_tokens": 4184934, "cached_input_tokens": 4079104, "cache_write_input_tokens": 0, "output_tokens": 18309, "reasoning_output_tokens": 4180}
