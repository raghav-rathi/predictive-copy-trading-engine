# GMMA — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: short group EMA(3,5,8,10,12,15) vs long group EMA(30,35,40,45,50,60), whole-group crossover entry, recross exit, 2xATR stop, 2.5xATR chandelier trail)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 206 | 26.7% | -$2,181 | -21.8% | -1.71 | -28.1% | -$10.59 | 0.74 |
| ETH | 211 | 26.5% | -$2,521 | -25.2% | -2.09 | -32.3% | -$11.95 | 0.72 |
| HYPE | 181 | 32.0% | -$1,088 | -10.5% | -0.78 | -17.0% | -$6.01 | 0.86 |
| **Combined** | **598** | **28.4%** | **-$5,790** | — | — | — | -$9.68 | — |

## Verdict: LOSER

Negative on all three coins with 598 trades in ~7 months — the strategy
massively overtrades. Raw GMMA on 1h crypto bars fires whole-group
crossovers constantly (the synthetic chop unit test documents this: even
fast mean-reverting noise produces dozens of full-group crossings), so
entries arrive on every coherent 2-3-bar move and the recross exit cuts
them for small losses plus $4.7k in combined fees. The 2.5xATR trail is
doing the only useful work in the config — removing it deepens BTC/ETH
losses and turns HYPE barely flat (see CALIBRATION.md). Win rate
26-32% with a recross exit cannot compensate a whipsaw entry; the failure
is the unfiltered crossover, not the exit logic.

## Calibration note

Group separation columns (`gmma_sep`, `gmma_bull_gap`, `gmma_bear_gap`)
were computed per bar and confirm the mechanism's flaw: `gmma_bull_gap`
crosses zero hundreds of times in the sample, i.e. the "compression then
separation" read the entry depends on never really compresses on 1h bars —
the groups separate, recross, and separate again on routine noise. What
survived contact with data: the EMA construction and crossover math are
correct and lookahead-free (truncation-tested), and the trailing stop is
net-positive for the system. What didn't: Guppy's textbook use assumes
daily bars and a compression filter (count-back line) that this port
omits; without it the 1h crossover is a noise trade. Compressed groups
help slightly (see CALIBRATION.md) but stay negative — structural, not
parametric.

## Mechanism

Whole-group crossover: LONG when every short-group EMA (3,5,8,10,12,15)
crosses fully above every long-group EMA (30,35,40,45,50,60); SHORT on
the mirror cross. Exit on group recross, 2xATR hard stop, 2.5xATR
chandelier trail rides trend legs, no fixed target, no max hold.

Source: GMMA (Daryl Guppy, Trend Trading) — BabyPips guide —
http://babypips.com/learn/forex/guppy-multiple-moving-average

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized crossover entry.
- Parameter sweep limited to 2 variants; no count-back-line compression
  filter or daily-bar variant tested — the most promising rescue is a
  genuine Guppy compression filter before the crossover.
