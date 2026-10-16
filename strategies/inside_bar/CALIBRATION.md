# inside_bar — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-20 → 2026-10-15, same costs/sizing). Two parameters: watch
expiry {2, 3 bars} × target {3, 4, 5x ATR}. Runner: `/tmp/batch7_run.py`
(results in `/tmp/batch7_results.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped (expiry 2, tgt 4) | BTC | 181 | −$1,633 | −1.05 |
| shipped (expiry 2, tgt 4) | ETH | 187 | −$128 | +0.07 |
| shipped (expiry 2, tgt 4) | HYPE | 154 | +$953 | +0.83 |
| expiry 2, tgt 3 | BTC | 215 | −$1,159 | −0.74 |
| expiry 2, tgt 3 | ETH | 214 | −$1,748 | −1.16 |
| expiry 2, tgt 3 | HYPE | 179 | +$247 | +0.34 |
| expiry 2, tgt 5 | BTC | 171 | −$621 | −0.21 |
| expiry 2, tgt 5 | ETH | 168 | −$1,483 | −0.85 |
| expiry 2, tgt 5 | HYPE | 142 | −$386 | −0.01 |
| expiry 3, tgt 3 | BTC | 243 | −$843 | −0.37 |
| expiry 3, tgt 3 | ETH | 243 | −$1,002 | −0.50 |
| expiry 3, tgt 3 | HYPE | 194 | +$260 | +0.34 |
| expiry 3, tgt 4 | BTC | 202 | −$623 | −0.19 |
| expiry 3, tgt 4 | ETH | 210 | −$132 | +0.08 |
| expiry 3, tgt 4 | HYPE | 162 | +$1,289 | +1.03 |
| expiry 3, tgt 5 | BTC | 186 | +$245 | +0.38 |
| expiry 3, tgt 5 | ETH | 185 | −$1,356 | −0.67 |
| expiry 3, tgt 5 | HYPE | 153 | +$1,272 | +1.11 |

## One-line verdicts

- **3-bar watch beats 2-bar everywhere it matters:** expiry 3 / tgt 4
  cuts BTC's loss by ~60% (−$623 vs −$1,633), holds ETH flat, and lifts
  HYPE to +$1,289 (Sharpe 1.03). Hourly breakouts need the extra bar —
  the mother break often comes one bar later than the daily version
  assumes.
- **Target 3 is too tight, target 5 too greedy on ETH:** tgt 3 bleeds
  everywhere (worst combined of any row); tgt 5 helps BTC (+$245) but
  wrecks ETH (−$1,356) and HYPE's edge flattens. Tgt 4 stays the best
  compromise.
- **Verdict:** in-sample, expiry 3 / tgt 4 dominates the shipped
  config. Shipped config stays at the published rule (expiry 2, tgt 4)
  — the expiry-3 improvement is a one-dataset observation, not a rule
  change. If it holds on fresh data, promote it.
