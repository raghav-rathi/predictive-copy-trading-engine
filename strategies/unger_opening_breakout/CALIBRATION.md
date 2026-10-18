# Unger Opening Breakout — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_sweeps.py` (results
only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped 3-bar range | BTC | 287 | 27.5% | -$4,392 | -3.48 | 0.59 |
| shipped 3-bar range | ETH | 276 | 31.9% | -$3,385 | -2.89 | 0.66 |
| shipped 3-bar range | HYPE | 282 | 29.1% | -$3,982 | -3.77 | 0.61 |
| tighter 2-bar range | BTC | 303 | 27.7% | -$4,577 | -3.65 | 0.60 |
| tighter 2-bar range | ETH | 296 | 31.8% | -$3,265 | -2.66 | 0.70 |
| tighter 2-bar range | HYPE | 296 | 31.1% | -$3,894 | -3.55 | 0.63 |

## Verdict

- **Tighter 2-bar range:** a narrower opening range fires slightly more
  trades (the first wiggle crosses sooner) and changes nothing material:
  BTC -4,577 vs -4,392, ETH -3,265 vs -3,385, HYPE -3,894 vs -3,982.
  The range width is not the binding constraint; the absence of session
  structure in 24/7 crypto is.
- **Shipped decision:** keep the specified 3-bar opening range as the
  registry config. The variant is diagnostic only; both readings lose on
  every coin.
