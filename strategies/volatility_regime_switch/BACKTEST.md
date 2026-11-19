# Volatility Regime Switch — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 262 | 38.2% | -2744.96 | -1.93 | -31.6% | -10.48 | 0.72 |
| ETH | 252 | 38.5% | -2289.88 | -1.26 | -29.1% | -9.09 | 0.79 |
| HYPE | 271 | 41.3% | -1508.94 | -0.96 | -21.0% | -5.57 | 0.86 |
| **Combined** | **785** | **39.4%** | **-6543.79** | **-1.92** | **-25.1%** | **-8.34** | **0.80** |

Fees: total $5630.96.
Exits: BTC {'stop': 166, 'signal': 96}; ETH {'stop': 176, 'signal': 76}; HYPE {'stop': 166, 'signal': 105}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23,456.21.

## Verdict: LOSER — -$6,543.79 on 785 trades, combined Sharpe -1.92, MaxDD -25.1%, PF 0.80.

The strategy loses on all three coins with the same shape:
win rate ~38–41%, expectancy -$5.57 to -$10.48 per trade.
The dominant cost is churn: 785 trades generate $5,630.96
of fees, 86% of the total loss — the level-based entries
(breakout on every close beyond the channel, fade on every
close beyond the band) re-enter constantly in trending or
ranging tape, and the 2xATR stop / 2.5xATR trail cuts most
trades before the signal exits can pay. Gross of fees the
strategy still loses, so fees amplify a negative edge rather
than create it. Regime shares are balanced (expansion ~40%,
compression ~40%, middle ~20% of bars), and entries split
roughly evenly between breakout and fade legs, so neither leg
carries the result — both lose. No parameter was tuned; the
spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 785 trades is a large sample for the sign of the result but a
  single regime window (Mar–Nov 2026 crypto bear leg); the
  verdict is "loses here", not "never works".
- Never tune the shipped parameters on this window.

Paper only, no live execution.
