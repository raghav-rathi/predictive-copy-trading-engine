# DeMarker exhaustion (DeMark) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-10
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; short holds make it second-order, but 24-bar max hold
can still span a day).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: DeM(14), long cross below 0.3 / short cross above 0.7, exit cross 0.5, 2xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 252 | 47.6% | -$2,934 | -29.3% | -2.51 | -30.0% | -$11.64 | 0.73 |
| ETH | 251 | 50.6% | -$1,705 | -17.1% | -1.39 | -28.1% | -$6.79 | 0.83 |
| HYPE | 234 | 44.9% | -$3,504 | -35.0% | -3.72 | -35.4% | -$14.97 | 0.63 |
| **Combined** | **737** | **47.7%** | **-$8,143** | — | — | — | -$11.05 | — |

## Verdict: LOSER

Negative on all three coins with deeply negative Sharpe. The win rate
hovers near 50% (the oscillator does catch bounces), but the payoffs are
asymmetric in the wrong direction: profit factor 0.63–0.83 means winners
are cut short by the cross-0.5 exit while the 24-bar max hold and 2xATR
stop let losers run in trending stretches. Turnover is the killer detail:
737 trades across three coins and $5.3k in combined fees — on the 1h
timeframe DeM crosses the 0.3/0.7 bands constantly in chop, so the
"exhaustion" signal fires as noise, not as reversal edges. The strategy
fades momentum in a window where mean-reversion on 1h crypto bars mostly
didn't pay.

## Calibration note

Shipped the canonical parameters (DeM(14), 0.3/0.7 exhaustion entries,
0.5 mean-reversion exits, 2xATR stop, 24-bar max hold). What I verified:
the DeM formula matches DeMark's definition exactly (unit-tested on
hand-built highs/lows: rising highs -> DeM 1.0, falling lows -> 0.0,
flat -> 0.5), entries require a true cross (not a touch), and indicators
are lookahead-free by truncation test. What didn't survive contact with
data: the 1h DeM oscillator whipsaws in chop — the cross below 0.3
fires several times into a single down-leg, each firing a fresh full-size
long, and the cross-above-0.5 exit takes the bounce off before it pays
for the sequence.

## Mechanism

Demand vs supply pressure oscillator: DeMax = max(h-h_prev, 0),
DeMin = max(l_prev-l, 0), DeM = SMA(DeMax,14)/(SMA(DeMax,14)+SMA(DeMin,14)).
Buy the cross below 0.3 (oversold exhaustion), exit the cross above 0.5
or above 0.7; mirror for shorts. 2xATR hard stop, 24-bar max hold, no
trailing/target.

Source: DeMarker (Tom DeMark) — TradingKey definition —
https://www.tradingkey.com/dictionary/demarker-indicator

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized exhaustion entry.
- Parameter sweep (CALIBRATION.md) tested period 9 and wider exit
  bands; neither rescued the edge — the failure is structural, not parametric.
