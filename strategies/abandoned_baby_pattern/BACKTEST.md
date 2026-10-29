# Abandoned Baby Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`), filter window
2026-03-14 → 2026-10-28 (t >= 1773446400000 and t <=
1793145600000), $10k start, 1% risk per trade on the 1.5xATR
stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off. WARMUP=30 bars.

**Actual candle window used (the cache, not the filter
bounds):** BTC and ETH first candle 2026-03-14 22:00 UTC
(t=1773525600000), HYPE first candle 2026-03-15 00:00 UTC
(t=1773532800000); all coins last candle 2026-10-27 13:00
UTC (t=1793106000000). The cache starts 22 hours after the
filter's lower bound and ends ~11 hours before its upper
bound — no candles were added or shifted; the window is
reported as actually returned.

## Results (shipped config: strict-gap abandoned baby, doji
<= 10% body, long bodies >= 40%, midpoint + volume
confirmation, 1.5xATR stop, 2xATR trail, 2.5xATR target,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0 | — | — | — | $0 fees |
| ETH | 0 | — | $0 | — | — | — | $0 fees |
| HYPE | 0 | — | $0 | — | — | — | $0 fees |
| **Combined** | **0** | **—** | **$0** | **—** | **—** | **—** | **—** |

## Why zero trades (diagnostic, not a guess)

Counting pattern components on the same frames: BTC 607
dojis, ETH 560, HYPE 560 — but gap-doji sequences (a doji
strictly gapped away from the prior candle) number 0 on BTC,
0 on ETH, and 1 on HYPE, and that single HYPE sequence fails
the remaining filters (long bodies / midpoint / volume).
The detector itself is verified: both bullish and bearish
variants fire on synthetic data in the unit tests. The
zero is structural — crypto trades 24/7, so true inter-bar
gaps essentially never occur on 1h candles, unlike
equities with an overnight close.

## Verdict: no-trade (untradeable as specified)

0 trades on all coins is neither a win nor a loss; it is
evidence the setup does not exist in this market at this
timeframe. Do not trade this as shipped, and do not relax
the gap rule to manufacture trades — that would be a
different pattern.

## Limitations

- Single ~7.5-month crypto window; funding unmodeled.
- A lower timeframe or a gapped market (equities) could
  show frequency; neither was tested here.
- Never tune the shipped parameters on this window.
