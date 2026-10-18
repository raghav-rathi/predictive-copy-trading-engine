# Hurst FLD — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,222 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: FLD(20/40/80) cascade entries, cross-back-through-FLD20 exits, 2xATR stop, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 245 | 29.8% | -$2,281 | -22.8% | -1.81 | -28.0% | -$9.31 | 0.75 |
| ETH | 253 | 28.1% | -$1,927 | -19.3% | -1.15 | -33.6% | -$7.62 | 0.76 |
| HYPE | 259 | 30.9% | -$1,824 | -18.2% | -1.58 | -22.6% | -$7.04 | 0.76 |
| **Combined** | **757** | **29.6%** | **-$6,032** | — | — | — | -$7.97 | — |

## Verdict: LOSER

Loses on all three coins (-$6,032 combined on 757 trades, profit factor
0.75-0.76 everywhere). The FLD cascade is a slow trend-alignment filter,
and on 1h crypto the alignment mostly arrives after the move: by the time
price sits above FLD20 > FLD40 > FLD80, the 20-bar cycle leg is already
exhausted, so entries buy the top of the swing and the FLD20 cross-back
exit hands most of it back. ~$5.5k in combined fees on 757 trades
($7.25/trade average) compounds the damage, but with PF at 0.75-0.76 the
failure is the edge, not the costs -- the gross book is underwater before
fees. Honest read: Hurst's FLD was built for daily/weekly equity cycles;
at 1h on crypto the cycle periods it resolves are mostly noise.

## Calibration note

Shipped exactly the specified parameters (FLD 20/40/80, cascade entries,
FLD20 cross-back exits, 2xATR stop, 72-bar max hold, WARMUP=90). A
one-variant sweep (FLD20-only entries, dropping the cascade filter) is
reported in CALIBRATION.md -- it is dramatically worse, so the shipped
cascade filter stays as the least-bad reading of the source.

## Mechanism

FLD(N)[i] = median(h,l)[i - N/2] (shifted median, past data only). Long
on the first bar with close > FLD20 AND FLD20 > FLD40 > FLD80; short on
the mirror. Exit long when close crosses back below FLD20 (shorts mirror);
2xATR hard stop, 72-bar max hold.

Source: J.M. Hurst, *The Profit Magic of Stock Transaction Timing* --
https://notes.hurstcycles.com/from-analysis-to-trading/

## Limitations

- Single 7-month crypto window; no bull-market sample, no daily/weekly bars.
- Funding unmodeled.
- Next-bar-open execution vs idealized signal-bar entry.
- FLD periods fixed at 20/40/80; cycle-length calibration untested.
