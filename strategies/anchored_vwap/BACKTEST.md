# Anchored VWAP — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window
t in [1773525600000, 1793318400000] (2026-03-14 22:00 UTC →
2026-10-30 00:00 UTC), deduplicated (keep first), $10k start
per coin, 1% risk per trade on the 2xATR stop, 3x leverage
cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=30 bars. Run through `strategies/backtest.py`
`run_backtest` with the strategy's own RiskConfig; the cache
was read directly, never rewritten (no `fetch_candles` call).

**Bar counts used (verified, matching the brief's
expectation exactly):** BTC 5499, ETH 5499, HYPE 5497.

## Results

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 173 | 17.9% | -$3,731.73 | -4.78 | -39.6% | -$21.57 | 0.42 |
| ETH | 204 | 20.1% | -$900.63 | -0.69 | -15.8% | -$4.41 | 0.87 |
| HYPE | 148 | 21.6% | -$910.18 | -1.01 | -19.4% | -$6.15 | 0.81 |
| **Combined** | **525** | **19.8%** | **-$5,542.54** | **-3.13** | **-21.1%** | **-$10.56** | — |

Fees: BTC $1,613.31, ETH $1,706.95, HYPE $678.48 (total
$3,998.74). Exits: BTC 91 signal / 82 stop; ETH 128 signal /
76 stop; HYPE 95 signal / 53 stop; 0 max-hold exits. Combined
Sharpe / MaxDD are computed on the summed $30k three-coin
equity curve.

## Verdict: loser, no demonstrated edge

Every coin loses, the win rate sits near 20%, and BTC's
drawdown reaches -39.6% on a single $10k book. The signal
exit fires often (about 60% of exits) without saving the
book — crosses of a slow cumulative average on 1h bars are
late by construction. Do not trade this as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
