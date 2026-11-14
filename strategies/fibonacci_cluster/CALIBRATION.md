# Fibonacci Cluster — Calibration

Cluster-width sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-18, same
costs/sizing, 2xATR stop, 3xATR trail, 200-bar max hold). The sweep
re-runs `add_indicators(df, cluster_width_atr=X)` only — signals
and risk are unchanged. The shipped 0.5x ATR width already produces
clusters on 86–90% of bars, so the 0.75x relaxation the brief
allowed was not needed for signal formation; it is reported here
purely as a sensitivity check.

| Cluster width | Coin | Trades | Win% | Net $ | Sharpe | PF | Bars w/ cluster |
|---|---|---|---|---|---|---|---|
| 0.5x ATR (shipped) | BTC | 283 | 30.0% | -$4,346 | -4.04 | 0.55 | 4,475 |
| 0.5x ATR (shipped) | ETH | 341 | 30.8% | -$3,054 | -2.20 | 0.73 | 4,598 |
| 0.5x ATR (shipped) | HYPE | 337 | 32.0% | -$2,309 | -1.54 | 0.81 | 4,722 |
| 0.5x ATR (shipped) | **Combined** | **961** | — | **-$9,709** | — | — | — |
| 0.75x ATR | BTC | 231 | 29.9% | -$4,525 | -4.45 | 0.45 | 4,731 |
| 0.75x ATR | ETH | 287 | 31.4% | -$1,657 | -1.03 | 0.86 | 4,753 |
| 0.75x ATR | HYPE | 288 | 28.8% | -$1,785 | -1.14 | 0.86 | 4,901 |
| 0.75x ATR | **Combined** | **806** | — | **-$7,967** | — | — | — |

## One-line verdict

- **0.75x ATR:** less bad combined (-$7,967 vs -$9,709) and fewer
  trades (806 vs 961) — a wider cluster band merges more levels,
  so the nearest cluster sits slightly further from the close and
  the touch test fires less often on noise. Still negative on all
  three coins.
- **0.5x ATR:** the shipped a-priori default, negative everywhere
  (-$9,709 combined).
- **Shipped decision:** keep the specified 0.5x ATR cluster width
  regardless. The 0.75x setting looks less bad only in-sample on
  this one 7-month window, and switching to it *because* it trims
  the loss would be in-sample selection. The honest read: width
  moves how often noise triggers a touch, not whether the bounce
  works — the cluster-bounce premise itself fails on this window
  at either width.
