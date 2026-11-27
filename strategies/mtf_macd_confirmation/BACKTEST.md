# Multi-Timeframe MACD Confirmation — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE. Funding not
modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=200 bars.

## Results (shipped config: 1h MACD(12, 26, 9) signal-line cross,
filtered to the 4h MACD histogram's sign; exit on the 1h cross
back or the 4h histogram crossing zero; 2xATR stop, 3xATR
trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 173 | 31.2% | -$893 | -8.8% | -0.61 | -18.4% | -$5.16 | 0.88 |
| ETH | 168 | 27.4% | -$2,375 | -23.8% | -1.97 | -24.9% | -$14.14 | 0.64 |
| HYPE | 163 | 29.4% | -$465 | -3.1% | -0.20 | -18.7% | -$2.85 | 0.93 |
| **Combined** | **504** | **29.4%** | **-$3,733** | **-11.9%** | **-1.33** | **-13.8%** | **-$7.41** | **0.82** |

Fees: BTC $1,863.53, ETH $1,235.69, HYPE $828.47 (total
$3,927.69). Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL. Combined end equity
$26,442.14 on $30k start.

Exit breakdown: BTC signal 103 / stop 70; ETH signal 84 /
stop 84; HYPE signal 110 / stop 53. No max-hold exits: every
trade resolved on a signal exit or a stop within the week.

## Verdict: a clean loser -- the 4h filter does not save MACD crosses on 1h crypto

Combined -$3,733 on 504 trades (29.4% win rate, PF 0.82) is a
real, well-sampled loss, not noise: all three coins lose, ETH
worst (-$2,375, Sharpe -1.97). The cross-based entries did
their job mechanically -- 504 trades over ~8.5 months is ~2
trades per coin per week, no churn explosion -- but the
edge is not there: MACD signal-line crosses on 1h bars lag
the move, and the 4h histogram filter keeps the trade
pointing the way the market already went rather than the way
it is about to go. The stop exits (207 of 504) show the 2xATR
stop doing most of the losing work; the signal exits (297)
are mostly small give-backs as the MACD whipsaws back across
its signal line. Honest read: the Elder Triple Screen at
1h/4h resolution on this window is a negative-expectancy
trend-following system. Do not trade it live.

## Mechanism

1h MACD(12, 26, 9) from `strategies.base.macd`; 4h MACD from
`strategies.timeframes.macd_4h_aligned`, which maps only
COMPLETED 4h bars onto the 1h grid (backward as-of join on
the 4h bar's close time). Long on a 1h cross above the signal
line with a positive 4h histogram; short mirror. Exit on the
1h cross back, the 4h histogram crossing zero, or the
opposite entry; 2xATR hard stop, 3xATR chandelier trail,
168-bar max hold behind them.

Source: Quantpedia, "How to Design a Simple Multi-Timeframe
Trend Strategy on Bitcoin" --
https://quantpedia.com/how-to-design-a-simple-multi-timeframe-trend-strategy-on-bitcoin/
(Elder Triple Screen principle).

## Limitations

- Single ~8.5-month crypto window (a strong downtrend into
  November 2026 dominates the second half); funding
  unmodeled; next-bar-open execution vs idealized entry.
- The 4h filter is NaN for the first ~136 bars, so the
  strategy is flat for the first ~5.7 days of the window.
- Never tune the shipped MACD parameters on this window.
