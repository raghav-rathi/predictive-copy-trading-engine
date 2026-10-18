# Taylor 3-Day Cycle — Calibration

Sweep on the same Hyperliquid 1h data as BACKTEST.md (BTC/ETH/HYPE,
2026-03-14 → 2026-10-18, same costs/sizing). One variant against the
shipped config. Throwaway sweep script: `/tmp/batch9_sweeps.py` (results
only; indicators/risk unchanged).

| Variant | Coin | Trades | Win% | Net $ | Sharpe | PF |
|---|---|---|---|---|---|---|
| shipped 0.1xATR tolerance | BTC | 141 | 27.0% | -$4,074 | -2.69 | 0.57 |
| shipped 0.1xATR tolerance | ETH | 120 | 33.3% | -$482 | -0.09 | 0.95 |
| shipped 0.1xATR tolerance | HYPE | 159 | 25.8% | -$1,417 | -0.67 | 0.89 |
| wider 0.25xATR tolerance | BTC | 151 | 28.5% | -$3,590 | -2.11 | 0.66 |
| wider 0.25xATR tolerance | ETH | 134 | 32.8% | -$900 | -0.29 | 0.92 |
| wider 0.25xATR tolerance | HYPE | 171 | 25.7% | -$1,527 | -0.70 | 0.88 |

## Verdict

- **Wider 0.25xATR tolerance:** fires a few more trades per coin and trims
  the BTC bleed (-$3,590 vs -$4,074, PF 0.66 vs 0.57) -- but it makes ETH
  and HYPE worse (-$900 vs -$482; -$1,527 vs -$1,417). The tolerance is
  not the binding constraint; the dip-to-prior-low reversal premise is.
  Widening the net catches more of the same losing setups.
- **Shipped decision:** keep the specified 0.1xATR tolerance as the
  registry config. The variant is diagnostic only; neither reading has an
  edge.
