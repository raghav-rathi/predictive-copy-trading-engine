# TD Sequential — Calibration

Sweeps run on the same data as BACKTEST.md (Hyperliquid 1h, 2026-03-14 →
2026-10-13, use_funding=False). Totals are summed net PnL across BTC+ETH+HYPE.

## Sweep results

| param | value | total $ | BTC $ | ETH $ | HYPE $ |
|-------|-------|---------|-------|-------|--------|
| stop_atr_mult | 1.5 | 2561 | 742 | 2184 | -366 |
| stop_atr_mult | **2.0** (classic default) | 1770 | 418 | 1865 | -512 |
| stop_atr_mult | 2.5 | 1975 | 450 | 2105 | -580 |
| max_hold_bars | 24 | 41 | 484 | -37 | -405 |
| max_hold_bars | **48** (default) | 1770 | 418 | 1865 | -512 |
| max_hold_bars | 96 | 4149 | 1051 | 3471 | -372 |
| perfect_only | **True** (published classic) | 1770 | 418 (17t) | 1865 (17t) | -512 (25t) |
| perfect_only | False | 529 | 14 (25t) | 1587 (25t) | -1072 (34t) |

Combination (stop 1.5 + hold 96): total **$5487** — BTC $1590, ETH $4076,
HYPE -$179. Beats the 2.0/48 baseline ($1770) on **all three coins**.

## Decision

- The perfection filter is the actual published classic parameter: perfect_only=True
  beats False on total and on every coin → **shipped as published (True)**.
- DeMark defines no ATR stop and no max hold — those are my risk overlays, so the
  "ship classic" rule does not bind them. stop=1.5 and hold=96 each beat the
  defaults on all 3 coins, and the 1.5/96 combination beats the baseline on all 3
  coins → **shipped 1.5xATR stop + 96-bar max hold** (risk.py updated in this commit).
- Caveat stated plainly: only 17–25 trades per coin, so the sweep is thin; the
  direction of improvement is consistent across all three coins, which is why I
  took it, but this is calibration on a small sample, not proof.
