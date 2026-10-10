# KAMA trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-10
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: KAMA(10,2,30), ER>0.3 entry filter, cross-back exits, 2.5xATR stop)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 151 | 22.5% | -$2,161 | -21.6% | -3.06 | -26.1% | -$14.31 | 0.55 |
| ETH | 144 | 24.3% | -$665 | -6.6% | -0.82 | -10.7% | -$4.62 | 0.82 |
| HYPE | 143 | 31.5% | +$886 | +8.9% | +1.11 | -5.6% | +$6.19 | 1.22 |
| **Combined** | **438** | **26.0%** | **-$1,940** | — | — | — | -$4.43 | — |

## Verdict: mixed

HYPE is a genuine winner: 143 trades, +8.9% net, Sharpe +1.11, profit
factor 1.22, max drawdown only -5.6%. BTC and ETH are losers as
parameterized: win rates in the low 20s with deeply negative Sharpe on
BTC (-3.06) and a -26.1% max drawdown. Combined the book is -$1,940 on
438 trades. The mechanism is not broken everywhere — it is coin-selective
in this window.

## Calibration note

Shipped exactly the specified parameters (n=10, fast=2, slow=30,
ER>0.3 entry filter, cross-back exits, 2.5xATR stop, no trailing/target,
no max hold, 60-bar warmup). A 2-variant sweep (ER window n=14; ER
filter 0.2 instead of 0.3) was run on the same data — see CALIBRATION.md.
Neither variant turned BTC/ETH positive; the HYPE edge survived both.
What the data says: the ER>0.3 filter does real work (the no-filter
behavior in unit tests fires entries deep in chop), but on 1h BTC/ETH
the KAMA cross entries still whipsaw through the choppy-to-bearish 2026
regime — the mirror-cross exit is too slow to cut the false breaks, and
fees ($2.9k combined) compound the bleed on the losing coins.

## Mechanism

Kaufman Adaptive Moving Average with Efficiency Ratio ER(10): fast
smoothing 2/(2+1), slow smoothing 2/(30+1), SC=(ER*(fastSC-slowSC)+
slowSC)^2, recursive KAMA seeded with SMA(10). Enter long when close
crosses above KAMA with ER>0.3 (short on cross below with ER>0.3); exit
on the mirror cross. 2.5xATR hard stop as safety net.

Source: KAMA (Perry Kaufman) — MetaTrader 5 docs —
https://www.metatrader5.com/en/terminal/help/indicators/trend_indicators/ama

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized cross entry.
- HYPE edge is in-sample on one window; no walk-forward validation yet.
- KAMA seed (SMA at first valid index) is positional, not global — a
  non-issue for causal end-truncation (unit-tested), but warmup is
  required before signals are meaningful (60 bars).
