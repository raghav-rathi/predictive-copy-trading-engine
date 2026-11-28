# Day-of-Week Effect (Bitcoin) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 2026-11-27 13:00 UTC): 6,185 bars BTC/ETH, 6,183 HYPE.
Funding not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: LONG Mondays, SHORT Thursdays,
UTC; 2xATR stop, 3xATR trail, 30-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 73 | 39.7% | +$738.64 | +7.4% | 0.75 | -13.4% | +$10.12 | 1.20 | $857.27 |
| ETH | 73 | 52.1% | +$2,877.49 | +28.8% | 2.36 | -8.0% | +$39.42 | 1.87 | $704.49 |
| HYPE | 73 | 39.7% | +$1,447.72 | +14.5% | 1.48 | -8.4% | +$19.83 | 1.40 | $402.51 |
| **Combined** | **219** | **43.8%** | **+$5,063.85** | **+16.9%** | **1.80** | **-5.3%** | **+$23.12** | **1.48** | **$1,964.28** |

Exit-reason breakdown: BTC stop 58 / signal 15; ETH stop
56 / signal 17; HYPE stop 54 / signal 19. Combined: stop
168, signal 51, max_hold 0. Net % is the final-equity
return ($30k combined -> $35,063.85); Net $ is the sum of
closed-trade PnL.

Per leg (shipped run, grouped by side; sizing follows the
shared equity path, so these are attribution, not
standalone runs): Monday longs 108 trades, 41 wins (38.0%),
net +$1,250.57 (BTC -$163.00, ETH +$1,107.15, HYPE
+$306.42); Thursday shorts 111 trades, 55 wins (49.5%),
net +$3,813.29 (BTC +$901.64, ETH +$1,770.35, HYPE
+$1,141.30). The Thursday short did ~75% of the profit.

## Verdict: net-positive, but read it as one window's luck until proven otherwise

Combined +$5,063.85 on 219 trades (win rate 43.8%, PF 1.48,
Sharpe 1.80) is the strongest batch-49 result on paper --
and it is not a fee story (gross PnL before the $1,964 of
fees is +$7,028). But three facts cut against trusting it:

1. **The calendar barely does the exiting.** 168 of 219
   trades (77%) die on the 2xATR stop, not the timed exit.
   A 24-hour leg routinely moves more than 2x the 14-hour
   ATR, so what this strategy mostly measures is whether
   price pokes 2 ATR against the leg within a day -- the
   weekday label is riding on top of a stop lottery.
2. **One coin carries it.** ETH is +$2,877 (Sharpe 2.36);
   BTC is barely positive at +$739 (PF 1.20, maxDD -13.4%).
   A weekday effect that only really shows up on one of
   three coins in one window is exactly what noise looks
   like.
3. **The literature is mixed and the effect is small.**
   Weekday seasonality in Bitcoin has been found, lost, and
   re-found across samples; a single 8.5-month window in a
   down-drifting regime cannot settle it. The Monday leg on
   its own is only +$1,213 (see CALIBRATION.md) -- the
   result leans on the Thursday short, i.e. on Thursdays
   being bad in this particular window.

Honest read: a real, tradeable-looking +16.9% on this
window that I would not size up without an out-of-sample
check. The mechanism is cheap to run and the downside is
bounded by the stop, but do not mistake one window for an
edge.

## Mechanism

Indicators.py derives UTC weekday/hour from each bar's
timestamp plus ATR(14). signals.py fires long_entry on
Sunday 23:00, long_exit on Monday 23:00, short_entry on
Wednesday 23:00, short_exit on Thursday 23:00 -- each on
exactly one bar per week; the harness executes each at the
next bar's open, so the legs cover the full Monday and
Thursday UTC days. The house 2xATR stop / 3xATR trail sit
behind the timed exits, with a 30-bar max hold.

Sources: Decourt, Chohan & Perugini 2017; Caporale &
Plastun 2018 -- https://mpra.ub.uni-muenchen.de/id/eprint/91429/contents
-- and FairHatch 2026 Binance daily data.

## Limitations

- Single ~8.5-month window, all three coins in the same
  regime for much of it; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 219 trades is a real sample for the combined figure, but
  the per-leg split (108/111) and per-coin split (73 each)
  are thin, and the three coins are not independent bets.
- The 2xATR stop dominates exits (77%): the result is
  sensitive to the stop width, which is a house parameter,
  not part of the weekday hypothesis.
- Never tune the shipped legs on this window.
