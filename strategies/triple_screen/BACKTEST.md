# Elder Triple Screen — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars,
2026-03-14 22:00 UTC → 2026-10-10 13:00 UTC (BTC/ETH 5037 bars, HYPE 5035 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR(14) stop, 3x leverage cap, $10k start.
Warmup 168 bars.

## Results (shipped config: 4h MACD(12,26,9) tide / 1h FI2 wave / prior-bar break trigger, 2xATR stop)

| Coin | Trades (signals) | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 345 (350) | 47.2% | -$3,080.81 | -30.8% | -4.74 | -31.1% | -$8.93 | 0.54 |
| ETH | 300 (302) | 53.3% | -$1,820.48 | -18.2% | -2.99 | -19.9% | -$6.07 | 0.66 |
| HYPE | 385 (388) | 53.0% | -$3,156.63 | -31.6% | -5.02 | -33.7% | -$8.20 | 0.58 |
| **Combined** | **1,030** | **51.1%** | **-$8,057.92** | — | — | — | **-$7.82** | — |

**Trade count, prominently:** ~1,000 trades over 7 months across three coins —
the three-screen conjunction does NOT produce a sparse system on 1h crypto
bars. The FI2 zero-cross fires in chop nearly as often as in real waves.

## Verdict: LOSER — negative on all three coins

Win rates near 50% with profit factors 0.54–0.66: the system gets direction
right about as often as a coin flip, but the tide-flip/FI2-hook exits cut
winners while the 2xATR stop absorbs full losers. The 4h MACD-histogram tide
is the weak link — on 1h crypto the histogram slope whipsaws between 4h
bars (it decays to zero in any established trend, so the "tide" flips on
noise), arming entries in both directions within the same trend leg.

## Mechanism

Screen 1 (tide): 4h MACD(12,26,9) histogram slope, taken from the most
recent *closed* 4h bar (shifted before forward-fill — no lookahead).
Screen 2 (wave): 1h 2-period EMA of Force Index crossing zero with the
tide. Screen 3 (trigger): bar's high takes out the prior bar's high
(long) / low undercuts prior low (short); the harness executes at the
next bar's open, one bar later than a true stop fill — an approximation
that biases results against the strategy. Exit on tide flip or FI2 hook
against the position. 2xATR(14) protective stop, 336-bar max hold.
Reuses this branch's `strategies/force_index` indicators module.
