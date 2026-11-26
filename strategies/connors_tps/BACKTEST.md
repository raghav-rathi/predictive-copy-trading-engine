# Connors TPS — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-47 window ms `[1773525600000, 1795701600000)`
(2026-03-14 22:00 UTC → 2026-11-26 14:00 UTC exclusive, last
bar 13:00 UTC): 6,160 bars BTC/ETH, 6,158 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=210 bars.

## Results (shipped config: SMA(200) trend filter, RSI(2)
below 25 / above 75 for two consecutive bars; exit on
RSI(2) above 70 / below 30 or 10-bar time exit; 2xATR stop,
3xATR trail)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 329 | 61.1% | -$1,930 | -19.3% | -1.81 | -23.3% | -$5.87 | 0.77 |
| ETH | 315 | 55.6% | -$2,412 | -24.1% | -2.49 | -25.8% | -$7.66 | 0.70 |
| HYPE | 330 | 57.3% | -$3,013 | -30.1% | -3.46 | -30.4% | -$9.13 | 0.61 |
| **Combined** | **974** | **58.0%** | **-$7,355** | — | **-3.55** | **-24.8%** | **-$7.55** | **0.69** |

Fees: BTC $3,574, ETH $2,497, HYPE $1,391 (total $7,461).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

## Verdict: a high win rate that still loses — the classic mean-reversion trap on 1h bars

Combined -$7,355 on 974 trades (PF 0.69, Sharpe -3.55)
despite a 58.0% win rate — the wins are small and the
losses are not. That is the TPS failure mode on 1h crypto:
RSI(2) below 25 catches pullbacks that keep falling, and
the 10-bar time exit plus the 2xATR stop cut the trade
before the snap-back the book's daily system waits for.
Signal exits dominate (251 / 238 / 243 vs 64 / 60 / 74
stops and 14 / 17 / 13 max-holds): most trades end on the
RSI(2) 70/30 exit, i.e. the system exits into strength and
still books a loss — the pullback entry is simply too early
on this timeframe. HYPE is the worst coin (-$3,013, PF
0.61, Sharpe -3.46) and BTC the least-bad (-$1,930, PF
0.77). Honest read: a 58% win rate with PF 0.69 is a system
that is right often and paid little — do not trade this on
1h bars. The scaling adaptation (daily → 1h) is the prime
suspect, and it is documented, not hidden.

## Mechanism

Trend: close vs SMA(200) (~8.3 days on 1h bars — the book's
daily 200-bar filter, scaled, stated as an adaptation).
Setup: RSI(2) below 25 for two consecutive bars goes long
on the close of the second bar (mirror above 75 for
shorts). Exit: RSI(2) closes above 70 (long) / below 30
(short), or the 10-bar time exit (the book's day-11 exit,
scaled) enforced by the harness max_hold_bars=10. The
original system has no stop; the house 2xATR stop / 3xATR
trail is added as a deviation required by house risk rules.
base.rsi 0-fills on flat stretches — the two-consecutive-bar
rule plus the SMA(200) filter guard the entry, and WARMUP =
210 covers the spin-up.

Source: Larry Connors & Cesar Alvarez — "Short Term Trading
Strategies That Work" (2008) —
https://tradingstrategyguides.com/tps-trading-strategy/

## Limitations

- Single ~8.4-month crypto window; the verdict is negative
  on all three coins, so no single-coin read generalises
  upward.
- The daily → 1h scaling is an untested adaptation: the
  book's edge, if any, lives on daily bars, and nothing here
  says it survives the scaling.
- 974 trades on $7,461 of fees: the most fee-heavy of this
  batch's three strategies relative to its loss.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped entry thresholds on this window.
