# Inside Bar Breakout — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to the batch window 2026-03-14 00:00 UTC →
2026-10-23 23:59 UTC (ms `[1773446400000, 1792713599000)`):
5,330 bars BTC/ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 2R
target, 3x leverage cap, $10k start, both directions. WARMUP=40.

## Results (shipped config: strict inside, 5-bar expiry, mother-dir
tie-break, opposite-breakout exits, 1.5xATR stop, 2R target,
48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 516 | 36.6% | -$5,874 | -58.8% | -4.44 | -63.5% | -$11.38 | 0.72 |
| ETH | 528 | 36.7% | -$5,143 | -51.4% | -3.32 | -53.9% | -$9.74 | 0.76 |
| HYPE | 427 | 38.9% | -$3,058 | -30.2% | -1.92 | -34.1% | -$7.16 | 0.84 |
| **Combined** | **1,471** | **37.3%** | **-$14,075** | — | — | — | -$9.57 | — |

Fees: BTC $5,348, ETH $3,935, HYPE $2,338 (combined $11,621 —
roughly equal to the net loss itself).

## Verdict: decisive loser — the 1h inside bar is a churn machine

This is not a close call. Every coin is deeply red, the combined
book loses -140% of its fee bill *on top of* $11.6k in fees, and
the Sharpe prints are catastrophic (-4.44 BTC, -3.32 ETH).

The mechanism explains the numbers: on 1h crypto, **17.4% of
bars are inside bars** (927 on BTC alone). That fires ~650 raw
entries per coin per 7 months, and after the 48-bar max hold and
stop/target churn the harness books 427–528 trades per coin —
roughly one trade every 10 bars. At a 36–39% win rate with a 2R
target the math needs ~33%+ to break even gross of fees; the
breakout direction is a coin flip and the whipsaws eat the
runners before the 2R target lands (profit factors 0.72–0.84 —
even *gross* of fees this is a loser).

The honest read: the inside-bar pattern's edge, if any, lives on
higher timeframes where compression is rare and meaningful
(the daily inside bar is the canon's home turf). On the 1h the
contraction signal fires so often it stops being a signal —
every consolidation produces a dozen overlapping 5-bar windows,
and breakouts of 1h mother levels are noise, not expansion.
Ship the code as a clean reference implementation; do not trade
it. No parameter rescue is credible here — the failure is
structural (too many setups, coin-flip direction), not a
±2-bar expiry tuning problem.

## Mechanism

Strict inside bar (whole range inside the prior bar) arms the
mother bar's high/low for up to 5 bars. Long on a close cross
above the armed mother high, short on a cross below the armed
mother low; same-bar double crosses take the mother bar's
direction; opposite breakout exits; 1.5xATR stop, 2R target,
48-bar max hold, both directions.

Sources: https://www.rebelsfunding.com/what-is-the-inside-bar-candlestick-pattern/ —
http://forexmt4indicators.com/inside-bar-pattern-price-action-strategy/

## Limitations

- Single 7-month crypto window; result is decisive enough that
  sample size is not the concern.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- 1h timeframe only — the pattern may behave differently on
  daily bars (untested here, deliberately not tuned).
- No walk-forward validation; with a loss this structural none
  is needed.
