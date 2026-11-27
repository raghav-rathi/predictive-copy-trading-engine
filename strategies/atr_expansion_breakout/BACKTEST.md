# ATR Expansion Breakout (NR7) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE. Funding not
modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=30 bars.

## Results (shipped config: NR7 = narrowest range of the last
7 bars; bracket = NR7 high/low, valid 3 bars; entry on a close
crossing the bracket; exit on a close back through the arming
level or the opposite entry; 2xATR stop, 3xATR trail, 48-bar
max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 582 | 24.9% | -$6,588.78 | -65.9% | -4.95 | -68.4% | -$11.32 | 0.59 | $4,003.60 |
| ETH | 565 | 27.3% | -$5,768.93 | -57.7% | -3.99 | -58.8% | -$10.21 | 0.64 | $3,129.61 |
| HYPE | 587 | 31.0% | -$5,001.29 | -49.1% | -3.32 | -51.8% | -$8.52 | 0.72 | $2,038.85 |
| **Combined** | **1,734** | **27.7%** | **-$17,359.00** | **-57.6%** | **-5.85** | **-58.6%** | **-$10.01** | **0.65** | **$9,172.06** |

Exit-reason breakdown: BTC signal 363 / stop 216 / max_hold 3;
ETH signal 342 / stop 219 / max_hold 4; HYPE signal 390 /
stop 197 / max_hold 0. Net % is the final-equity return
($30k combined -> $12,729.82); Net $ is the sum of
closed-trade PnL.

## Verdict: the NR7 bracket churns itself to death on 1h crypto

Combined -$17,359 on 1,734 trades (win rate 27.7%, PF 0.65)
is a decisive loser, and it is not a fee story: gross PnL
before the $9,172 of fees is still about -$8,187. The
mechanics fire constantly -- ~1,050 NR7 bars and ~3,080
armed-bracket bars per coin, ~860 entry signals per coin --
because on 1h bars the narrowest range of 7 is a routine
event, not a rare contraction. Most trades die on the
signal exit (1,095 of 1,734): the close breaks out of the
NR7 bracket and then falls straight back through the arming
level, i.e. the "expansion" is usually a 1-bar poke, not a
trend. The 2xATR stop takes another 632. No coin, no
validity setting (see CALIBRATION.md), no NR window rescues
it: every swept variant loses $15.7k-$18.7k combined. Honest
read: the NR7 bracket as specified is a churn machine on
1h crypto -- the setup needs a trend or volume filter it
does not have, and adding one would be a different strategy.

## Mechanism

State machine in indicators.py: a bar whose range is
strictly less than each of the previous six ranges is an
NR7; its high/low arm a bracket live through the next 3
bars (a newer NR7 re-arms). signals.py enters on a close
crossing above the armed high (long) or below the armed low
(short), enters neither if both would fire on one bar, and
exits a long on a close below the NR7 low that armed the
trade (mirror for shorts) or on the opposite entry. The
house 2xATR stop / 3xATR trail sit behind the signal exit,
with a 48-bar max hold.

Sources: Toby Crabel NR4/NR7 --
https://tradingstrategyguides.com/narrow-range-bars-the-nr4-and-nr7-strategy/
and https://www.loomiai.io/learn/nr7-inside-day-toby-crabel-strategy/

## Limitations

- 1,734 trades is plenty of sample: the loss is not a
  small-sample artefact, it is the strategy.
- The 48-bar max hold almost never binds (7 trades) -- the
  signal exit and the stop do the exiting.
- Single ~8.4-month crypto window, all three coins in the
  same down-drifting regime for much of it; funding
  unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped NR window or bracket validity on
  this window.
