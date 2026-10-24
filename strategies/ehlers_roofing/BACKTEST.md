# Ehlers Roofing Filter — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), FULL cached range: BTC/ETH 5,335 bars, 2026-03-14 22:00 UTC →
2026-10-22 23:00 UTC; HYPE 5,333 bars, 2026-03-15 00:00 UTC →
2026-10-22 23:00 UTC.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short. WARMUP=80 bars.

## Results (shipped config: 48-bar high-pass + 10-bar SuperSmoother,
zero-cross entries/exits, 1.5xATR stop, 2xATR chandelier trail,
72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 528 | 27.1% | -$6,771 | -67.8% | -4.70 | -70.1% | -$12.82 | 0.62 |
| ETH | 525 | 34.5% | -$3,917 | -39.3% | -1.95 | -44.8% | -$7.46 | 0.80 |
| HYPE | 506 | 35.0% | -$2,355 | -23.5% | -1.08 | -27.8% | -$4.65 | 0.90 |
| **Combined** | **1,559** | **32.1%** | **-$13,043** | — | — | — | -$8.37 | — |

Fees: BTC $4,597, ETH $4,514, HYPE $3,122 (total $12,233).
Exits: ~71% harness stops (BTC 377/528), the rest signal exits;
the 72-bar max hold never binds.

## Verdict: a clear loser — the zero cross whipsaws on 1h bars

Combined -$13,043 across 1,559 trades, every leg deeply red
(PF 0.62 / 0.80 / 0.90), BTC's equity curve down 70% peak to
trough. The failure mode is visible in the exit mix: the roofing
line crosses zero roughly every other day per coin, and most
crossings reverse into the 1.5xATR stop before the opposite cross
can pay. The filter does what Ehlers claims — a pure 48-bar sine
keeps ~47% of its amplitude and the output tracks the cycle with a
fixed phase shift (unit-tested) — but real 1h crypto price is not
a clean 48-bar sine: it is trend plus broadband noise, and the
high-pass passes enough of that noise to flip the line's sign
constantly. Each flip costs ~0.055% round-trip plus the stop loss.

The short side is not the problem and the long side is not the
problem — both bleed (entries split almost evenly, 779 long /
780 short). The problem is frequency: ~500 trades per coin in
seven months is a scalping frequency on a cycle-turn thesis, and
the thesis needs the turn to persist. On 1h bars it usually
doesn't.

Honest read: as specified this is not tradeable. If revisited, it
needs a regime gate (trade crossings only when a cycle is actually
dominant, e.g. a measured cycle-strength or ADX filter) or a
longer bar scale — and any of that must be validated on
walk-forward data, not this window (see CALIBRATION.md: no
in-sample tuning was performed).

## Mechanism

48-bar high-pass (alpha = 2*pi/48, seeded 0) + 10-bar SuperSmoother
(Ehlers coefficients, seeded 0); long on a zero cross up, short on
a zero cross down, exit on the opposite cross. 1.5xATR stop, 2xATR
chandelier trail, 72-bar max hold. All params fixed a priori; no
optimization.

Source: John Ehlers, Cycle Analytics for Traders — Roofing Filter
(https://www.mesasoftware.com/).

## Limitations

- Single 7-month crypto window; 1,559 trades is plenty for the
  negative verdict but says nothing about other regimes.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
