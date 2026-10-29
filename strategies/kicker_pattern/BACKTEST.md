# Kicker Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), requested window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and
t <= 1793145600000), $10k start, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per
side, funding off. WARMUP=20 bars.

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

## Results (shipped config: o2 beyond o1 gap, second body >=
0.5 * range, 2xATR stop, 2.5xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 1 | 0.0% | -$110.08 | -1.70 | -1.1% | -$110.08 | 0.00 |
| ETH | 1 | 100.0% | +$235.17 | +1.85 | -0.7% | +$235.17 | inf |
| HYPE | 3 | 0.0% | -$201.10 | -1.62 | -2.2% | -$67.03 | 0.00 |
| **Combined** | **5** | **20.0%** | **-$76.02** | -0.40 | -1.3% | **-$15.20** | 0.76 |

Fees: BTC $10.08, ETH $4.29, HYPE $13.65 (total $28.03).
Exits: 5 stop / 0 signal — every trade ended at the stop
(the ETH winner exited via a trailed stop ratcheted above
entry). Combined Sharpe / MaxDD are computed on the summed
$30k three-coin equity curve.

## Verdict: loser on a trivial sample

-$76 across 5 trades. The pattern fired 5 times in 16,351
bars — the textbook gap test is nearly impossible on 1h
crypto, where opens track prior closes. One ETH winner cannot
carry four stop-outs, and five trades cannot support any
statistical claim. This is "no evidence", not a tradeable edge.

## Limitations

- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Cache starts 22 hours late (BTC/ETH) / 24 hours late
  (HYPE first bar) vs the requested window start.
- Never tune the shipped parameters on this window.
