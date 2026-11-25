# Percentage Price Oscillator — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-46 window ms `[1773525600000, 1795615200000)`
(2026-03-14 22:00 UTC → 2026-11-25 14:00 UTC exclusive, last
bar 13:00 UTC): 6,136 bars BTC/ETH, 6,134 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=40 bars.

## Results (shipped config: PPO(12,26,9), long on a signal-line
cross up while PPO > 0, short on a cross down while PPO < 0,
exit on the opposite cross, 2xATR stop, 3xATR trail, 60-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 167 | 31.7% | -$1,137 | -10.4% | -0.73 | -20.3% | -$6.81 | 0.83 |
| ETH | 167 | 28.1% | -$863 | -7.9% | -0.46 | -23.2% | -$5.17 | 0.87 |
| HYPE | 163 | 27.6% | -$1,545 | -15.4% | -1.49 | -21.4% | -$9.48 | 0.74 |
| **Combined** | **497** | **29.2%** | **-$3,545** | **-11.3%** | **-1.16** | **-19.1%** | **-$7.13** | **0.82** |

Fees: BTC $1,669, ETH $1,296, HYPE $714 (total $3,678).
Exits: BTC signal 97 / stop 70; ETH signal 78 / stop 89;
HYPE signal 115 / stop 48. Net % is the final-equity return
(it includes the mark-to-market of any position still open at
the window end); Net $ is the sum of closed-trade PnL.

## Verdict: a loser on all three coins — the signal-line cross
is too slow for 1h crypto chop

Combined -$3,545 on 497 trades. The PPO cross is a lagging
momentum trigger: by the time PPO crosses its 9-period signal
line, the 1h move that caused the cross is mostly spent, and
the PPO > 0 / PPO < 0 filter keeps the system out of the
sharpest reversals (where the money would be) while letting
it in late to trend legs that then stall. Win rate 27.6–31.7%,
profit factor 0.74–0.87 on every coin; HYPE is the worst
(-15.4%, Sharpe -1.49) despite the fewest fees, so this is
not a fee story — the entries themselves lose. The 2xATR
stops fire on 40%+ of exits on BTC and ETH, i.e. the system
buys the top of a wiggle and gets stopped out of it. There
is no coin, no sub-period, no reading in which the shipped
config works on this window.

## Calibration note

Shipped the specified signal period 9. A 5/9/14 signal-period
sweep on this batch-46 window is in CALIBRATION.md: 14 is the
least bad combined (-$1,887, 403 trades) and even prints a
+$113 ETH read — but that is an in-sample observation on a
knob that only changes how late the cross fires, and every
value is still a combined loser. The 9 config was fixed
before any backtest was run; no in-sample adoption — the
shipped config stays 9 and the verdict stays: loser.

## Mechanism

StockCharts ChartSchool, "Percentage Price Oscillator"
(Gerald Appel lineage via MACD): PPO = 100 × (EMA(12) −
EMA(26)) / EMA(26); signal = EMA(PPO, 9); histogram = PPO −
signal. Long = PPO crosses above its signal line while PPO >
0; short = PPO crosses below its signal line while PPO < 0;
exit on the opposite cross. The harness 2xATR hard stop /
3xATR chandelier trail sit behind the PPO cross as a safety
net for gap-through moves; 60-bar max hold.

Source: StockCharts ChartSchool, "Percentage Price Oscillator" —
https://chartschool.stockcharts.com/~gitbook/pdf?page=9QwAOEXf9dmW4Fkyz4Yb&only=yes&limit=100
(verified via search 2026-11-25; confirms the 12/26/9
standard, the signal line as a 9-day EMA of PPO, and the
histogram as PPO minus signal).

## Limitations

- Single ~8.4-month crypto window; 497 trades — the failure
  is consistent across all three coins, not a sample-size
  artefact.
- The PPO > 0 / < 0 filter plus a 9-period signal EMA makes
  entries late by construction on 1h bars; the calibration
  sweep shows a longer signal period helps a little
  in-sample (14 → -$1,887 combined) but does not fix the
  sign — adopting it would be in-sample selection.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped signal period on this window.
