# SMI Ergodic Oscillator Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`, columns t,o,h,l,c,v; t in
ms), sliced to the batch window 2026-03-14 00:00 UTC →
2026-10-23 23:59 UTC (ms `[1773446400000, 1792713599000)`):
5,330 bars BTC, 5,330 ETH, 5,328 HYPE.
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not
modeled (fully offline run).
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x
leverage cap, $10k start, long/short symmetric. WARMUP=120 bars.

## Results (shipped config: Blau's SMI Ergodic 5/20, signal 5,
zones ±40; long on cross-above from ≤ −40, short on cross-below
from ≥ +40, exit on the opposite cross, 1.5xATR stop, 2xATR
chandelier trail, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 77 | 28.6% | -$1,786 | -17.9% | -2.14 | -21.0% | -$23.20 | 0.58 |
| ETH | 86 | 33.7% | -$278 | -2.8% | -0.20 | -16.8% | -$3.23 | 0.94 |
| HYPE | 82 | 23.2% | -$2,563 | -25.9% | -3.79 | -26.0% | -$31.26 | 0.41 |
| **Combined** | **245** | **28.6%** | **-$4,627** | — | — | — | -$18.89 | — |

Fees: BTC $953, ETH $851, HYPE $450.

Side breakdown (net $ / win%): BTC long -$1,544/21.6% vs short
-$242/35.0%; ETH long -$1,210/25.0% vs short +$932/41.3%; HYPE long
-$866/25.0% vs short -$1,697/21.4%. Zone occupancy is healthy
(207–376 bars per coin in the ±40 zones; 41–48 entries per side per
coin) — the strategy trades plenty; it just loses.

## Verdict: honest loser on all three coins

Combined -$4,627 over 245 trades, expectancy -$18.89/trade,
Sharpe negative on every leg. The mechanism fires as designed —
the zones are occupied, the hooks trigger 80+ entries per coin —
but the edge is absent:

- **The oversold hook is a falling-knife catch.** BTC longs win
  21.6% and lose -$1,544; HYPE longs and shorts both lose at
  ~21–25% win rates. On 1h crypto, an SMI hook out of -40 is far
  more often a brief dead-cat bounce inside a continuing leg than
  a momentum turn.
- **ETH shorts are the only green sub-leg** (+$932, 41.3% win),
  but they are swamped by ETH longs (-$1,210). One green
  sub-component out of six is noise, not a short-side edge —
  HYPE shorts are the worst sub-leg of the whole run (-$1,697).
- **The opposite-cross exit gives back the winners.** Profit
  factor 0.41–0.58 on BTC/HYPE means losses dominate by ~2:1;
  the 1.5xATR stop is doing most of the exiting on losers while
  the signal exit arrives too late on the rare winners.

Blau's 5/20/5/±40 was calibrated on daily equities; on 1h crypto
the oscillator whipsaws across the zones (a zone is occupied on
~6–7% of bars) and the hook-from-extreme pattern has no
predictive content here. Per the honest-loser standard, this ships
as a documented loser — see CALIBRATION.md for why the parameters
were nevertheless not re-tuned on this window.

## Mechanism

m = close.diff(); smi = 100 × EMA(EMA(m, 5), 20) /
EMA(EMA(|m|, 5), 20); signal = EMA(smi, 5). Long when smi crosses
above its signal with the prior-bar smi at/below −40; short on the
mirror from at/above +40; exit on the opposite cross. 1.5xATR stop,
2xATR chandelier trail, no fixed target, 96-bar max hold, symmetric
long/short.

Sources: https://en.wikipedia.org/wiki/True_strength_index —
https://www.gate.com/learn/articles/what-is-tsi-indicator
(SMI Ergodic follows Blau's book parameters; see README.md for the
honest sourcing note.)

## Limitations

- Single 7-month crypto window; 245 trades.
- The zone-gate occupancy differs by coin (HYPE spends the least
  time ≤ −40), but the verdict is the same on all three.
- Funding unmodeled; next-bar-open execution vs idealized entry.
- Never tune the shipped parameters on this window.
