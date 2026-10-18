# Hurst FLD — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_sweeps.py` (results
only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped cascade | BTC | 245 | 29.8% | -$2,281 | -1.81 | 0.75 |
| shipped cascade | ETH | 253 | 28.1% | -$1,927 | -1.15 | 0.76 |
| shipped cascade | HYPE | 259 | 30.9% | -$1,824 | -1.58 | 0.76 |
| FLD20-only entries (no cascade filter) | BTC | 740 | 23.0% | -$6,859 | -4.89 | 0.63 |
| FLD20-only entries (no cascade filter) | ETH | 742 | 25.1% | -$5,986 | -3.87 | 0.66 |
| FLD20-only entries (no cascade filter) | HYPE | 667 | 31.3% | -$608 | -0.15 | 0.97 |

## Verdict

- **FLD20-only entries:** dropping the cascade alignment requirement
  triples trade count and wrecks the book (BTC -$6,859, PF 0.63; ETH
  -$5,986). The cascade filter is doing real work as a churn brake -- it
  keeps ~500 marginal FLD20 whipsaws per coin out of the book. It just is
  not enough to make the strategy profitable.
- **Shipped decision:** keep the specified full-cascade config as the
  registry config. The variant is diagnostic: it confirms the cascade is
  the better of two losing readings, not an edge.
