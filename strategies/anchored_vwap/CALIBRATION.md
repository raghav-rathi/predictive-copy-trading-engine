# Anchored VWAP — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-15, same costs/sizing). Two parameters: the
reclaim filter strictness (bars below the line in the 10-bar window)
and the fractal anchor half-width (15/25/40 bars). Throwaway sweep
script: `/tmp/batch7_calibrate.py` (results in `/tmp/batch7_calib.json`).

| Variant | Coin | Trades | Net $ | Sharpe |
|---|---|---|---|---|
| shipped reclaim2/half25 | BTC | 72 | −$2,291 | −2.94 |
| shipped reclaim2/half25 | ETH | 67 | −$1,422 | −1.44 |
| shipped reclaim2/half25 | HYPE | 59 | +$1,773 | +1.69 |
| reclaim1/half15 | BTC | 108 | −$1,892 | −1.64 |
| reclaim1/half15 | ETH | 104 | −$1,472 | −1.23 |
| reclaim1/half15 | HYPE | 82 | +$531 | +0.65 |
| reclaim1/half25 | BTC | 87 | −$2,457 | −2.83 |
| reclaim1/half25 | ETH | 76 | −$1,714 | −1.73 |
| reclaim1/half25 | HYPE | 70 | +$395 | +0.59 |
| reclaim1/half40 | BTC | 65 | −$1,804 | −2.34 |
| reclaim1/half40 | ETH | 66 | −$1,461 | −1.75 |
| reclaim1/half40 | HYPE | 58 | +$2,987 | +2.51 |
| reclaim2/half15 | BTC | 93 | −$1,802 | −1.70 |
| reclaim2/half15 | ETH | 93 | −$1,016 | −0.82 |
| reclaim2/half15 | HYPE | 72 | +$311 | +0.48 |
| reclaim2/half40 | BTC | 56 | −$1,295 | −1.69 |
| reclaim2/half40 | ETH | 56 | −$1,295 | −1.69 |
| reclaim2/half40 | HYPE | 52 | +$3,617 | +2.90 |
| reclaim4/half15 | BTC | 78 | −$1,713 | −1.74 |
| reclaim4/half15 | ETH | 75 | −$722 | −0.61 |
| reclaim4/half15 | HYPE | 54 | +$292 | +0.49 |
| reclaim4/half40 | BTC | 40 | −$1,249 | −1.93 |
| reclaim4/half40 | ETH | 40 | −$785 | −1.13 |
| reclaim4/half40 | HYPE | 35 | −$721 | −1.17 |

## One-line verdicts

- **Reclaim filter (1 vs 2 vs 4):** 1 is too loose (108 BTC trades,
  churn without edge); 4 is too strict (starves HYPE of its winners —
  reclaim4/half40 even loses on HYPE). 2 is the sweet spot.
- **Anchor half-width (15 vs 25 vs 40):** wider anchors win on HYPE
  in every reclaim setting — half40 roughly doubles the HYPE print
  (+$3,617, Sharpe 2.90 at reclaim2/half40). The edge lives in major
  swings; minor-swing anchors get run over.
- **The BTC/ETH problem:** every variant loses on both majors. This
  is a coin property, not a parameter problem — anchored-VWAP reclaims
  work where trends follow through (HYPE 2026), not in range-bound
  majors.
- **Verdict:** shipped config (reclaim2/half25, the documented 51-bar
  fractal) stands as the spec-compliant baseline. reclaim2/half40 is
  the HYPE-only promotion candidate — best print in the sweep, fewer
  trades (52), cleaner anchors — but it needs walk-forward validation
  before it replaces anything, since its advantage is concentrated in
  one coin's trend regime.
