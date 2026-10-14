# NR7 — Calibration

**Scope:** two robustness variants only; no parameter grid was run because
the shipped config already failed structurally (see BACKTEST.md). Sweep ran
via a throwaway script against the same HL 1h data, BTC/ETH/HYPE, same
risk config and execution convention. Nothing was changed in the shipped
strategy as a result.

## Shipped baseline (NR7, 7-bar window)

| Coin | Trades | Win% | Net % | Sharpe | MaxDD | Profit factor |
|---|---|---|---|---|---|---|
| BTC | 368 | 24.7% | -57.0% | -3.44 | -59.0% | 0.65 |
| ETH | 351 | 27.6% | -33.6% | -1.49 | -41.1% | 0.79 |
| HYPE | 367 | 28.9% | -55.0% | -4.06 | -55.0% | 0.67 |

## Variant A: NR4 (4-bar narrowest-range window)

Idea: a shorter compression window should catch faster contraction/expansion
cycles on 1h bars.

| Coin | Trades | Win% | Net % | Sharpe | MaxDD | Profit factor |
|---|---|---|---|---|---|---|
| BTC | 519 | 27.9% | -71.0% | -4.76 | -71.9% | 0.60 |
| ETH | 511 | 27.2% | -60.2% | -3.35 | -61.9% | 0.68 |
| HYPE | 516 | 29.5% | -53.1% | -3.04 | -53.1% | 0.75 |

**Verdict:** WORSE. ~510 trades per coin — the 4-bar window flags
compression almost constantly, so the "breakout" fires into ordinary chop
even more often. Negative on all three coins, deeper drawdowns. Confirms the
BACKTEST.md diagnosis: shortening the window just increases the false-signal
rate; the pattern's edge lives in its rarity, and rarity disappears on 1h.

## Variant B: range filter (NR7 + breakout-bar range > 1.2x the NR7 bar's range)

Idea: require the breakout bar to show real expansion — its range must exceed
1.2x the NR7 bar's range — a "volume-of-move" filter to cut weak breakouts.

| Coin | Trades | Win% | Net % | Sharpe | MaxDD | Profit factor |
|---|---|---|---|---|---|---|
| BTC | 309 | 27.5% | -49.4% | -2.90 | -52.9% | 0.69 |
| ETH | 298 | 29.5% | -18.3% | -0.66 | -31.0% | 0.89 |
| HYPE | 298 | 30.2% | -34.6% | -2.19 | -34.7% | 0.78 |

**Verdict:** BETTER but still a LOSER. Trade count drops ~17% and losses
shrink everywhere (ETH: -33.6% -> -18.3%, profit factor 0.89 — the closest
to breakeven anywhere), but the mechanism still has no gross edge: win rate
barely moves (24.7-28.9% -> 27.5-30.2%) and every coin stays negative.
Expansion-confirmation helps; it does not fix the core problem that 1h
crypto NR7 bars mark ordinary chop rather than genuine compression.

## Decision

Neither variant ships. Variant B's range filter is the better idea and is
worth carrying into any future volatility-compression strategy, but NR7 on
1h crypto is a dead end as implemented. The daily-bar version remains the
untested hypothesis (Crabel's original domain), not validated here.
