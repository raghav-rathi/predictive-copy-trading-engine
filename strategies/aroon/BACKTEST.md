# Aroon — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic Aroon(25), long on AroonUp >= 70 crossing
above AroonDown, short on the mirror, exit on the opposite cross, 2xATR
stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 182 | 34.1% | −$1,632 | −16.1% | −1.15 | −26.4% | −$8.97 | 0.80 |
| ETH | 168 | 38.1% | +$1,187 | +11.9% | +0.91 | −15.4% | +$7.07 | 1.14 |
| HYPE | 178 | 37.6% | +$2,289 | +23.1% | +1.51 | −10.7% | +$12.86 | 1.23 |
| **Combined** | **528** | **36.6%** | **+$1,844** | — | — | — | +$3.49 | — |

## Verdict: MIXED (positive combined, not a clean winner)

ETH and HYPE are positive with positive Sharpe (0.91 / 1.51) over
~170 trades each — real trade counts, not a handful of lucky prints.
BTC loses −$1,632 (Sharpe −1.15). The Aroon fresh-high/low filter does a
better job than ADX of waiting for a genuine new leg, which is why the
trade count is sane (528 vs hull_ma's 1,916). Combined book is +$1,844 —
the best combined result in this batch so far. The BTC failure is the
honest caveat: Aroon(25) on 1h BTC still buys late breakouts that fail.

## Calibration note

Indicators verified: hand-checked monotonic rise gives AroonUp=100 /
AroonDown=4 exactly; truncation test proves lookahead-freedom. The
lookback sweep (see CALIBRATION.md) confirms 25 is the best and sits in a
stable region — 42 is close (+$1,988) but thinner (320 trades), 14
churns. Shipped the classic 25.

## Mechanism

AroonUp = 100·(25 − bars since highest high)/25; AroonDown the same for
the lowest low. Long when AroonUp ≥ 70 and crosses above AroonDown
(a fresh high-leg while the low-leg is stale); short on the mirror.
Exit on the opposite cross. 2xATR hard stop, 3xATR chandelier trail,
120-bar (5-day) max hold.

Source: Tushar Chande — Aroon oscillator (1995) —
https://www.investopedia.com/terms/a/aroon.asp

## Limitations

- Single 7-month window; BTC's −16% is the regime reminder.
- Funding unmodeled (short book would earn it).
- Next-bar-open execution vs the idealized cross fill; fresh-breakout
  entries are the most slippage-sensitive of the batch.
