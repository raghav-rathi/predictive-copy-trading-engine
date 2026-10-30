# VWAP Std Bands — Backtest

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
| BTC | 238 | 47.5% | -$2,696.84 | -3.44 | -28.0% | -$11.33 | 0.59 |
| ETH | 223 | 46.2% | -$2,830.22 | -3.56 | -29.9% | -$12.69 | 0.59 |
| HYPE | 234 | 53.0% | -$2,575.56 | -3.61 | -26.7% | -$11.01 | 0.63 |
| **Combined** | **695** | **48.9%** | **-$8,102.61** | **-5.34** | **-27.5%** | **-$11.66** | — |

Fees: BTC $2,296.44, ETH $1,624.22, HYPE $1,037.30 (total
$4,957.96). Exits: BTC 172 signal / 66 stop; ETH 153 signal /
70 stop; HYPE 161 signal / 73 stop; 0 max-hold exits.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: loser, no demonstrated edge

Every coin loses by a similar amount, which is the worst
kind of consistency: the 2-sigma fade loses on BTC, ETH,
and HYPE alike. The midline exit fires often (~70% of exits)
but winners do not cover the stops — excursions that recover
one band tend to stall before the midline, and excursions
that trend run straight through the stop. Do not trade this
as shipped.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
