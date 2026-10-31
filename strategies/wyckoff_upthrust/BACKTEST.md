# Wyckoff Upthrust — Backtest

**Data:** Hyperliquid 1h candles read directly from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`) — `fetch_candles` was NOT called,
so the cache was not rewritten. Window t in [1773525600000,
1793318400000] (2026-03-14 22:00 UTC → 2026-10-30 00:00 UTC), duplicates
dropped (keep first). $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP = 25 bars.

**Bar counts used:** BTC 5499, ETH 5499, HYPE 5497. Window rows before
dedup: 5504 / 5504 / 5502, i.e. 5 exact-duplicate bars dropped per
coin. First bar BTC/ETH 1773525600000 (2026-03-14 22:00 UTC), HYPE
1773532800000 (2026-03-15 00:00 UTC); last bar all coins
1793318400000 (2026-10-30 00:00 UTC).

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 136 | 30.9% | −$955.85 | −0.81 | −27.6% | −$7.03 | 0.86 |
| ETH | 112 | 30.4% | −$730.85 | −0.68 | −21.1% | −$6.53 | 0.88 |
| HYPE | 169 | 32.0% | −$687.65 | −0.54 | −20.4% | −$4.07 | 0.89 |
| **Combined** | **417** | **31.2%** | **−$2,374.36** | **−1.13** | **−17.9%** | **−$5.69** | **0.87** |

Fees: BTC $1,534.43, ETH $1,013.02, HYPE $760.15 (total $3,307.61).
Exits: 319 stop / 98 signal / 0 max-hold — the stop manages 77% of
trades. Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve truncated to the shortest series (5497 bars);
combined totals are sums of the per-coin runs.

## Verdict: loser, but the least-bad of this batch

−$2,374 across 417 trades (−7.9% on $30k) with profit factors of
0.86–0.89 is a loser on every coin, but it is much closer to
breakeven than its batchmates, and its trade count is sane. The
pattern is consistent: ~31% win rate, stops doing most of the
exiting — the bare formalization catches real failed breakouts but
also shorts genuine breakouts that pause inside the range for one
bar before continuing up. Volume confirmation or a sign-of-weakness
filter might help, but neither was tested here.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- No volume filter, no distribution-phase requirement (see README).
- Never tune the shipped parameters on this window.
