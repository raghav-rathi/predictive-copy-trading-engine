"""Hyperliquid copy-trading module.

Mirrors profitable Hyperliquid perps traders in near-real-time, driven by
the same philosophy as the rest of this repo: SCORE THE WALLETS, DON'T
BLIND-COPY.

Pipeline:
    targets.py    scored target list (kind: wallet|vault) + single-operator
                  clustering
    scorer.py     realized-PnL profiler: time-weighted WR/PF, consistency,
                  min-sample guard -> 0-100 score
    sizing.py     proportional mirror + fractional-Kelly cap (shrinks only)
    mirror.py     WS userFills loop, fill-hash dedup, intent aggregation
                  (fragmented fills -> one copyable intent), open/close/
                  proportional logic, per-coin serial queues
    exits.py      independent hard stops: SL / trailing SL / TP / max-hold /
                  max-age (side-aware); pre-close state sync
    reconcile.py  periodic drift check vs target clearinghouseState +
                  startup position sync
    paper.py      paper ledger, shadow positions, decision log, live gate
    risk.py       4-layer circuit breakers (trade / target / daily / kill)
    notify.py     trade/breaker/error events (log or Telegram backend)

Paper mode is the default and the only mode that runs end-to-end here.
See README.md in this directory.
"""
