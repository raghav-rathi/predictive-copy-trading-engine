# Ergodic Oscillator — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 501 | 30.1% | -4791.47 | -3.11 | -53.3% | -9.56 | 0.70 |
| ETH | 493 | 30.2% | -3218.39 | -1.70 | -45.9% | -6.53 | 0.80 |
| HYPE | 473 | 32.1% | 502.35 | 0.43 | -20.0% | 1.06 | 1.03 |
| **Combined** | **1467** | **30.8%** | **-7507.50** | **-1.74** | **-31.1%** | **-5.12** | **0.86** |

Fees: total $9663.55.
Exits: BTC {'stop': 262, 'signal': 239}; ETH {'stop': 282, 'signal': 211}; HYPE {'stop': 253, 'signal': 220}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$22,685.91.

## Verdict: LOSER — -$7,507.50 on 1,467 trades, combined Sharpe -1.74, MaxDD -31.1%.

The closest to breakeven of the three batch-34 strategies, but still
a loser. HYPE is the only profitable coin (+$502.35, PF 1.03,
Sharpe 0.43) while BTC (-$4,791.47, PF 0.70) and ETH (-$3,218.39,
PF 0.80) both lose. Combined PF 0.86 and expectancy -$5.12 per
trade say the signal-line cross on 1h crypto is slightly worse than
a coin flip after costs: the double smoothing that makes the ergodic
clean also makes it late, so crosses fire after the move has already
run and the 2xATR stop takes the reversal. The exit split is nearly
even (797 stop / 670 signal), so neither the cross nor the stop is
rescuing the trade — the entry itself has no edge here. $9,663.55 of
fees on 1,467 trades is the other drag: the cross fires often enough
that costs eat the thin HYPE profit several times over.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,467-trade sample: the combined loss is modest in dollars but
  consistent in direction — two of three coins lose with PF below
  0.80, and the one winner is barely above 1.00.
- The HYPE profit (+$502.35) is small enough to be noise; do not
  read it as a HYPE-only edge.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
