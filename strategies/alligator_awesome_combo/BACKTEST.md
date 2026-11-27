# Alligator + Awesome Oscillator Combo — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-48 window ms `[1773525600000, 1795788000000)`
(2026-03-14 22:00 UTC → 2026-11-27 14:00 UTC exclusive, last
bar 13:00 UTC): 6,184 bars BTC/ETH, 6,182 HYPE (HYPE's first
bar is 2026-03-15 00:00 UTC). Funding not modeled (fully
offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=60 bars.

## Results (shipped config: Alligator SMMA 13/8/5 unshifted,
AO SMA(5)-SMA(34), 2-bar fractals; long on a close crossing
above a confirmed up-fractal high above the teeth with AO > 0
and rising and lips > teeth > jaw, short mirror; exit on a
close back inside the lips, 2 consecutive AO bars against
the trade, or the opposite entry; 2xATR stop, 3xATR trail,
120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 223 | 29.6% | -$3,081 | -30.8% | -2.72 | -33.6% | -$13.82 | 0.63 |
| ETH | 231 | 27.7% | -$2,708 | -27.1% | -2.15 | -27.2% | -$11.72 | 0.68 |
| HYPE | 224 | 32.6% | -$1,525 | -15.2% | -1.39 | -25.1% | -$6.81 | 0.80 |
| **Combined** | **678** | **29.9%** | **-$7,314** | **-24.4%** | **-3.01** | **-25.6%** | **-$10.79** | **0.70** |

Fees: BTC $2,176.82, ETH $1,610.13, HYPE $1,051.95 (total $4,838.90).
Net % is the final-equity return (it includes the
mark-to-market of any position still open at the window end);
Net $ is the sum of closed-trade PnL.

Exit breakdown: BTC signal 152 / stop 71; ETH signal 148 /
stop 83; HYPE signal 178 / stop 46; max-hold exits 0 on all
three coins.

## Verdict: a clean loser on every coin

Combined -$7,314 on 678 trades (29.9% win rate, PF 0.70,
Sharpe -3.01) -- the strategy fires plenty and loses
steadily on all three coins, worst on BTC (-30.8%) and
least-bad on HYPE (-15.2%, PF 0.80). It is not a fee story:
gross PnL before fees is about -$2,475, so the edge is
negative even at zero cost. The signal exits dominate
(478 of 678), so the lips/AO exit rules are doing what
they are told -- the entries are simply buying upside
fractal breakouts (and shorting downside ones) into a
window where those breakouts keep failing: the classic
fractal-breakout trap on 1h crypto, where a 5-bar local
extreme is usually a pullback high, not a trend launch.
The 120-bar max hold never binds (0 exits), so the hold
is not the problem either. Honest read: the Profitunity
entry as specified does not survive 1h crypto in this
window. Do not trade it; do not tune the fractal window
to rescue it (see CALIBRATION.md -- every setting loses).

## Mechanism

SMMA of the median price (Jaw 13 / Teeth 8 / Lips 5,
unshifted -- see the deviation note in README.md), AO =
SMA(median, 5) - SMA(median, 34), and 2-bar fractals
confirmed with a 2-bar lag. Entry is a close crossing a
confirmed fractal extreme (above the teeth for longs,
below for shorts) with AO on the trade's side and rising
(falling) and the Alligator mouth open in the trade's
direction. The cross is only counted while the fractal
level is unchanged from the previous bar, so a newly
confirmed fractal moving the forward-filled level cannot
fake a breakout. Exits are a close back inside the lips,
two consecutive AO bars against the trade, or the opposite
entry, behind the house 2xATR stop / 3xATR trail.

Source: Bill Williams Profitunity / Trading Chaos --
https://www.mql5.com/en/articles/16365

## Limitations

- Single ~8.4-month crypto window (Mar-Nov 2026, a
  strongly down-trending tape for much of it); funding
  unmodeled; next-bar-open execution vs idealized entry.
- Fractal breakouts are regime-sensitive: the same rules
  may behave differently in a sustained uptrend, but
  nothing in this window supports that hope.
- Never tune the shipped fractal window on this window.
