# Taylor 3-Day Cycle — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,222 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 1xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 0.1xATR dip/rally tolerance, -1-day re-phase on missed Buy Days, prior-day-extreme exits, 1xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 141 | 27.0% | -$4,074 | -40.7% | -2.69 | -46.4% | -$28.89 | 0.57 |
| ETH | 120 | 33.3% | -$482 | -4.3% | -0.09 | -16.1% | -$4.01 | 0.95 |
| HYPE | 159 | 25.8% | -$1,417 | -14.2% | -0.67 | -25.3% | -$8.91 | 0.89 |
| **Combined** | **420** | **28.3%** | **-$5,973** | — | — | — | -$14.22 | — |

## Verdict: LOSER

Loses on all three coins (-$5,973 combined on 420 trades). The Taylor
rhythm is a mean-reversion-around-the-daily-range idea built for
specialist-era equities with clean overnight gaps and pit-session
rhythms; on 24/7 crypto the "prior day's low" is an arbitrary NY-midnight
cut of a continuous auction, and dips to it carry no reversal edge --
BTC's book (PF 0.57, -$4,074) is the clearest read. ETH's -$482 (PF 0.95)
is the closest to flat but with 120 trades and a -16% drawdown it reads as
a slower bleed, not a near-miss. The re-phase logic fires as designed
(missed Buy Days do slide the cycle), but re-phasing a rhythm that has no
edge just reschedules the losses.

## Calibration note

Shipped exactly the specified parameters (0.1xATR dip/rally tolerance,
Buy -> Sell -> Sell-Short cycle on NY time anchored at Monday 2026-01-05,
-1-day re-phase, prior-day-high/low exits, 1xATR stop, 24-bar max hold,
WARMUP=72). A one-variant sweep (wider 0.25xATR tolerance) is reported in
CALIBRATION.md -- no rescue, shipped config stays.

## Mechanism

Cycle days on NY time (EDT=UTC-4 fixed; anchored Monday 2026-01-05 00:00
NY). Buy Day: long when the bar's low dips within 0.1xATR of the prior
NY-day low and recovers (close > open); exit at a touch of the prior day's
high. Sell Day: no new entries. Sell-Short Day: short when the bar's high
rallies within 0.1xATR of the prior day's high and rejects (close < open);
exit at a touch of the prior day's low. A Buy Day with no entry shifts the
cycle offset by -1 day for all following days. 1xATR stop, 24-bar max hold
as the time stop.

Source: George Douglass Taylor, *The Taylor Trading Technique* (1950) --
https://www.smbtraining.com/blog/the-taylor-rhythm

## Limitations

- Single 7-month crypto window; no equities sample where the method was born.
- NY = UTC-4 assumed fixed across the whole window (window sits inside US
  daylight time, so this holds).
- Funding unmodeled.
- Next-bar-open execution vs idealized signal-bar entry.
- 24/7 crypto has no true session open/close; NY-midnight day cuts are a
  modeling choice, not market structure.
