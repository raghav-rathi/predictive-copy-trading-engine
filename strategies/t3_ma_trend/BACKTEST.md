# Tillson T3 Trend — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC/ETH 6,064 bars, HYPE 6,062 bars — counts verified against
the cache; HYPE's first bar is one hour later).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: T3(10, 0.7) trigger, T3(30, 0.7)
confirmation; exit on close through T3(10) or T3(10) turning;
2xATR harness backstop; 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 465 | 24.3% | -$5,412 | -54.2% | -4.52 | -56.5% | -$11.64 | 0.59 |
| ETH | 451 | 27.1% | -$2,300 | -23.1% | -1.13 | -35.0% | -$5.10 | 0.83 |
| HYPE | 467 | 29.1% | -$2,744 | -27.4% | -1.88 | -32.0% | -$5.88 | 0.80 |
| **Combined** | **1,383** | **26.8%** | **-$10,456** | — | — | — | **-$7.56** | **0.74** |

Fees: BTC $3,739, ETH $3,328, HYPE $2,016 (total $9,083).

## Verdict: loser — a faster EMA is still an EMA on choppy 1h crypto

A clear loss on all three coins across 1,383 trades: 26.8% win
rate, profit factor 0.74, expectancy -$7.56/trade. T3's lag
reduction did not buy a trend edge — it bought a faster
whipsaw. The average trade lasted 5.9 bars (vs 3.5 for the Hull
average in the same batch, so T3 is the slower of the two
losers, and still far too fast). Exits were 87% signal-driven
(1,198 of 1,383) and 13% stops; the 168-bar max hold never
fired once.

- Fees are 87% of the damage: $9,083 of the $10,456 combined
  loss is fees and slippage. At ~460 trades per coin the
  strategy pays the 0.055%-per-side round-trip cost roughly once
  every 13 bars.
- BTC was the worst (-54.2%, Sharpe -4.52) and ETH the least bad
  (-23.1%, Sharpe -1.13) — the ordering mirrors how choppy each
  coin was in this window rather than any property of T3.
- The T3(30) confirmation gate did not earn its keep: it agrees
  with T3(10) through most trends, so it filters few entries
  while adding nothing on the exits, which are driven by the
  fast T3 alone.

Stated plainly: do not trade this. Tillson's smoother does what
it promises — it tracks price with less lag than an EMA — and
on 1h crypto that is the failure mode, not the edge. Both
lag-reduced averages in this batch lost for the same reason:
on hourly bars, turning faster means trading the noise.

## Mechanism

LONG when C > T3(10, 0.7) with T3(10) rising and T3(10) above
T3(30, 0.7); SHORT on the mirror; exit on a close back through
T3(10) or T3(10) turning against the position; transition-only
entries via a position state machine. All params fixed a priori;
no optimization.

Source: Tim Tillson, "Smoothing Techniques for More Accurate
Signals", *Technical Analysis of Stocks & Commodities*, Jan 1998
(https://www.mesasoftware.com/papers/T3.pdf).

## Limitations

- Single 8-month crypto window (a strong downtrend regime for
  much of it); funding unmodeled; next-bar-open execution vs
  idealized entry.
- The loss is large enough that the sign is robust, but the
  magnitudes are window-specific — do not quote -$10,456 as a
  general expectation.
- Never tune the shipped parameters on this window — least of
  all the 10/30 periods or the 0.7 vfactor, which directly
  control the trade count.
