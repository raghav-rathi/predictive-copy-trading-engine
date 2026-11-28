# Popgun Bar Pattern — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 13:00 UTC): 6,185 bars BTC/ETH, 6,183 HYPE. Funding not
modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=10 bars.

## Results (shipped config: inside bar followed by an
engulfing outside bar arms a high/low bracket, valid 5
bars; entry on a close crossing the bracket; exit on a
close back through the arming level or the opposite entry;
2xATR stop, 3xATR trail, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 147 | 32.0% | -$1,156.73 | -10.9% | -0.67 | -23.7% | -$7.87 | 0.83 | $1,469.30 |
| ETH | 133 | 33.1% | -$1,080.46 | -9.9% | -0.70 | -29.6% | -$8.12 | 0.83 | $1,040.29 |
| HYPE | 145 | 29.7% | -$1,220.17 | -12.2% | -0.79 | -17.8% | -$8.41 | 0.83 | $674.99 |
| **Combined** | **425** | **31.5%** | **-$3,457.36** | **-11.5%** | **-1.17** | **-19.6%** | **-$8.13** | **0.83** | **$3,184.58** |

Exit-reason breakdown: BTC stop 107 / signal 28 / max_hold 12;
ETH stop 91 / signal 35 / max_hold 7; HYPE stop 104 /
signal 34 / max_hold 7. Net % is the final-equity return
($30k combined -> $26,700.66); Net $ is the sum of
closed-trade PnL.

## Verdict: a loser -- and the uniformity is the tell

Combined -$3,457 on 425 trades (win rate 31.5%, PF 0.83)
is a clear loser, and the most damning number in the table
is not the total but the sameness: profit factor 0.83 on
BTC, 0.83 on ETH, 0.83 on HYPE; expectancy -$7.87 / -$8.12 /
-$8.41. Three different coins, same failure to three
significant figures -- the popgun bracket has no edge on
any of them, in either direction. Gross PnL before the
$3,185 of fees is only about -$273: like the AO Saucer,
the pattern is essentially breakeven gross and the
0.055%-per-side round trip turns zero edge into a steady
bleed. That is still a rejection: 425 trades, gross
expectancy -$0.64/trade, no coin above PF 0.83. The exit
mix explains the mechanism: 302 of 425 trades (71%) die
on the 2xATR hard stop, only 97 on the signal exit. The
outside bar's range is usually just the bar's own noise,
not a coiled spring -- the breakout pokes out and falls
straight back, and the stop takes the trade before the
failed-popgun exit can act. The 48-bar max hold binds on
26 trades, the only strategy in this batch where it does
anything at all. Honest read: on 1h crypto the
inside-then-outside sequence is a routine volatility
flicker, not a setup; the bracket needs a trend or volume
filter it does not have, and adding one would be a
different strategy.

## Mechanism

State machine in indicators.py: a bar whose high/low sit
strictly inside the previous bar's range, followed by a bar
whose high/low strictly engulf it, is a popgun; its
outside bar's high/low arm a bracket live through the next
5 bars (a newer popgun re-arms). signals.py enters on a
close crossing above the armed high (long) or below the
armed low (short), enters neither if both would fire on one
bar, and exits a long on a close below the popgun low that
armed the trade (mirror for shorts) or on the opposite
entry. Raw counts: 201 / 176 / 180 popguns per coin (BTC /
ETH / HYPE), ~1,135 / 978 / 1,025 armed-bracket bars, 578
entry signals total, of which the harness turns 425 into
trades. The house 2xATR stop / 3xATR trail sit behind the
signal exit, with a 48-bar max hold.

Sources: Popgun bar pattern — Jeffrey Kennedy / Elliott Wave
International --
https://elliottwaveuniversity.com/popgun-twobar-pattern-points-trade-setups/

## Limitations

- 425 trades is plenty of sample: the loss is not a
  small-sample artefact, though the gross-PnL near-zero
  means the verdict is "no edge" rather than "anti-edge".
- Single ~8.5-month crypto window, all three coins in the
  same down-drifting regime for much of it; funding
  unmodeled; next-bar-open execution vs idealized entry.
- The validity-8 sweep (see CALIBRATION.md) turns HYPE
  marginally positive (+$113) -- a one-coin, 174-trade
  wobble around zero, not an edge; do not chase it.
- Never tune the shipped bracket validity on this window.
