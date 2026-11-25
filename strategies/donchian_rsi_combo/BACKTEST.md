# Donchian RSI Combo — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: 20-bar Donchian breakout with
RSI(14) filter — long above the prior 20-bar high with RSI <
70, short below the prior 20-bar low with RSI > 30; Turtle
exit on the 10-bar channel; 2xATR stop, 3xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 177 | 30.5% | -$1,935 | -18.2% | -1.11 | -30.6% | -$10.93 | 0.76 |
| ETH | 159 | 37.1% | +$1,411 | +15.5% | +1.03 | -11.9% | +$8.87 | 1.19 |
| HYPE | 200 | 35.0% | +$1,166 | +14.0% | +0.87 | -16.3% | +$5.83 | 1.10 |
| **Combined** | **536** | **34.1%** | **+$642** | — | **+0.39** | **-9.4%** | **+$1.20** | **1.02** |

Fees: BTC $1,769, ETH $1,336, HYPE $1,114 (total $4,219).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a small winner on paper, a loser on BTC — the
classic Donchian story in miniature

Combined +$642 on 536 trades (PF 1.02, Sharpe +0.39) is a
win by $642 and a rounding error by any other measure.
ETH (+$1,411, Sharpe +1.03, PF 1.19) and HYPE (+$1,166,
Sharpe +0.87, PF 1.10) are both solidly positive, while BTC
(-$1,935, Sharpe -1.11, MaxDD -30.6%, PF 0.76) loses more
than either makes alone. Stop exits dominate (144 / 124 /
151 vs 33 / 35 / 49 signal exits): the 10-bar Turtle exit
is wide on 1h bars, so the 2xATR stop usually ends the
trade first — the system pays for breakouts that reverse
before the channel can confirm the turn. Win rates 30–37%
with PF ~1.0–1.2 say the RSI filter keeps out the worst
overextended entries but does not create an edge by itself.
Honest read: two coins say the Turtle breakout still works
a little, one coin says it doesn't, and the combined
+$642 on $4,219 of fees is not evidence to trade on.

## Mechanism

Richard Donchian's channel: upper = highest high, lower =
lowest low of the last 20 periods. Long when the close
crosses above the prior 20-bar high (channel shifted by 1,
so the breakout is vs the prior 20 bars) with RSI(14) < 70;
short when the close crosses below the prior 20-bar low
with RSI(14) > 30. Exit is the classic Turtle 10-bar
channel: long exits on a close below the prior 10-bar low,
short on a close above the prior 10-bar high. The exit
shift is required, not optional: the unshifted 10-bar low
includes the current bar's own low, and the close can never
be below it, so the unshifted exit could never fire. The
harness 2xATR hard stop / 3xATR chandelier trail sit behind
the Turtle exit as a safety net for gap-through-channel
moves; 120-bar max hold.

Source: Richard Donchian — Donchian channel —
https://en.wikipedia.org/wiki/Donchian_channel (verified via
web search 2026-11-25; confirms Upper = HighestHigh(N),
Lower = LowestLow(N), N usually 20, and the long-on-break-
above / short-on-break-below rule).

## Limitations

- Single ~8.4-month crypto window; the verdict is
  coin-dependent (ETH/HYPE positive, BTC negative), so no
  single-coin read generalises.
- The 10-bar exit lags on 1h bars: stop exits outnumber
  signal exits ~4:1, so most trades are decided by the
  harness stop, not the Turtle logic.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped entry window on this window.
