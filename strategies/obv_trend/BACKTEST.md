# OBV Trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-12
(~5,080 bars each).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: OBV, close vs EMA(50), OBV vs EMA(20) + 3-bar slope, rollover exits, 2xATR stop, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 506 | 18.2% | -$5,700 | -56.4% | -4.00 | -62.0% | -$11.26 | 0.59 |
| ETH | 483 | 18.0% | -$3,833 | -38.3% | -2.15 | -44.9% | -$7.94 | 0.73 |
| HYPE | 456 | 25.7% | -$734 | -7.0% | -0.27 | -23.0% | -$1.61 | 0.95 |
| **Combined** | **1,445** | **20.6%** | **-$10,267** | — | — | — | -$7.11 | — |

## Verdict: LOSER

Uniform loser: negative on all three, Sharpe -0.27 to -4.00, win rate
under 26%. The failure mode is mechanical: on 1h crypto the
price/EMA(50) and OBV/EMA(20) alignments flip constantly, so the
edge-triggered entries fire 450–500 times per coin over 7 months and the
rollover exits cut every position at the first wobble — win rate never
clears 20%. $3,607 in BTC fees alone. Granville's OBV confirms trends
after they are established; as a 1h timing trigger it is pure churn.

## Calibration note

Shipped the classic EMA(50)/EMA(20) construction without tuning. The
EMA sweep (34/50/100 trend filter, see CALIBRATION.md) shows no filter
length rescuing the book — the problem is the two-EMA alignment firing
into chop, not the window. What I verified: OBV accumulates signed
volume exactly (hand-checked), entries are genuinely edge-triggered
(no consecutive-bar double-fires), and indicators are lookahead-free by
truncation test.

## Mechanism

OBV(i) = OBV(i-1) + sign(c[i]-c[i-1]) * v[i]. Long state: close > EMA(50),
OBV > EMA(20 of OBV), 3-bar OBV slope > 0; entry on fresh alignment.
Short state mirrored. Exit on close crossing EMA(50) against the
position or OBV crossing its EMA(20) against it. 2xATR hard stop, no
trailing/target, 240-bar max hold.

Source: On-Balance Volume (Joseph Granville) — Investopedia —
https://www.investopedia.com/terms/o/onbalancevolume.asp

## Limitations

- Single 7-month window; the loss is too uniform to be a data artifact.
- Funding unmodeled.
- OBV on daily bars as a regime filter (rather than a 1h trigger) was not tested.
