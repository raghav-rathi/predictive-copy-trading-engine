"""Hyperliquid copy-trading module.

Mirrors profitable Hyperliquid perps traders in near-real-time, driven by
the same philosophy as the rest of this repo: SCORE THE WALLETS, DON'T
BLIND-COPY.

Pipeline:
    targets.py    scored target list + single-operator clustering
    scorer.py     realized-PnL profiler (win rate, profit factor, drawdown)
    sizing.py     proportional mirror + fractional-Kelly cap (shrinks only)
    mirror.py     WS userFills loop, open/close/proportional logic
    exits.py      independent hard stops (stop-loss / take-profit / max hold)
    reconcile.py  periodic drift check vs target clearinghouseState
    paper.py      paper ledger, shadow positions, decision log, live gate
    risk.py       daily-loss breaker, kill switch, limits

Paper mode is the default and the only mode that runs end-to-end here.
See README.md in this directory.
"""
