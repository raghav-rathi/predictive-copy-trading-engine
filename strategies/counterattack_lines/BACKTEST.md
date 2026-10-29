# Counterattack Lines — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), requested window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and
t <= 1793145600000), $10k start, 1% risk per
trade on the 2xATR stop, 3x leverage cap, 0.045% fee + 0.01%
slippage per side, funding off. WARMUP=20 bars.

**Actual window used (as returned by the cache):** BTC/ETH
first candle 1773525600000 (2026-03-14 22:00 UTC), last candle
1793145600000 (2026-10-28 00:00 UTC) — the cache starts 22
hours after the requested window start, so the first 22 hours
are missing, not shifted. HYPE first candle 1773532800000
(2026-03-15 00:00 UTC), last 1793145600000. The cache also
contains 5 exact-duplicate bars per coin; those were dropped
(keep first) before running, so bar counts below are
deduplicated. Note: the cache was extended to the window end
during this batch's work (it previously ended 2026-10-27
13:00 UTC); the numbers below are on the final cache state.

**Method note:** the backtest ran through the same
`strategies/backtest.py` `run_backtest` harness and the
strategy's own RiskConfig as `scripts/run_strategy_backtest.py`,
but on the window-filtered, deduplicated cache read directly
— the script's `fetch_candles` path would extend the cache
past the window end and change the window, so it was not used.

## Results (shipped config: 5-bar trend, gap-against-trend
open, close within 0.2xATR of the prior close, body ratio
within 2/3–3/2, 2xATR stop, 2.5xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 8 | 0.0% | -$684.86 | -3.24 | -6.8% | -$85.61 | 0.00 |
| ETH | 11 | 36.4% | -$323.63 | -1.21 | -5.8% | -$29.42 | 0.42 |
| HYPE | 8 | 37.5% | +$68.21 | +0.24 | -2.8% | +$8.53 | 1.20 |
| **Combined** | **27** | **25.9%** | **-$940.27** | -1.96 | -3.2% | **-$34.82** | 0.41 |

Fees: BTC $71.22, ETH $103.47, HYPE $34.15 (total $208.84).
Exits: 25 stop / 2 signal / 0 max-hold — the stop manages
nearly every trade. Combined Sharpe / MaxDD are computed on
the summed $30k three-coin equity curve.

## Verdict: loser

-$940 across 27 trades. BTC wins nothing in 8 trades
(Sharpe -3.24, -$685) and ETH wins barely a third; only
HYPE is green (+$68) and nowhere near enough to matter. A
stalemate candle on 1h crypto is a pause inside the trend,
not a turn — exactly the weakness Nison's ranking predicts
for this pattern versus piercing / dark-cloud cover.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Cache starts 22 hours late (BTC/ETH) / 24 hours late
  (HYPE first bar) vs the requested window start.
- Never tune the shipped parameters on this window.
