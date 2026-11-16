# FFT Dominant Cycle — Calibration

Top-K sensitivity on the same Hyperliquid 1h data as BACKTEST.md
(BTC/ETH/HYPE, 2026-03-14 → 2026-11-16, same costs/sizing, 1.5xATR
stop, 2.5xATR target, 96-bar max hold). The sweep re-runs
`add_indicators(df, top_k=K)` only — signals and risk are unchanged.

| Top-K | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 1 | BTC | 142 | 38.7% | -$692 | -0.55 | 0.89 | -$4.87 |
| 1 | ETH | 143 | 37.1% | -$912 | -0.81 | 0.85 | -$6.38 |
| 1 | HYPE | 125 | 42.4% | -$1,031 | -1.15 | 0.83 | -$8.25 |
| 3 (shipped) | BTC | 331 | 34.1% | -$5,283 | -5.20 | 0.55 | -$15.96 |
| 3 (shipped) | ETH | 340 | 36.5% | -$2,774 | -2.10 | 0.77 | -$8.16 |
| 3 (shipped) | HYPE | 315 | 42.2% | -$1,784 | -1.39 | 0.85 | -$5.66 |
| 5 | BTC | 498 | 39.4% | -$4,749 | -3.70 | 0.69 | -$9.54 |
| 5 | ETH | 488 | 40.0% | -$2,241 | -1.38 | 0.87 | -$4.59 |
| 5 | HYPE | 476 | 44.5% | -$1,947 | -1.30 | 0.88 | -$4.09 |

## One-line verdict

- **top_k=1:** the least bad setting — 125–143 trades per coin,
  combined -$2,635. A single dominant frequency turns less often,
  so it trades a third as much and bleeds a third as fast. Still red
  on all three coins.
- **top_k=5:** more frequencies, more turns, 476–498 trades per
  coin, combined -$8,937 — no better than shipped, just busier.
- **top_k=3 (shipped):** worst combined (-$9,840) and the worst
  per-trade expectancy on BTC (-$15.96). More reconstructed
  components means more slope turns, and each turn is a lagging
  entry into a drifting cycle.
- **Shipped decision:** keep the specified top_k=3 as the registry
  config regardless. It was fixed before any backtest was run; the
  in-sample ranking (top_k=1 loses least) does not change that, and
  leaning toward top_k=1 *because* it loses least would be
  in-sample selection on a window where no setting works. The honest
  read: the parameter moves how fast the strategy loses, not whether
  it works — the FFT cycle premise itself fails on drifting crypto
  cycles.
