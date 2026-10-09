# Heikin-Ashi Trend System — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,000 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: Valcu 6 rules, consolidation = body < 25% of HA range)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 649 | 23.6% | -$6,997 | -70.0% | -9.73 | -70.1% | -$10.78 | 0.41 |
| ETH | 601 | 28.6% | -$4,099 | -41.0% | -4.04 | -41.4% | -$6.82 | 0.68 |
| HYPE | 561 | 33.3% | -$4,326 | -43.3% | -5.02 | -45.0% | -$7.71 | 0.60 |
| **Combined** | **1811** | **28.3%** | **-$15,422** | — | — | — | -$8.51 | — |

## Verdict: LOSER (worst of the batch)

The single worst result in this batch: -$15.4k combined, BTC Sharpe -9.73.
1,811 trades — roughly one every 8 bars — exposes the core problem: on 1h
bars the Heikin-Ashi color flip is not a trend signal, it is noise
amplified. HA smoothing lags just enough that the entry is always late,
and the "exit on opposite color or consolidation bar" rule then flips the
book straight into the whipsaw. The consolidation skip (no entries on
small-body HA bars) does not save it; it just delays entries into worse
prices.

## Calibration note

Shipped the specified parameters exactly (haClose=(o+h+l+c)/4,
haOpen=(prev haOpen+prev haClose)/2 seeded from the first open,
consolidation = body < 0.25 x HA range, skip entries during
consolidation, exit on opposite color or consolidation, 2xATR stop /
2.5xATR trail, no target). One genuine finding from testing, kept as
specified behavior: on smooth data the HA flip bar is almost always a
consolidation bar (tiny body at the turn), so entries only fire on sharp
V-turns — the rule set is internally consistent but starves itself of
trades on gentle trends and over-trades on chop. No parameter rescue was
attempted: the failure (1,811 trades, PF 0.41-0.68) is the timeframe, not
the thresholds. Valcu's rules are a daily-chart trend system; the 1h port
is a churn machine.

## Mechanism

Long when the previous HA bar is red and the current HA bar is green and
not a consolidation bar (mirror for shorts); no entries during
consolidation bars; flatten on an opposite-color HA bar or a consolidation
bar. Risk: 2xATR stop, 2.5xATR chandelier trail, no fixed target.

Source: Dan Valcu, Heikin-Ashi technique (six rules) —
https://www.mql5.com/en/articles/91

## Limitations

- Single 7-month window; daily-bar variant (the system's native timeframe) untested.
- Funding unmodeled (would modestly help the short book).
- Next-bar-open execution vs idealized HA-close entry.
- HA computation seeded from the first bar's open; warmup is 30 bars.
