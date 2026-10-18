# Cyber Cycle — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_calibration.py`
(results only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped (alpha 0.07) | BTC | 2,308 | 29.4% | -$9,742 | -17.45 | 0.45 |
| shipped (alpha 0.07) | ETH | 2,328 | 31.1% | -$9,345 | -13.12 | 0.55 |
| shipped (alpha 0.07) | HYPE | 2,197 | 35.4% | -$8,972 | -12.53 | 0.54 |
| variant (alpha 0.10) | BTC | 2,300 | 30.1% | -$9,695 | -16.59 | 0.48 |
| variant (alpha 0.10) | ETH | 2,324 | 32.1% | -$9,270 | -12.62 | 0.55 |
| variant (alpha 0.10) | HYPE | 2,251 | 35.9% | -$9,127 | -13.45 | 0.52 |

## One-line verdict

- **Alpha 0.10:** statistically identical losses on all three coins
  (trade counts within 3%, nets within a few hundred dollars on a
  -$9k base). The smoothing constant is not the problem — the
  cycle-vs-lagged-trigger cross fires ~2,300 times per coin either way.
- **Shipped decision:** keep alpha=0.07 as specified; the sweep is
  diagnostic, not an adoption. Fixing this strategy would mean changing
  the trigger logic (e.g. requiring the cycle to cross with slope
  confirmation, or using Ehlers' dominant-cycle period), not tuning
  alpha.
