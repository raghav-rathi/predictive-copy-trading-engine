# Elder Ray — Backtest

Window: 2026-03-14 → 2026-10-22, Hyperliquid 1h candles (cache, no
network writes). Start equity $10,000 per coin. Execution at bar i+1
open, taker fee 0.00045/side + slippage 0.0001/side, no funding,
WARMUP=60. Parameters fixed a priori (see CALIBRATION.md) — no tuning.

## Per-coin results

| Coin | Trades (L/S) | Win rate | Net $ | Net % | Sharpe | Max DD % | Expectancy $ | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 803 (418/385) | 30.5% | -8,559 | -85.6% | -12.79 | -86.4% | -10.66 | 0.38 | 5,643 |
| ETH | 850 (413/437) | 28.9% | -8,488 | -84.9% | -11.73 | -84.9% | -9.99 | 0.41 | 4,738 |
| HYPE | 768 (395/373) | 37.0% | -6,690 | -67.0% | -8.52 | -67.1% | -8.71 | 0.52 | 2,893 |
| **Combined** | **2,421** | **32.0%** | **-23,737** | — | — | — | **-9.80** | — | **13,274** |

Exit reasons (all coins): signal exits dominate (~83-84% of trades),
hard stops the rest. Both sides lose: longs -$12,883, shorts -$10,855
combined — the mirror offers no refuge.

## Honest verdict: LOSER

Elder Ray, as published (dip-in-uptrend / rip-in-downtrend around
EMA(13)), does not survive 2026 Hyperliquid 1h data:

1. **Negative expectancy on every coin** (-$8.71 to -$10.66/trade).
   Profit factors 0.38–0.52: losers are ~2x winners in size, and the
   win rate (29–37%) can't compensate.
2. **Turnover is the killer.** ~800 trades per coin over 5,330 bars —
   a signal every ~6.6 bars. Bear/bull power oscillates around zero
   constantly in crypto chop, so "dip while bears weaken" fires all
   the time; fees alone ($13,274 combined) exceed half the total loss.
3. **Signal exits cut winners, stops take the rest.** 84% of trades
   exit on signal (power exhaustion / slope reversal) — in a
   mean-reverting chop regime the "exhaustion" exit fires right as
   momentum would extend, while the 1.5xATR stop eats the entries
   that immediately reverse.

What would need to change (not done — params were fixed a priori):
a regime filter so the triggers only fire in trending markets
(Elder's own Triple Screen context), wider stops, and a minimum
power-magnitude threshold to stop trading noise around zero. As
shipped, this is a documented, reproducible loser — kept in the
engine as the honest record, not as a tradable signal.
