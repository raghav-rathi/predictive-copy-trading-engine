# New York Open Momentum — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 48 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 216 | 35.2% | -2949.30 | -3.07 | -33.5% | -13.65 | 0.55 |
| ETH | 198 | 40.4% | -477.14 | -0.29 | -16.7% | -2.41 | 0.92 |
| HYPE | 214 | 47.2% | 572.78 | 0.56 | -12.6% | 2.68 | 1.08 |
| **Combined** | **628** | **40.9%** | **-2853.66** | **-0.99** | **-14.6%** | **-4.54** | **0.86** |

Fees: total $4,638.11.
Exits: BTC {'signal': 142, 'stop': 74}; ETH {'signal': 121, 'stop': 77}; HYPE {'signal': 144, 'stop': 70}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,146.34.

## Verdict: LOSER — -$2,853.66 on 628 trades, combined Sharpe -0.99, MaxDD -14.6%.

The strategy trades almost every day (628 trades) and loses on two
of three coins. BTC is the worst (-$2,949.30, Sharpe -3.07, MaxDD
-33.5%): the first-hour break keeps fading into the 21:00 time exit
(142 of 216 BTC exits are signal/time exits, not stops). HYPE is
nominally green (+$572.78, PF 1.08, expectancy +$2.68) but that is
214 trades of noise around breakeven, not an edge. Fees ($4,638.11
across the three books) exceed the combined loss — gross of fees the
strategy is roughly breakeven, so the first-hour-break rule itself
carries no edge on this window; the fee drag turns it into a loser.
No parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry (the 21:00 time exit fills at the
  22:00 open).
- The 13:00 UTC open is a clock rule imposed on a 24/7 market (see
  CALIBRATION.md); the break window and time exit are interpretation
  choices.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
