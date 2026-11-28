# Follow-Through Day (O'Neil) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 2026-11-27 13:00 UTC): 6,185 bars BTC/ETH, 6,183 HYPE.
Funding not modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=528 bars.

## Results (shipped config: correction >= 8% below 20-day
high; new 20-day low; first up-close day starts the attempt;
FTD on attempt-day 4-7 with day return >= 1.5% on rising
volume; exit on a later day's close below attempt_low;
2xATR stop, 3xATR trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 0 | — | $0.00 | 0.0% | 0.00 | 0.0% | — | 0.00 | $0.00 |
| ETH | 2 | 0.0% | -$165.92 | -1.7% | -1.44 | -2.2% | -$82.96 | 0.00 | $14.23 |
| HYPE | 5 | 20.0% | +$325.00 | +3.3% | 1.04 | -2.9% | +$65.00 | 2.67 | $20.86 |
| **Combined** | **7** | **14.3%** | **+$159.09** | **+0.5%** | **0.47** | **-1.5%** | **+$22.73** | **1.44** | **$35.09** |

Exit-reason breakdown: BTC none; ETH stop 2; HYPE stop 5.
The strategy-defined exit (later day's close below
attempt_low) fired ZERO times; the max hold fired zero
times. Every closed trade died on the 2xATR stop (one of
them, HYPE +$519.86, after running up first -- the trailing
stop banked it). Net % is the final-equity return ($30k
combined -> $30,159.09); Net $ is the sum of closed-trade
PnL.

## Verdict: seven trades is not a backtest, it is an anecdote

Combined +$159.09 on 7 trades, with BTC never firing once
in 8.5 months, is statistically meaningless -- the sign of
the total is decided by a single HYPE trade (+$519.86).
The honest read is that the FTD, as specified, is nearly
absent on 1h crypto in this window: 59 BTC / 95 ETH /
119 HYPE correction days and 30 / 27 / 32 new-low days
produced only 0 / 2 / 5 follow-through days. The 1.5%
daily-gain bar on rising volume inside a 4-day window,
after an 8% correction, is a rare event in a market that
falls in grinding steps rather than O'Neil-style
correction-then-rally cycles. Nothing here supports or
refutes the signal -- there is no sample. Do not trade
this on the strength of +$159, and do not reject O'Neil on
the strength of 7 trades either. The calibration sweep
(CALIBRATION.md) agrees: every variant lands within a few
hundred dollars of zero on 6-10 trades.

## Mechanism

State machine in indicators.py: UTC days are aggregated
(d_close/d_low/d_vol); a new 20-day-low day during a >=8%
correction arms an awaiting low; the first up-close day
after it starts the attempt (attempt_low = that low day's
low); the attempt fails on a later day's low undercutting
attempt_low or expires after day 7; on attempt-days 4-7 a
day gaining >=1.5% on rising volume sets ftd_day on its
23:00 bar. signals.py enters long on crossed_above of the
ftd_day flag and exits on a later day's 23:00 close below
the held attempt_low. The house 2xATR stop / 3xATR trail
sit behind the signal exit, with a 240-bar max hold.

Sources: William O'Neil, "How to Make Money in Stocks" --
https://traderlion.com/trading-strategies/follow-through-day/

## Limitations

- 7 trades: no statistical content whatsoever. Any
  parameter change moves the total by more than the total.
- The signal exit never fired -- untested in live conditions
  on this window; all exits were stops.
- BTC produced zero signals: the strategy is effectively
  untested on the largest coin.
- Single ~8.5-month crypto window, all three coins in the
  same regime for much of it; funding unmodeled;
  next-bar-open execution vs idealized entry.
- First cache day (2026-03-14) is a 2-bar partial day;
  inside warmup, no trade impact.
- Never tune the shipped gain threshold or attempt window
  on this window.
