# Opening Range Breakout Failure Fade — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 13:00 UTC Nov 27): 6,185 bars BTC/ETH, 6,183 HYPE. Funding
not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars. Both sides.

## Results (shipped config: OR = first 4 bars of the UTC day,
break = close crossing or_high / or_low, failure = close back
inside within 6 bars; entry on the failure bar; exit on a
close back beyond the frozen range level or the opposite fade
entry; 2xATR stop, 3xATR trail, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 264 | 29.2% | -$2,462.77 | -24.6% | -1.84 | -27.2% | -$9.33 | 0.74 | $2,633.74 |
| ETH | 248 | 25.4% | -$1,950.00 | -19.5% | -1.53 | -28.8% | -$7.86 | 0.79 | $2,054.36 |
| HYPE | 271 | 29.2% | -$1,866.67 | -18.7% | -1.61 | -27.4% | -$6.89 | 0.80 | $1,285.62 |
| **Combined** | **783** | **28.0%** | **-$6,279.44** | **-20.9%** | **-2.58** | **-24.5%** | **-$8.02** | **0.77** | **$5,973.72** |

Exit-reason breakdown: BTC signal 153 / stop 82 / max_hold 29;
ETH signal 156 / stop 69 / max_hold 23; HYPE signal 189 /
stop 61 / max_hold 21. Net % is the final-equity return
($30k combined -> $23,720.56); Net $ is the sum of
closed-trade PnL.

## Verdict: the fade churns, and fees do the killing

Combined -$6,279 on 783 trades (win rate 28.0%, PF 0.77) is
the batch's worst loser by dollars, and the mechanism is
churn, not catastrophe: ~3 trades a day per coin, a 28%
win rate, and $5,974 of fees on $6,279 of net loss. Gross
PnL before fees is only -$306 combined (BTC +$171 and ETH
+$104 gross, HYPE -$581) -- the fade is roughly break-even
before costs, and the 0.055%-per-side round trip on 783
trades eats it alive. The signal exits dominate (498 of 783):
the fade usually exits quickly on a reclaim of the range
level for a small win or small loss, and the 212 stop exits
are where the real breakouts run over the fade. 73 trades
hit the 24-bar max hold. BTC and ETH record identical break
counts (263 up / 228 down each) -- verified genuine, not a
bug: the opening-range levels are coin-specific (e.g. BTC
or_high 71,570 vs ETH 2,232.7 on the same day), and the two
coins simply break their narrow 4-bar ranges on the same
days with the same frequency; their entry counts differ
(124/155 vs 122/140 long/short). Honest read: on 1h crypto
the opening range is too narrow to mean anything -- price
breaks it and re-enters it several times a day, so "failure"
is the normal state, not a signal. Fading every failure is
fading noise at taker fees.

## Mechanism

indicators.py computes each UTC day's opening range from its
00:00-03:00 bars and forward-fills it from 04:00. signals.py
detects breaks with crossed_above / crossed_below, arms a
pending setup per break (frozen level carried in
fail_up_level / fail_down_level), and enters on the first
re-cross back inside within 6 bars (crossed_below /
crossed_above on the frozen level); a new break or a new UTC
day cancels the pending setup. Exits fire on a close back
beyond the entry-frozen range level or on the opposite fade
entry; the house 2xATR stop / 3xATR trail sit behind them,
with a 24-bar max hold. Breaks per coin: BTC 263 up / 228
down, ETH 263 / 228, HYPE 247 / 256; fade entries: BTC 124
long / 155 short, ETH 122 / 140, HYPE 152 / 132 (entries
exceed closed trades slightly -- some fire while a position
is already open and the harness ignores them).

Source: Opening range breakout failure fade — ORB failure --
https://steady-turtle.com/knowledge/opening-range-breakout-strategy

## Limitations

- 783 trades: the backtest measures a high-frequency churn
  regime, not a handful of clean setups; per-trade expectancy
  (-$8.02) is small next to the fee drag.
- Gross PnL near zero means the verdict is fee-driven: at
  zero fees this is roughly break-even, not an edge.
- Single ~8.4-month crypto window; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The 04:00-bar breakout is not detected (no prior-bar level
  in the series); see README.
- Never tune the shipped OR window or failure window on
  this window.
