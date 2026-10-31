# Choppiness Index — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 30 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Before dedup the
window held 5504 / 5504 / 5502 rows, i.e. 5 exact-duplicate bars per
coin were dropped. First bar BTC/ETH 1773525600000 (2026-03-14 22:00
UTC), HYPE 1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 58 | 31.0% | -$318.18 | -0.15 | -9.7% | -$5.49 | 0.89 |
| ETH | 76 | 25.0% | -$1,966.39 | -2.54 | -24.2% | -$25.87 | 0.49 |
| HYPE | 53 | 43.4% | +$255.31 | +0.42 | -6.4% | +$4.82 | 1.12 |
| **Combined** | **187** | **32.1%** | **-$2,029.27** | **-1.30** | **-10.1%** | **-$10.85** | **0.78** |

Fees: BTC $716.88, ETH $592.91, HYPE $271.48 (total $1,581.27).
Exits: 151 stop / 36 signal / 0 max-hold — the stop manages 81% of
trades. Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve.

## Verdict: loser, not a demonstrated edge

-$2,029 across 187 trades on $30k starting capital over ~7.5 months,
with ETH alone contributing -$1,966 and a -24.2% drawdown. Only HYPE
is green, and by just $255 on 53 trades — noise. The CHOP gate cuts
trade count versus a raw Donchian breakout but does not produce a
winning filter on this window.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- CHOP lags: the regime reading is backward-looking, so entries chase
  established moves.
- Never tune the shipped parameters on this window.
