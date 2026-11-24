# Livermore — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only via the pinned batch-45 runner
(`scripts/run_pinned_backtest45.py`), window ms
`[1773525600000, 1795525200000)` (2026-03-14 22:00 UTC →
2026-11-24 14:00 UTC exclusive; last bar 2026-11-24 13:00 UTC):
6,111 bars BTC/ETH, 6,109 HYPE (first HYPE bar 2026-03-15
00:00 UTC). Batch 45 refresh of the Nov-14 build; the stale
Nov-14 window numbers have been replaced, not kept alongside.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=60 bars.

## Results (shipped config: long on a close above the prior
20-bar high with higher swing lows, short mirror with lower
highs, exit on a break of the prior 10-bar low/high, 2xATR
stop, 3xATR trail, 60-bar max hold)

| Coin | Bars | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|---|
| BTC | 6,111 | 139 | 33.09% | -$86.55 | -0.87% | +0.05 | -21.52% | -$0.62 | 0.99 | $1,461.27 |
| ETH | 6,111 | 133 | 34.59% | +$800.88 | +8.01% | +0.60 | -18.77% | +$6.02 | 1.12 | $1,031.82 |
| HYPE | 6,109 | 152 | 32.89% | -$1,477.93 | -14.78% | -1.05 | -23.48% | -$9.72 | 0.81 | $714.26 |
| **Combined** | **18,331** | **424** | **33.49%** | **-$763.60** | — | — | — | **-$1.80** | — | **$3,207.36** |

Net % is the final-equity return (it includes the mark-to-market
of any position still open at the window end); Net $ is the sum
of closed-trade PnL.

## Verdict: loser overall, but the least-bad of this batch —
closest to break-even, and the failure is concentrated

Combined -$763.60 on 424 trades, win rate 33.49% — the smallest
combined loss and the best per-trade expectancy (-$1.80) of
this batch's strategies. BTC is nearly flat (-$86.55, PF 0.99,
Sharpe +0.05), ETH wins (+$800.88, PF 1.12), and the whole
combined loss is HYPE (-$1,477.93, PF 0.81, Sharpe -1.05).
HYPE fires far more signals than the other coins and trends
harder and chops harder on 1h, and the 20-bar breakout with the
higher-lows filter catches the chop. The structure filter helps
— a bare 20-bar breakout would be worse — but "helps" here
means "loses slowly": there is no coin on which this is a system
to run.

Unlike fakey, the loss here is cost-driven, not signal-driven:
gross of fees the book is +$2,443.76 (BTC +$1,374.72, ETH
+$1,832.71, HYPE -$763.67) — the signal is roughly breakeven
gross, and $3,207.36 of fees turns it negative. That is the one
respect in which this strategy is not a write-off: at lower
fees, or with a filter that cuts the HYPE chop, there is
something to investigate. As shipped, it is still a loser.

## Calibration note

Shipped the specified breakout_lookback=20. A 10/20/30
breakout sweep is in CALIBRATION.md: 10 is least-bad combined
(+$209.38, 552 trades, BTC +$62.15, ETH +$1,196.77) but still
losing on HYPE (-$1,049.53); 30 is worst combined (-$1,261.60).
The lookback moves the loss around, never flips it decisively.
The 20-bar config was fixed before any backtest was run; no
in-sample adoption — the lb10 combined number being slightly
positive on this window does not change that.

## Audit (batch 45 refresh)

All 8 files re-read and re-verified on the batch-45 window. No
lookahead found: `brk_high`/`brk_low` are the prior 20-bar
extremes (rolling window shifted by 1); the swing-low/high
comparisons use 10-bar windows ending 10 and 20 bars ago
(shifts of 10 and 20); `exit_low`/`exit_high` are prior-10-bar
extremes (shift 1); `crossed_above`/`crossed_below` compare
only bar i and bar i-1. NaN handling is explicit
(`.fillna(False)` on every signal column; boolean dtype
enforced). No bug found, no code changed in this refresh —
parameters untouched.

## Mechanism

Jesse Livermore, "How to Trade in Stocks" (1940): higher
highs / higher lows define an uptrend, lower highs / lower
lows a downtrend. Long when close breaks above the highest
high of the prior 20 bars AND the most recent swing low is
above the previous swing low — implemented as the 10-bar low
ending 10 bars ago (bars i−19..i−10) being higher than the
10-bar low ending 20 bars ago (bars i−29..i−20). Short
mirror: close below the prior 20-bar low AND the 10-bar high
ending 10 bars ago lower than the one ending 20 bars ago.
Exit long on a close below the prior 10-bar low; exit short
on a close above the prior 10-bar high. 2xATR hard stop,
3xATR chandelier trail, 60-bar max hold.

Source: Jesse Livermore, "How to Trade in Stocks" (1940) —
systematized in MQL5, "Automating Classic Market Methods
(Part 6): Jesse Livermore's Pivotal Point System":
https://www.mql5.com/en/articles/24075

## Limitations

- Single 8.5-month crypto window; 424 trades, combined PF
  below 1.0 — the edge is ~zero gross, negative net.
- HYPE dominates the loss: the same breakout rules behave
  very differently per coin, and the 20-bar window is too
  short for HYPE's chop.
- The higher-lows filter compares two adjacent 10-bar
  windows — a weak trend definition on 1h bars; a genuine
  trend filter (structure over a longer window) would be a
  different strategy, not a calibration.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped breakout lookback on this window.
