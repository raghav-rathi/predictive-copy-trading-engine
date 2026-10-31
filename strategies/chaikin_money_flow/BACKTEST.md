# Chaikin Money Flow — Backtest

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
| BTC | 695 | 28.8% | −$6,937.02 | −6.61 | −69.8% | −$9.98 | 0.55 |
| ETH | 624 | 33.8% | −$4,257.76 | −3.05 | −45.9% | −$6.82 | 0.75 |
| HYPE | 581 | 34.1% | −$2,866.42 | −1.86 | −33.1% | −$4.93 | 0.83 |
| **Combined** | **1,900** | **32.1%** | **−$14,061.19** | **−5.54** | **−48.2%** | **−$7.40** | **0.71** |

Fees: BTC $4,842.36, ETH $4,202.55, HYPE $2,579.36 (total $11,624.27).
Exits: 1,195 signal / 705 stop / 0 max-hold. Combined Sharpe / MaxDD
are computed on the summed $30k three-coin equity curve truncated to
the shortest series (5497 bars); combined totals are sums of the
per-coin runs.

## Verdict: loser — do not trade this as specified

−$14,061 on $30k starting capital across 1,900 trades, with a
combined Sharpe of −5.54 and a −48.2% max drawdown, is a decisive
rejection, not noise. The zero cross fires constantly in ranges
(695 BTC trades alone), and with a ~32% win rate and profit factors
of 0.55–0.83 on every coin, the signal carries no edge on this
window — fees alone ($11,624) account for most of the damage, but the
gross edge is negative too. A threshold band (e.g. ±0.05 or ±0.10)
might cut whipsaw, but that would be a different strategy and was
not tested here.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- CMF ignores gaps (see README limitation).
- Never tune the shipped parameters on this window.
