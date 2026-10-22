# Decycler Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE,
sliced to the batch window 2026-03-14 00:00 UTC → 2026-10-21 23:59:59
UTC (ms `[1773446400000, 1792627199000)`; actual data starts 2026-03-14
22:00 UTC for BTC/ETH, 2026-03-15 00:00 UTC for HYPE): 5,301 bars
BTC/ETH, 5,299 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start. WARMUP=80 bars.

## Results (shipped config: Decycler(P=20), long on close crossing above
the rising decycler, short on close crossing below the falling
decycler, exits on the opposite cross, 2xATR stop, 2xATR trail,
150-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 639 | 24.7% | -$6,559 | -65.6% | -7.81 | -66.4% | -$10.26 | 0.49 |
| ETH | 631 | 24.4% | -$4,507 | -45.1% | -3.85 | -49.9% | -$7.14 | 0.68 |
| HYPE | 630 | 29.4% | -$4,382 | -43.8% | -4.48 | -44.5% | -$6.96 | 0.62 |
| **Combined** | **1,900** | **26.2%** | **-$15,448** | — | — | — | **-$8.13** | — |

## Verdict: a clear loser — the lag-free line is a whipsaw machine

Combined **-$15,448** on 1,900 trades, negative on all three coins,
win rates 24–29%, profit factors 0.49–0.68. Nothing to salvage:

- **BTC** is the worst (-$6,559, PF 0.49, MaxDD -66.4%). The decycler
  line hugs price so closely that ordinary 1h chop crosses it back
  and forth; 639 trades in 7 months is pure overtrading.
- **ETH** and **HYPE** are the same shape (-$4,507 and -$4,382,
  PF 0.68/0.62). Even HYPE — the coin that carried nearly every
  other batch-11/12 winner — can't make this green.
- Fees ($11,355 combined) are real but not the story: the
  pre-fee expectancy is also negative. The strategy's premise fails,
  not its cost model.
- The mechanism explains the failure: the decycler's selling point
  (no lag) is also its trading flaw. Price crosses a zero-lag trend
  line constantly; the rising/falling confirmation filter does not
  change that, and the exits come after each whipsaw has already
  reversed. This is the "too responsive to trade raw" filter —
  Ehlers pairs it with further smoothing (the Roofing Filter) for a
  reason, and this strategy lacks that layer.

This is a research negative, not a ship candidate. The honest
takeaway: the decycler as a raw entry/exit line needs a smoothing
layer (longer cutoff, or an additional low-pass on the decycler
itself) before it can produce tradeable signals.

## Calibration note

Shipped the specified P=20 — fixed before any backtest was run.
A 10/20/40 cutoff sweep is in CALIBRATION.md: red at every setting
(P=40 is least bad at -$11,220 combined, still deeply negative).
The P=20 setting was not chosen in-sample; adopting P=40 because it
"loses less" on this window would be exactly the in-sample selection
the a-priori rule exists to prevent.

## Mechanism

Decycler: 2-pole Butterworth high-pass (cutoff P=20) of close
subtracted from close to leave the zero-lag trend component; long
when close crosses above the decycler while it is rising, short when
close crosses below while it is falling; exits on the opposite cross
(trend component turned). 2xATR hard stop, 2xATR chandelier trail,
150-bar max hold.

Source: Decycler (John Ehlers, TASC Sep 2015) —
https://ar.tradingview.com/scripts/ehlers/

## Limitations

- Single 7-month crypto window; 1,900 trades is a large sample but
  from one regime (and one that punished chop strategies).
- Funding unmodeled; next-bar-open execution vs idealized entry.
- The 630–639 trades/coin pace means costs and the max-hold cap are
  binding design constraints, not afterthoughts.
- Never tune the shipped cutoff on this window (see CALIBRATION.md).
