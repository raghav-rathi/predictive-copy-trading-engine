# Order Flow Imbalance — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), window
t in [1773525600000, 1793318400000] (2026-03-14 22:00 UTC →
2026-10-30 00:00 UTC), deduplicated (keep first), $10k start
per coin, 1% risk per trade on the 2xATR stop, 3x leverage
cap, 0.045% fee + 0.01% slippage per side, funding off.
WARMUP=25 bars. Run through `strategies/backtest.py`
`run_backtest` with the strategy's own RiskConfig; the cache
was read directly, never rewritten (no `fetch_candles` call).

**Bar counts used (verified, matching the brief's
expectation exactly):** BTC 5499, ETH 5499, HYPE 5497.

## Results

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 477 | 26.2% | -$5,343.92 | -4.51 | -54.3% | -$11.20 | 0.60 |
| ETH | 474 | 30.4% | -$3,389.25 | -2.28 | -40.1% | -$7.15 | 0.77 |
| HYPE | 473 | 34.9% | -$2,263.17 | -1.49 | -27.2% | -$4.78 | 0.84 |
| **Combined** | **1,424** | **30.5%** | **-$10,996.35** | **-4.09** | **-38.0%** | **-$7.72** | — |

Fees: BTC $3,882.49, ETH $3,463.58, HYPE $2,129.98 (total
$9,476.05). Exits: BTC 310 signal / 167 stop; ETH 296 signal /
178 stop; HYPE 321 signal / 152 stop; 0 max-hold exits.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: loser, no demonstrated edge

The highest trade count in the batch and the worst combined
loss. A 5-bar imbalance window on 1h bars whipsaws: the
zero-cross exit fires often (~65% of exits) but entries
re-trigger almost immediately, so the book churns through
fees while the stop takes the trend moves. BTC's -54.3%
drawdown on a single $10k book is the worst single-coin
drawdown in this batch. Do not trade this as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The bar-delta proxy is not measured order flow (see
  README.md); results say nothing about true footprint
  delta, which needs tick bid/ask data.
- Never tune the shipped parameters on this window.
