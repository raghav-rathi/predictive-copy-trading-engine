# ABCD Pattern — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,335 bars, 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC; HYPE 5,333 bars, 2026-03-15 00:00 UTC →
2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=80 bars.

## Results (shipped config: 5-bar zigzag pivots, BC 38.2%–88.6% of
AB, CD 127.2%–161.8% of BC, |CD| within 20% of |AB|, opposite-
completion / 50%-of-CD-past-D exits, 2xATR stop, 2.5xATR trail,
96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 9 | 22.2% | -$526 | -5.3% | -2.28 | -6.2% | -$58.39 | 0.07 |
| ETH | 13 | 30.8% | -$232 | -2.3% | -0.62 | -5.2% | -$17.81 | 0.64 |
| HYPE | 11 | 63.6% | +$717 | +7.2% | +1.99 | -2.2% | +$65.17 | 2.97 |
| **Combined** | **33** | **39.4%** | **-$41** | — | — | — | -$1.24 | — |

Fees: BTC $92, ETH $104, HYPE $57 (total $253).
Exits: ALL 33 trades exited via the harness stop/trail — no trade
ever reached a signal exit (opposite completion or CD-failure
level) first, and the 96-bar max hold never binds.

## Verdict: inconclusive — the sample is far too thin to judge

33 trades across three coins in seven months, with each coin's
sample in single digits or low teens (9 / 13 / 11). Combined net
is -$41, which is a rounding error, not a result. Nothing here
supports or refutes the ABCD thesis:

- The HYPE leg (+$717, 63.6% win, PF 2.97) looks like an edge
  until you count the trades: 11. Seven wins out of eleven on a
  single coin is well inside noise.
- The BTC leg (PF 0.07 on 9 trades) looks like a disaster until
  you count the trades: 9. Two wins out of nine is also noise.
- The fact that every trade exited via the harness stop rather
  than a signal exit is the one structural observation worth
  keeping: D-pivot entries on 1h bars rarely run far enough, fast
  enough, for the pattern's own exits to matter — the stop/trailing
  machinery does all the work, which means the pattern is mostly
  contributing entry timing, not trade management.

Stated plainly: this backtest is inconclusive. The tight ratio
bands do their job — random walks fire only ~1 completion per 500
bars (unit-tested) — but that selectivity starves the sample. A
real verdict would need a much longer window, more coins, or a
deliberately looser band set validated out-of-sample — not a
band-widening exercise on this window (see CALIBRATION.md).

## Mechanism

5-bar zigzag pivots (confirmed with a 5-bar lag, no lookahead);
bullish ABCD (A high, B low, C lower high, D low) -> long,
bearish mirror -> short; BC 38.2%–88.6% of AB, CD 127.2%–161.8%
of BC, |CD| within 20% of |AB|; exits on opposite completion or
a 50%-of-CD move past D against the position. 2xATR stop, 2.5xATR
chandelier trail, 96-bar max hold. All params fixed a priori; no
optimization.

Source: Harmonic Trading (Scott Carney) — ABCD pattern
(https://harmonictrading.com/).

## Limitations

- 33 trades total: no per-coin or combined statistic here is
  significant; do not quote the HYPE leg as an edge or the BTC
  leg as a failure.
- Single 7-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Never tune the shipped parameters on this window.
