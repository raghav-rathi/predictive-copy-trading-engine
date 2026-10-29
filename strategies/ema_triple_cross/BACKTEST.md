# EMA Triple Cross — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filter window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and t <=
1793145600000), $10k start, 1% risk per trade on the 2xATR
stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP=30 bars.

**Actual candle window used (the cache, not the filter
bounds):** BTC and ETH first candle 2026-03-14 22:00 UTC
(t=1773525600000), HYPE first candle 2026-03-15 00:00 UTC
(t=1773532800000); all coins last candle 2026-10-27 13:00
UTC (t=1793106000000). The cache starts 22 hours after the
filter's lower bound and ends ~11 hours before its upper
bound, so the run covers 5,445 / 5,445 / 5,443 bars rather
than the full filter span — no candles were added or
shifted; the window is reported as actually returned.

## Results (shipped config: EMA 3/8/21 stack, exit on
unstacking, 2xATR stop, 3xATR trail, 336-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 499 | 23.6% | -$6,080 | -4.98 | -62.4% | -$12.18 | 0.59 |
| ETH | 494 | 24.3% | -$4,373 | -2.96 | -45.8% | -$8.85 | 0.71 |
| HYPE | 458 | 31.2% | -$1,465 | -0.70 | -24.8% | -$3.20 | 0.91 |
| **Combined** | **1,451** | **26.2%** | **-$11,917** | — | — | **-$8.21** | — |

Fees: BTC $3,727, ETH $3,273, HYPE $2,290 (total $9,290).
Exits: 971 signal (unstack) / 480 stop. Signal entries
fired 501 long / 496 short across the three coins.

## Verdict: loser

-$11,917 across 1,451 trades, negative on every coin. The
stack exit churns: two-thirds of trades end on an unstack
rather than a stop, so the system bleeds fees on EMA wobbles
and never holds a trend long enough to pay. BTC is the worst
leg (-$6,080, Sharpe -4.98, -62.4% drawdown).

## Limitations

- Single ~7.5-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
