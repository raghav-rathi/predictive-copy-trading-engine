# AO Saucer (Bill Williams) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive, last
bar 13:00 UTC): 6,185 bars BTC/ETH, 6,183 HYPE. Funding not
modeled (fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=50 bars.

## Results (shipped config: AO = SMA(median,5) − SMA(median,34);
buy saucer = three AO bars above zero, middle falling, last
rising; sell saucer mirror; exit on AO zero-cross or the
opposite saucer; 2xATR stop, 3xATR trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 205 | 27.3% | -$2,702.80 | -26.6% | -1.81 | -36.0% | -$13.18 | 0.70 | $1,744.49 |
| ETH | 218 | 32.6% | -$905.61 | -9.1% | -0.42 | -22.2% | -$4.15 | 0.90 | $1,661.74 |
| HYPE | 190 | 31.6% | -$1,220.65 | -10.4% | -0.59 | -19.7% | -$6.42 | 0.87 | $875.54 |
| **Combined** | **613** | **30.5%** | **-$4,829.06** | **-15.3%** | **-1.27** | **-23.5%** | **-$7.88** | **0.83** | **$4,281.77** |

Exit-reason breakdown: BTC stop 154 / signal 51 / max_hold 0;
ETH stop 158 / signal 60 / max_hold 0; HYPE stop 156 /
signal 34 / max_hold 0. Net % is the final-equity return
($30k combined -> $25,397.45); Net $ is the sum of
closed-trade PnL.

## Verdict: a loser with no edge before costs, and fees do the rest

Combined -$4,829 on 613 trades (win rate 30.5%, PF 0.83)
is a clear loser, but milder than the batch-48 churners --
and the shape of the loss matters. Gross PnL before the
$4,282 of fees is only about -$547: the saucer is
essentially breakeven gross, and the 0.055%-per-side round
trip turns a zero-edge signal into a steady bleed. That is
still a rejection, not a near-miss: 613 trades is plenty of
sample, gross expectancy is -$0.89/trade, and no coin is
close to profitable (best is ETH at PF 0.90). The exit mix
explains the mechanism: 468 of 613 trades (76%) die on the
2xATR hard stop, only 145 on the signal exit. The saucer's
red-to-green AO turn does not persist on 1h crypto -- price
reverses into the stop before AO ever crosses zero, so the
Williams exit almost never gets to act. The 96-bar max hold
never binds (0 trades): the stop always gets there first.
Honest read: the saucer identifies real AO troughs, but on
1h bars the trough is noise more often than the start of a
momentum leg, and at 1% risk on a 2xATR stop the position
cannot survive the whipsaw long enough to find out.

## Mechanism

indicators.py computes median = (h+l)/2 and AO =
SMA(median,5) − SMA(median,34) plus ATR(14). signals.py
flags a buy saucer when the last three AO bars are above
zero with the middle bar below the first and the last bar
above the middle (mirror below zero for sells), exits a
long on crossed_below(ao, 0) or a sell saucer (mirror for
shorts), and never re-fires while AO keeps rising. Raw
signal counts: BTC 224 buy / 211 sell saucers, ETH 214 /
201, HYPE 187 / 190 -- roughly one saucer per 29 bars per
coin, of which the harness turns ~613 into trades. The
house 2xATR stop / 3xATR trail sit behind the signal exit,
with a 96-bar max hold.

Sources: Awesome Oscillator Saucer — Bill Williams,
*New Trading Dimensions* -- https://www.mql5.com/en/code/13

## Limitations

- 613 trades is plenty of sample: the loss is not a
  small-sample artefact, though the gross-PnL near-zero
  means the verdict is "no edge" rather than "anti-edge".
- Single ~8.5-month crypto window, all three coins in the
  same down-drifting regime for much of it; funding
  unmodeled; next-bar-open execution vs idealized entry.
- The 96-bar max hold never binds, so its exact value is
  untested by this run.
- Never tune the shipped AO lengths or exit rule on
  this window.
