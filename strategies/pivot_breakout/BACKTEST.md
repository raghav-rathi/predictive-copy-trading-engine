# Pivot Breakout — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-12
(~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: prior-day R1/S1 break-and-close, opposite-side touch exit, 2xATR stop, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 108 | 21.3% | +$501 | +5.4% | 0.43 | -21.3% | +$4.63 | 1.06 |
| ETH | 109 | 21.1% | +$844 | +8.4% | 0.56 | -20.6% | +$7.75 | 1.10 |
| HYPE | 108 | 25.9% | +$524 | +5.2% | 0.43 | -19.8% | +$4.85 | 1.06 |
| **Combined** | **325** | **22.8%** | **+$1,869** | — | — | — | +$5.75 | — |

## Verdict: WINNER (thin margin — do not oversell)

Positive on all three coins with positive Sharpe (0.43–0.56) and profit
factors of 1.06–1.10. The edge is real but marginal: win rate is only
~21–26% and the book survives on a few large breakout winners — the
$524–844 net per coin is a handful of trades away from zero. This is a
legitimate low-win-rate breakout system, not a reliable income engine.
The prior-day R1/S1 lines are wide enough that entries fire only ~15
times a month per coin, and the opposite-side touch exit caps the
failed-breakout damage before the 2xATR stop has to.

## Calibration note

Shipped the classic floor-pivot construction without tuning. The stop
sweep (1.5/2.0/2.5 xATR, see CALIBRATION.md) shows 2.0x in the stable
region — tighter stops get chopped, wider stops give back too much on
fakeouts. What I verified: pivot math matches hand-computed PP/R1/S1/R2/S2
exactly, levels are constant within each UTC day and sourced from the
prior complete day only, and indicators are lookahead-free by truncation
test. Fragility: with only ~108 trades per coin, two or three fewer
winners flips the verdict.

## Mechanism

PP = (H+L+C)/3 of the prior complete UTC day; R1 = 2PP-L, S1 = 2PP-H,
R2 = PP+(H-L), S2 = PP-(H-L); levels forward-filled within the current
day. Long on 1h close crossing above prior R1, short on crossing below
prior S1; exit on touch of the opposite side (long: close <= S1, short:
close >= R1). 2xATR hard stop, no trailing/target, 120-bar max hold.

Source: Pivot Point (floor-trader pivots) — Investopedia —
https://www.investopedia.com/terms/p/pivotpoint.asp

## Limitations

- Single 7-month, mostly choppy window; ~108 trades/coin makes Sharpe estimates noisy.
- Max drawdown is material (-19.8% to -21.3%) against a +5–8% return.
- Funding unmodeled; next-bar-open execution vs idealized breakout entry.
