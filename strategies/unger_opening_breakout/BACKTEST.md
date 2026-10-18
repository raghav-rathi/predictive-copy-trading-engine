# Unger Opening Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-18
(~5,222 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled
(notes as limitation).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 3-bar (00:00-03:00 UTC) opening range, first-close-beyond entry, one trade per side per day, no take-profit, 1.5xATR chandelier trail, 1.5xATR stop, 21-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 287 | 27.5% | -$4,392 | -43.9% | -3.48 | -46.3% | -$15.30 | 0.59 |
| ETH | 276 | 31.9% | -$3,385 | -33.9% | -2.89 | -34.6% | -$12.26 | 0.66 |
| HYPE | 282 | 29.1% | -$3,982 | -39.8% | -3.77 | -39.8% | -$14.12 | 0.61 |
| **Combined** | **845** | **29.5%** | **-$11,759** | — | — | — | -$13.92 | — |

## Verdict: LOSER (worst of the batch)

The biggest loser of batch 9: -$11,759 combined on 845 trades, profit
factor 0.59-0.66 on every coin, Sharpe -2.9 to -3.8. Unger's opening-range
breakout is a session-structure trade: it assumes the first 2-3 hours
concentrate the day's informed order flow (pit open, economic releases,
cash-equity open). On 24/7 crypto there is no session open -- the
00:00-03:00 UTC "range" is three arbitrary hours of overnight chop, so the
"breakout" is just the first wiggle past a noise band, and the 1.5xATR
trail gives back the wiggle on the next bar. Win rates near 30% with the
trail doing all the exits means breakouts almost never extend: this is a
fade-the-opening-range market wearing a breakout costume. ~$7.4k in
combined fees on 845 trades finishes the job, but PF at 0.6 says the
premise fails before costs.

## Calibration note

Shipped exactly the specified parameters (3-bar opening range, first
close beyond the range per side per day, no take-profit, 1.5xATR trail,
1.5xATR stop, 21-bar max hold, WARMUP=48). A one-variant sweep (tighter
2-bar opening range) is reported in CALIBRATION.md -- no improvement,
shipped config stays.

## Mechanism

Session day = UTC day. Opening range = high/low of the first 3 hourly
bars (00:00-03:00 UTC). Enter on the first 1h bar that closes beyond the
range (long above, short below); only one trigger per side per day. No
take-profit (Unger's rule -- let it run); the 1.5xATR chandelier trail and
1.5xATR hard stop (the opposite range extreme is the natural technical
level; 1.5xATR is its ATR-scaled proxy) manage the trade; 21-bar max hold
flattens by session end.

Source: Andrea Unger interview (4x World Cup Trading Champion) --
https://bettersystemtrader.com/016-andrea-unger/

## Limitations

- Single 7-month crypto window; no futures/equities session-structure sample.
- UTC-day session is a modeling choice; crypto has no true session open.
- Funding unmodeled (shorts would earn it on most days).
- Next-bar-open execution vs idealized signal-bar entry.
- 1h granularity: Unger's original systems ran on finer intraday bars.
