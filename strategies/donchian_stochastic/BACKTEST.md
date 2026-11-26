# Donchian Stochastic — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: 20-bar Donchian breakout with
Stochastic(14,3,3) filter — long above the prior 20-bar high
with %K > %D and %K < 80, short below the prior 20-bar low
with %K < %D and %K > 20; Turtle exit on the 10-bar channel
or a %K/%D cross; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 22 | 13.6% | -$61 | -0.6% | -0.07 | -4.9% | -$2.80 | 0.93 |
| ETH | 31 | 35.5% | -$175 | -1.8% | -0.66 | -2.7% | -$5.66 | 0.68 |
| HYPE | 8 | 25.0% | +$405 | +4.0% | +2.06 | -1.4% | +$50.57 | 3.65 |
| **Combined** | **61** | **26.2%** | **+$168** | — | **+0.26** | **-2.2%** | **+$2.75** | **1.10** |

Fees: BTC $315, ETH $266, HYPE $47 (total $628).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined equity ends
at $30,168 on a $30,000 start.

## Verdict: a $168 "win" on 61 trades — statistically nothing, carried by 8 HYPE trades

Combined +$168 (PF 1.10, Sharpe +0.26) is a rounding error
on $628 of fees, and the coin split gives it away: HYPE is
+$405 on just 8 trades (PF 3.65, Sharpe +2.06 — two or three
good trades doing all the work), while BTC (−$61, win rate
13.6%, PF 0.93) and ETH (−$175, PF 0.68) both lose. The
headline number is the Stochastic filter doing its job too
well: it blocks ~90% of Donchian breakouts (61 trades here
vs 536 for the RSI-filtered Donchian combo on the same
window), because a breakout close sits at the extreme of
its 14-bar range and %K is near 100/0 unless the breakout
bar carries a real wick. The 61 trades that do pass are a
tiny, wick-selected sample, and the combined +$168 rests
entirely on HYPE's 8. Signal exits dominate (17 / 29 / 8
vs 5 / 2 / 0 stops) — when it does trade, the Turtle/%K
exit usually ends the trade, not the stop. Honest read: no
edge demonstrated. The filter buys selectivity at the cost
of sample size, and the one positive coin is too thin to
generalise from.

## Mechanism

Richard Donchian's channel: upper = highest high, lower =
lowest low of the last 20 periods. Long when the close
crosses above the prior 20-bar high (channel shifted by 1,
so the breakout is vs the prior 20 bars) with %K > %D and
%K < 80; short when the close crosses below the prior
20-bar low with %K < %D and %K > 20. Stochastic(14,3,3):
%K = 100×(close − lowest low(14))/(highest high(14) −
lowest low(14)); %D = SMA(%K, 3); a zero 14-bar range
prints %K = 50.0 (neutral). Exit is the classic Turtle
10-bar channel (long exits on a close below the prior 10-bar
low, short on a close above the prior 10-bar high) OR a
%K/%D cross against the position. The exit shift is
required, not optional: the unshifted 10-bar low includes
the current bar's own low, and the close can never be below
it, so the unshifted exit could never fire. The harness
2xATR hard stop / 3xATR chandelier trail sit behind the
Turtle/momentum exit as a safety net for gap-through-channel
moves; 120-bar max hold.

Source: Richard Donchian — Donchian channel —
https://en.wikipedia.org/wiki/Donchian_channel; Stochastic
oscillator (George Lane) —
https://en.wikipedia.org/wiki/Stochastic_oscillator (verified
via web search 2026-11-26; confirms %K/%D construction and
the 80/20 overbought/oversold levels).

## Limitations

- Single ~8.5-month crypto window; the verdict rests on 61
  trades total (8 on HYPE), so no single-coin read
  generalises and the combined +$168 is noise-level.
- The %K filter is wick-dependent: it passes breakouts only
  when the breakout bar has a large wick, which selects a
  non-representative subset of breakouts.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped entry window on this window.
