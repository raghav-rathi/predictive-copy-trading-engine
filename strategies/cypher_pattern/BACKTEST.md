# Cypher Harmonic Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), filtered to t >= 1773525600000: BTC/ETH 5,445 bars,
2026-03-14 22:00 UTC → 2026-10-27 13:00 UTC; HYPE 5,443 bars,
2026-03-15 00:00 UTC → 2026-10-27 13:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run, funding off).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=70 bars.

## Results (shipped config: lagged 5-bar pivots, 60-bar window,
AB/XA 38.2–61.8%, BC/AB 113–141.4%, CD/XC 78.6%, each ±8pp
tolerance, opposite-pattern or 168-bar max hold exit, 2xATR stop,
2.5xATR trail)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 2 | 50.0% | -$39.97 | -0.40% | -0.35 | -1.53% | -$19.98 | 0.46 |
| ETH | 3 | 33.3% | -$160.25 | -1.60% | -1.16 | -2.46% | -$53.42 | 0.11 |
| HYPE | 3 | 33.3% | +$33.57 | +0.34% | +0.19 | -1.93% | +$11.19 | 1.40 |
| **Combined** | **8** | — | **-$166.65** | — | — | — | **-$20.83** | — |

Fees: BTC $27.35, ETH $19.94, HYPE $10.63 (total $57.92).
Signal entries: BTC 1 long / 1 short, ETH 2 / 1, HYPE 2 / 1.
Tolerances were NOT loosened to manufacture trades.

## Verdict: inconclusive (too few trades)

8 trades in seven months cannot confirm or refute the Cypher at
1h. The combined -$166.65 is one bad ETH trade away from flat,
and every per-coin statistic is noise at this sample size. The
detector works as specified (unit tests prove bullish and bearish
completions fire exactly once on crafted paths), but the pattern
as defined barely occurs on 1h crypto — which is itself a finding:
a pattern that fires ~once per coin per quarter is not a tradable
system at this timeframe, whatever its textbook reputation.

## Mechanism

Lagged 5-bar pivots within a 60-bar window; AB/XA 38.2–61.8%,
BC/AB 113–141.4%, CD/XC 78.6% (±8pp each); entry at D-bar
confirmation; opposite-pattern or 168-bar max hold exit; 2xATR
stop, 2.5xATR trail. All params fixed a priori; no optimization.

## Limitations

- 8 trades total — no metric above is statistically meaningful.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped tolerances on this window to chase trade
  count.
