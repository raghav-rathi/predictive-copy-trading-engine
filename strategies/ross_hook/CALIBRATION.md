# Ross Hook Continuation — Calibration

Pivot-length sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-20, same costs/sizing,
1.5xATR stop, 2.5xATR target, 60-bar max hold). The pivot length is the
pattern's timeframe knob: shorter pivots = more (noisier) 1-2-3s, longer
pivots = fewer, more significant swings.

| Pivots | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 5 (shipped) | BTC | 109 | 39.4% | -$709 | -0.51 | 0.90 | -$6.50 |
| 5 (shipped) | ETH | 99 | 30.3% | -$2,452 | -2.64 | 0.63 | -$24.77 |
| 5 (shipped) | HYPE | 119 | 37.0% | -$760 | -0.62 | 0.90 | -$6.39 |
| 3 | BTC | 156 | 41.0% | -$327 | -0.08 | 0.97 | -$2.09 |
| 3 | ETH | 157 | 33.1% | -$2,692 | -2.22 | 0.72 | -$17.15 |
| 3 | HYPE | 174 | 38.5% | -$802 | -0.49 | 0.93 | -$4.61 |
| 7 | BTC | 77 | 28.6% | -$2,092 | -2.07 | 0.61 | -$27.16 |
| 7 | ETH | 65 | 36.9% | -$920 | -1.06 | 0.80 | -$14.15 |
| 7 | HYPE | 92 | 35.9% | -$1,151 | -1.18 | 0.81 | -$12.51 |

## One-line verdict

- **3-bar:** combined -$3,821 on 487 trades — least bad, and closest to
  breakeven on BTC (-$327, PF 0.97, Sharpe -0.08). More pivots catch
  more hooks, but the edge doesn't appear.
- **7-bar:** combined -$4,163 on 234 trades — worst on BTC (-$2,092, win
  rate collapses to 28.6%). Bigger swings, fewer setups, no payoff.
- **Shipped decision:** keep the specified 5-bar pivots. No setting is
  positive combined, so there is no in-sample winner to be tempted by;
  the sweep's real message is that pivot length moves trade count far
  more than expectancy — the pattern's problem is setup quality, not
  the pivot window.
