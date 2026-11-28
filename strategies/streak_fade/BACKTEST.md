# Consecutive Days Fade (Connors) — Backtest

**Data:** Hyperliquid 1h bars, BTC + ETH + HYPE, read from the
local cache only (`data/candles/{BTC,ETH,HYPE}_1h.csv`), pinned
batch-49 window ms `[1773525600000, 1795874400000)`
(2026-03-14 22:00 UTC → 2026-11-28 14:00 UTC exclusive;
cache ends 2026-11-27 14:00 UTC, last bar 13:00 UTC):
6,185 bars BTC/ETH, 6,183 HYPE. Funding not modeled
(fully offline run).
**Costs:** 0.045% taker fee + 0.01% slippage per side.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x
leverage cap, $10k start per coin. WARMUP=20 bars.

## Results (shipped config: fade the 4th consecutive up/down
close; exit on a close crossing SMA(10) or the opposite
entry; 2xATR stop, 3xATR trail, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor | Fees |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 309 | 58.9% | -$3,657.18 | -36.6% | -3.86 | -36.8% | -$11.84 | 0.62 | $2,864.40 |
| ETH | 318 | 56.9% | -$3,223.78 | -32.2% | -3.31 | -33.7% | -$10.14 | 0.67 | $2,169.64 |
| HYPE | 359 | 64.1% | -$517.56 | -5.2% | -0.39 | -12.6% | -$1.44 | 0.95 | $1,786.56 |
| **Combined** | **986** | **60.1%** | **-$7,398.52** | **-24.7%** | **-3.51** | **-25.4%** | **-$7.50** | **0.76** | **$6,820.60** |

Exit-reason breakdown: BTC signal 210 / stop 99 / max_hold 0;
ETH signal 220 / stop 98 / max_hold 0; HYPE signal 256 /
stop 103 / max_hold 0. Net % is the final-equity return
($30k combined -> $22,601.48); Net $ is the sum of
closed-trade PnL.

## Verdict: wins most trades, loses money anyway -- the fade is right about direction, wrong about size

Combined -$7,398.52 on 986 trades at a 60.1% win rate (PF
0.76) is a loser with an unusual shape: the fade usually
works -- the streak does stall and price does cross back
through SMA(10) -- but the wins are small and the losses
are large. The signal exit (686 of 986 trades) banks the
small reversion; the 2xATR stop (300 trades) takes the
full-sized loss whenever the streak extends into a run
instead of reverting, and on 1h crypto a 4-up streak is
often the start of a trend leg, not its end. HYPE is
closest to breakeven (-$517.56, PF 0.95) and BTC the worst
(-$3,657.18, PF 0.62). It is barely a fee story: gross PnL
before the $6,820.60 of fees is still -$577.92 -- the edge
is absent, not eaten by costs. The 24-bar max hold never
binds (0 trades): every trade resolves through the signal
exit or the stop first. Honest read: fading 4-day streaks
on hourly bars wins the coin flip and loses the payoff --
the Connors daily-stock effect does not survive the
transfer to 1h crypto, where streaks run further than the
2xATR stop allows.

## Mechanism

State machine in indicators.py: up_streak / down_streak
count consecutive closes vs the prior close (flat resets
both); sma10 is SMA(close, 10). signals.py enters short
when up_streak crosses above 3 and long when down_streak
crosses above 3 (exactly once per streak), enters neither
if both would fire on one bar (impossible in practice --
a close cannot be both up and down), and exits a long on
a close crossing above SMA(10) (mirror for shorts) or on
the opposite entry. The house 2xATR stop / 3xATR trail
sit behind the signal exit, with a 24-bar max hold.

Sources: Larry Connors, "Consecutive Up/Down Days" --
https://tradingmarkets.com/recent/if_a_stock_drops_5_days_in_a_row_should_you_buy_it-674228

## Limitations

- 986 trades is plenty of sample: the loss is not a
  small-sample artefact, it is the strategy (and the
  win-rate / payoff split is the story, not the headline).
- Single ~8.5-month crypto window, all three coins in the
  same regime for much of it; funding unmodeled;
  next-bar-open execution vs idealized entry.
- The daily-stock source result is being tested on hourly
  crypto bars; the transfer itself is the hypothesis under
  test, and it fails here.
- Never tune the shipped streak threshold or exit SMA on
  this window.
