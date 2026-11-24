# Premium/Discount — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local candle cache, window ms `[1773525600000, 1795525200000)`
(2026-03-14 22:00 UTC → 2026-11-24 14:00 UTC, last bar
2026-11-24 13:00 UTC): 6,111 bars BTC/ETH, 6,109 HYPE (HYPE's
first bar is 2026-03-15 00:00 UTC). Batch-45 frozen window — supersedes the Nov-14 window entirely.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap,
$10k start per coin. WARMUP=60 bars.

## Results (shipped config: 48-bar range, eq = midpoint, premium
75% / discount 25% of range, 12-bar touch window, long on cross
above eq after a discount touch, short mirror, exit on the
opposite eq cross, 2xATR stop, 3xATR trail, 60-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 292 | 22.60% | -$2,965.86 | -29.14% | -2.08 | -34.07% | -$10.16 | 0.72 | $2,638.34 |
| ETH | 256 | 25.78% | -$574.31 | -5.02% | -0.21 | -29.57% | -$2.24 | 0.94 | $2,079.32 |
| HYPE | 268 | 23.88% | +$1,552.77 | +16.46% | +1.04 | -14.84% | +$5.79 | 1.14 | $1,501.54 |
| **Combined** | **816** | **24.02%** | **-$1,987.40** | — | — | — | **-$2.44** | — | **$6,219.21** |

Net % is the final-equity return (it includes the mark-to-market
of any position still open at the window end); Net $ is the sum
of closed-trade PnL.

## Verdict: loser overall — the reclaim does not follow through,
except on HYPE

Combined -$1,987.40 on 816 trades, win rate 24.02%, profit
factor 0.72–0.94 on BTC/ETH. The setup fires constantly (292
trades on BTC alone — equilibrium crosses on 1h crypto are
routine noise, and the 12-bar touch window is almost always
satisfied in a wide range), and the reclaim usually fails:
price crosses the midpoint, then crosses straight back, and
the 2xATR stop or the opposite-cross exit takes the loss. BTC
is the worst of it (-$2,965.86, Sharpe -2.08, MaxDD -34.07%).

The one honest nuance: HYPE wins (+$1,552.77, PF 1.14, Sharpe
+1.04, the only positive coin) — but on 268 trades at 23.88%
win rate, that is a handful of large winners carrying a
negative-expectancy base rate, not evidence the pattern
generalises. One coin out of three, in the same window, is
what a coin flip looks like.

Vs the Nov-14 window the story is unchanged: combined net
moved only from -$1,910 (789 trades) to -$1,987.40 (816
trades); BTC got worse (-$2,720 → -$2,965.86), ETH improved
(-$835 → -$574.31), HYPE slightly worse (+$1,645 → +$1,552.77).
Ten more days of data did not rescue or condemn the system
any further — it just confirmed the same failure mode.

## Calibration note

Shipped the specified lookback=48. A 24/48/96 lookback sweep,
re-run on the batch-45 window, is in CALIBRATION.md: 24 is far
worse combined (-$7,968.26, 1,553 trades — more crosses, more
fees, same failure); 96 is least-bad combined (-$1,747.26, 377
trades) but still negative on BTC and ETH. The lookback is not
the problem — the equilibrium reclaim on 1h bars does not
predict continuation. The 48-bar config was fixed before any
backtest was run; no in-sample adoption.

## Mechanism

ICT premium/discount (Michael Huddleston): over a rolling
48-bar range, eq = (high48 + low48) / 2, premium = low48 +
0.75 × (high48 − low48), discount = low48 + 0.25 ×
(high48 − low48). Long when close crosses above eq while
the lowest low of the last 12 bars touched discount (min low
≤ discount); short mirror after a premium touch (max high ≥
premium). Exit on the opposite cross of eq. 2xATR hard stop,
3xATR chandelier trail, 60-bar max hold.

Source: ICT premium/discount (Michael Huddleston) —
https://www.luxalgo.com/library/concept/premium-and-discount/

## Limitations

- Single 8-month crypto window; 816 trades is a fair sample
  and it still loses — the failure is not sample size.
- 24.02% win rate with PF < 0.95 on two of three coins; the
  touch condition is weak (in a wide range the extremes are
  touched constantly, so it barely filters).
- Equilibrium crosses are whipsaw-prone on 1h bars; a
  confirmation filter (e.g. a close beyond eq, or a displacement
  leg) would be a different strategy, not a calibration.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped lookback on this window.
