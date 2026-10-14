# Hull MA — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → present
(BTC 5,080 bars; ETH 5,080; HYPE 5,078).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: classic HMA(16), long on slope-turn positive with
close above HMA, short on the mirror, exit on opposite slope turn or price
cross, 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 657 | 27.6% | −$6,896 | −68.5% | −7.39 | −69.7% | −$10.50 | 0.52 |
| ETH | 646 | 27.9% | −$5,093 | −50.4% | −3.98 | −52.5% | −$7.88 | 0.67 |
| HYPE | 613 | 35.6% | −$3,846 | −37.6% | −3.02 | −38.9% | −$6.27 | 0.73 |
| **Combined** | **1,916** | **30.3%** | **−$15,834** | — | — | — | −$8.26 | — |

## Verdict: LOSER (worst of the batch)

Negative on all three with Sharpe −3 to −7 and profit factors 0.52–0.73.
The failure mode is whipsaw: HMA(16)'s slope flips on almost every hourly
wiggle, so the system trades 1,916 times in 7 months (~9/day across the
book) into chop. Win rates of 28–36% cannot carry PF < 0.75 at these
hold lengths. Fees ($10,808 combined) amplify the damage but the
pre-cost book is still deeply negative.

## Calibration note

Indicators verified: independent pure-Python WMA recomputation matches
exactly; truncation test proves lookahead-freedom. The N sweep (see
CALIBRATION.md) shows the loss is structural at every period — 32 is
merely least-bad. What would need to change: a slope-confirmation filter
(e.g. slope must exceed an ATR-normalized threshold, not just flip sign)
or moving the rule to 4h+ bars where the slope turn is meaningful.

## Mechanism

HMA(16) = WMA(2·WMA(close,8) − WMA(close,16), 4). Design note: on a
V-reversal price crosses the HMA before its slope turns (low lag is the
point of HMA), so the shipped rule triggers on the slope turn with price
confirmation: long when slope crosses above 0 with close above the HMA;
short on the mirror. Exit on the opposite slope turn or a price cross of
the HMA. 2xATR hard stop, 3xATR chandelier trail, 120-bar max hold.

Source: Alan Hull — Hull Moving Average — https://alanhull.com/hull-moving-average

## Limitations

- Single 7-month window; slope-turn systems historically prefer trending
  regimes, but the whipsaw here is a mechanism problem, not a regime one.
- Funding unmodeled.
- Next-bar-open execution: slope turns often gap against the fill on
  fast reversals.
