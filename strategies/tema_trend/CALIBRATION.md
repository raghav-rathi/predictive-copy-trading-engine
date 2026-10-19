# TEMA Trend — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-19, same costs/sizing). One variant against the
shipped config: faster TEMA pair (10,30) instead of (20,50) — same
SMA200 regime filter, same 2.5xATR stop / 3xATR trail / 120-bar max
hold. Sweep script: `/tmp/bt_new3.py` (`cal` mode).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped TEMA(20,50) | BTC | 119 | 27.7% | -$1,750 | -2.10 | 0.66 |
| shipped TEMA(20,50) | ETH | 124 | 32.3% | -$250 | -0.16 | 0.95 |
| shipped TEMA(20,50) | HYPE | 98 | 42.9% | +$2,131 | +2.14 | 1.63 |
| TEMA(10,30) | BTC | 218 | 28.0% | -$2,659 | -2.83 | 0.68 |
| TEMA(10,30) | ETH | 216 | 25.9% | -$1,602 | -1.41 | 0.81 |
| TEMA(10,30) | HYPE | 201 | 31.3% | +$99 | +0.15 | 1.01 |

## One-line verdict

- **TEMA(10,30):** worse on every coin — combined −$4,162 on 635 trades
  vs shipped +$131 on 341. The faster cross nearly doubles trade count
  (whipsaw entries into every 1h chop) and, critically, wipes out the
  one bright spot: HYPE drops from +$2,131 (Sharpe 2.14) to +$99
  (Sharpe 0.15). The HYPE edge in the shipped config came from the
  slower pair holding through HYPE's clean trends; the faster pair
  chops those same trends into losses.
- **Shipped decision:** keep the specified TEMA(20,50) + SMA200 as the
  registry config. The variant sweep was run to check sensitivity, not
  to select: the faster pair's uniform underperformance confirms the
  shipped pair is the calmer, less curve-fit-prone choice, and the
  HYPE-only edge is flagged in BACKTEST.md as a single-window result
  rather than adopted as truth.
