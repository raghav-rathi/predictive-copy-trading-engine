# Detrended Price Oscillator — Calibration

DPO-period sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, pinned batch-46 window
2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC, 6,136 bars
BTC/ETH, 6,134 HYPE; same costs/sizing, 2xATR stop, 3xATR
trail, 60-bar max hold). The DPO period is the strategy's
natural knob: which cycle length the oscillator is tuned to
— the displacement is recomputed as period/2 + 1 for each
value (10 → 6 bars, 20 → 11, 40 → 21). The sweep re-runs
`add_indicators(df, period=X)` only — signals and risk are
unchanged.

| DPO period | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 10 | BTC | 674 | 22.8% | -$6,380 | -4.23 | 0.63 | -$9.47 |
| 10 | ETH | 708 | 23.0% | -$5,101 | -2.77 | 0.74 | -$7.20 |
| 10 | HYPE | 664 | 26.2% | -$1,407 | -0.38 | 0.94 | -$2.12 |
| 20 (shipped) | BTC | 462 | 21.0% | -$5,087 | -3.24 | 0.65 | -$11.01 |
| 20 (shipped) | ETH | 482 | 21.2% | -$3,218 | -1.63 | 0.80 | -$6.68 |
| 20 (shipped) | HYPE | 454 | 23.6% | -$644 | -0.01 | 0.96 | -$1.42 |
| 40 | BTC | 284 | 26.1% | -$2,175 | -1.26 | 0.80 | -$7.66 |
| 40 | ETH | 346 | 20.2% | -$3,185 | -1.94 | 0.74 | -$9.20 |
| 40 | HYPE | 304 | 22.7% | -$514 | -0.01 | 0.95 | -$1.69 |

## One-line verdict

- **10:** combined -$12,887 (2,046 trades) — worst combined;
  the shortest oscillator crosses most and pays most in fees.
- **20:** the shipped setting — combined -$8,949 (1,398
  trades). HYPE nearly breakeven (-$644, PF 0.96) but BTC
  still -$5,087.
- **40:** combined -$5,874 (934 trades) — least-bad combined
  and best on BTC (-$2,175), but still a clear loser on
  every coin, and the improvement tracks the falling trade
  count (2,046 → 1,398 → 934) more than any signal quality.
- **Shipped decision:** keep the specified DPO(20) as the
  registry config regardless. It was fixed before any
  backtest was run; adopting 40 *because* it loses less
  in-sample would be in-sample selection on a monotone
  trade-count effect that never reaches breakeven at any
  value. The honest read: the zero-line cross loses at
  every period, and longer just loses slower.

## Batch-46 audit (2026-11-25)

- **Lookahead audit:** no lookahead found. DPO[i] =
  close[i] − SMA20[i − 11]: the SMA uses closes through bar
  i − 11 only, so every value on bar i uses data through bar
  i's close only. The centered StockCharts plotting
  convention (price minus the SMA ending 11 bars in the
  future) is deliberately NOT implemented — that version is
  lookahead and is documented as such in the README.
  Signals use `crossed_above`/`crossed_below` on bars i and
  i−1 only. The truncation test (`test_no_lookahead_truncation`)
  confirms indicator and signal values at bar j are identical
  whether computed on the full frame or on the frame truncated
  at j.
- **Source check:** the StockCharts ChartSchool DPO article
  (found via web search 2026-11-25; the search index returns
  the ChartSchool page at the gitbook PDF URL cited in the
  registry) confirms the 20-period default, the 20/2 + 1 =
  11 displacement, and that DPO "is not designed for momentum
  signals". The causal reading implemented here matches the
  MetaStock "Technical Analysis from A to Z" formula quoted
  in the same search ("subtract the moving average (n/2)+1
  days ago from the closing price"). No URL was guessed: the
  cited URL is verbatim from the search results.
- **Tests:** 14/14 pass (`python3 -m unittest
  strategies.detrended_price_osc.test_detrended_price_osc`).
- **No parameter was tuned to PnL.** DPO period stays 20.
