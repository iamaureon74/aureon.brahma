# security audit — brahma.asherin.com (2026-11-18)

source: external header scan (B+, 80/100) plus a review of `vercel.json`,
`packaging/web/_headers` and the service worker.

| # | finding | severity | status |
|---|---------|----------|--------|
| 1 | CSP `connect-src` allowed `http://localhost:*` and `http://127.0.0.1:*` (A02 · CWE-319) | medium | fixed |
| 2 | no `upgrade-insecure-requests` | low | fixed |
| 3 | HSTS without `preload` | low | fixed |
| 4 | no `manifest-src`, `X-Permitted-Cross-Domain-Policies`, `Origin-Agent-Cluster` | low | added |
| 5 | service worker registered without explicit scope or cache rules (A05 · CWE-16, informational) | info | hardened |

## what changed

- `vercel.json` and `packaging/web/_headers`: `connect-src 'self' https:` and
  `upgrade-insecure-requests`; no `http://` source remains. `manifest-src
  'self'` added.
- HSTS `max-age=63072000; includeSubDomains; preload`; `X-Permitted-Cross-
  Domain-Policies: none`; `Origin-Agent-Cluster: ?1`; `X-DNS-Prefetch-Control: off`.
- `apps/brahma-web/index.html`: the worker is registered with `scope: './'`
  and `updateViaCache: 'none'`. the loader that registers it is still moved to
  an external file with an SRI hash by `packaging/web/secure_site.py`, so the
  only worker that can be installed is the first-party `sw.js`.

## behavior change

the browser build can no longer call the local Ollama / LM Studio presets on
`http://localhost`. those remain available in the desktop app. a public https
page calling loopback was already restricted by chrome's private/local network
access rules, so this mainly removes the attack surface.

## verified

- `vercel.json` parses; the loader script passes `node --check`;
  `apps/brahma-web/src/main.rs` still finds `serviceWorker` in the page.
- the wasm build itself is unchanged.
