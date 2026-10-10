# Awesome Oscillator — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-09
(~5,030 bars each; API caps history at 5,000 candles/request).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation; 1h-bar holds keep it second-order).
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: AO(5,34) of median, cross/saucer/twin-peak entries, opposite-cross exits, 2xATR stop, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 235 | 28.1% | -$572 | -5.5% | -0.08 | -32.1% | -$2.43 | 0.95 |
| ETH | 237 | 28.3% | -$1,528 | -14.7% | -0.57 | -33.1% | -$6.45 | 0.87 |
| HYPE | 215 | 29.3% | +$164 | +1.6% | +0.25 | -23.5% | +$0.76 | 1.01 |
| **Combined** | **687** | **28.5%** | **-$1,936** | — | — | — | -$2.82 | — |

## Verdict: mixed (leaning LOSER)

Net-negative combined (-$1,936 on 687 trades). HYPE prints a small win
(+1.6%, Sharpe +0.25, profit factor 1.01) but with 215 trades and a
-23.5% max drawdown that reads as noise, not edge. BTC and ETH lose
with 28% win rates. The Williams patterns fire constantly on 1h crypto —
687 combined trades, ~$5.4k in combined fees — and the opposite-cross
exit keeps every trade capped to one AO swing, which is not enough to
cover the churn when direction only persists a third of the time. Fees
are a real drag here but the gross book is near flat on BTC (PF 0.95)
and underwater on ETH (PF 0.87), so the failure is the edge, not the
costs.

## Calibration note

Shipped exactly the specified parameters (AO 5/34, saucer/twin-peak
detectors, opposite-cross exits, 2xATR stop, 72-bar max hold, WARMUP=70).
A two-variant sweep (zero-cross-only entries; faster AO(8,21)) is reported
in CALIBRATION.md — neither variant rescues the strategy. The twin-peak
detector fired in synthetic tests (unit test) and on real data, but
real-data peaks are mostly momentum-noise dips, not the clean two-trough
reversals of the textbook pattern. What holds up: zero-cross is a fast,
cheap momentum switch; what doesn't: the pattern overlays add trades
without adding win rate.

## Mechanism

AO = SMA(5) - SMA(34) of (h+l)/2. Long entries on AO crossing above 0,
bullish saucer (three bars > 0, middle lowest, last rising), or bullish
twin peaks (two rising troughs < 0, no zero crossing between, AO rising).
Short entries mirror. Exits on the opposite zero-line cross (longs exit
when AO crosses below 0), 2xATR hard stop, 72-bar max hold.

Source: Awesome Oscillator (Bill Williams) — MetaTrader 5 docs —
https://www.metatrader5.com/en/terminal/help/indicators/bw_indicators/awesome

## Limitations

- Single 7-month, choppy-to-bearish crypto window; no bull-market sample.
- Funding unmodeled (short book would earn it; longs would pay).
- Next-bar-open execution vs idealized signal-bar entry.
- Twin-peak window fixed at 30 bars; slower (4h/daily) bars untested.
