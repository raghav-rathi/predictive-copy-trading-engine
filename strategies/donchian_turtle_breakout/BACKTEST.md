# Donchian Turtle Breakout (System 1) — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), pinned window: 2026-03-14 22:00 UTC → 2026-11-22 14:00 UTC
(BTC 6,064 bars, ETH 6,064 bars, HYPE 6,062 bars — exactly the
expected counts).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 2xATR(20) stop, 3x
leverage cap, $10k start, long/short. WARMUP=60 bars.

## Results (shipped config: prior-20-bar Donchian breakout entry,
prior-10-bar Donchian exit, 2xATR(20) stop, 336-bar max hold;
no skip rule, no pyramiding)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 174 | 28.2% | -$1,889 | -19.1% | -0.89 | -34.3% | -$10.86 | 0.80 |
| ETH | 152 | 28.3% | +$1,006 | +9.7% | +0.58 | -20.7% | +$6.62 | 1.11 |
| HYPE | 184 | 32.1% | +$46 | +0.7% | +0.18 | -21.7% | +$0.25 | 1.00 |
| **Combined** | **510** | **29.6%** | **-$838** | — | — | — | **-$1.64** | — |

Fees: BTC $1,674, ETH $1,234, HYPE $959 (total $3,867).

Exit reasons: BTC 89 signal / 85 stop; ETH 84 signal / 68 stop;
HYPE 109 signal / 75 stop. No max-hold exits — the 10-bar
channel exit always fired first. Sides roughly balanced
(BTC 83 long / 91 short; ETH 73 / 79; HYPE 93 / 91).

## Verdict: loser — the 1h Turtle whipsaws itself to death

Combined -$838 across 510 trades with a 29.6% win rate and a
0.80 profit factor is a loser, plainly. The mechanism works as
designed (breakouts fire, the 10-bar exit and the 2xATR stop
both fire, unit-tested) — the edge does not survive the 1h
scaling:

- The Turtle profile is many small losses for a few big wins.
  Here the losses arrived on schedule (49% of exits are
  stops) but the big wins did not: BTC lost -$1,889 with a
  -34.3% max drawdown, and the ETH/HYPE gains (+$1,006 /
  +$46) are not enough to cover it.
- Fees alone ($3,867) are 4.6x the net loss — the system
  trades ~2x per coin per week, and at that frequency the
  0.055%/side round-trip cost is a real headwind. Even
  fee-free, the combined result would be roughly breakeven,
  not a winner.
- HYPE's +$46 on 184 trades (PF exactly 1.00) is the purest
  statement of the result: the system is a coin flip after
  costs on this window.

Stated plainly: do not trade System 1 on 1h crypto as built.
The daily original's edge — if it exists — lives in the
multi-week trend the 20-day channel captures; compressing it
to 20 hours turns it into a noise-breakout machine. The skip
rule's omission (documented in the README) likely made this
worse by trading breakouts into extended moves, but the
dominant problem is the timeframe, not the skip rule — no
parameter change is adopted here to fix it, and none should
be tuned on this window.

## Mechanism

LONG on close above the prior-20-bar Donchian high; SHORT on
close below the prior-20-bar low; exit LONG on close below the
prior-10-bar low, SHORT above the prior-10-bar high; 2xATR(20)
stop; no trail/target; 336-bar max hold. System 1 only, no
skip rule, no pyramiding. All params fixed a priori; no
optimization.

Source: Curtis Faith, *Way of the Turtle* (2007) — Turtle
trading, System 1 (https://en.wikipedia.org/wiki/Turtle_trading).

## Limitations

- Single 8-month crypto window, heavily down-trending in the
  second half; funding unmodeled; next-bar-open execution vs
  idealized entry.
- 510 trades is a large sample for the win rate but the
  per-coin split (BTC loser, ETH/HYPE flat-to-green) shows the
  result is regime-dependent, not a stable edge.
- Never tune the shipped parameters on this window — least of
  all the 20/10 channel lengths, which directly control how
  many trades fire.
