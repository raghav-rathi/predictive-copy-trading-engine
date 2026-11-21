# Stochastic RSI Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 515 | 25.2% | -5845.96 | -7.55 | -59.1% | -11.35 | 0.42 |
| ETH | 493 | 28.0% | -3729.79 | -3.86 | -38.1% | -7.57 | 0.61 |
| HYPE | 485 | 23.5% | -5288.19 | -7.43 | -54.1% | -10.90 | 0.42 |
| **Combined** | **1493** | **25.6%** | **-14863.94** | **-8.51** | **-50.2%** | **-9.96** | **0.48** |

Fees: total $8664.52.
Exits: BTC {'signal': 438, 'stop': 77}; ETH {'signal': 433, 'stop': 60}; HYPE {'signal': 425, 'stop': 60}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$15,136.06.

## Verdict: LOSER (worst of the batch) — −$14,863.94 on 1,493 trades, combined Sharpe −8.51, MaxDD −50.2%.

StochRSI whipsaws relentlessly on 1h crypto: 1,493 trades, a 25.6%
win rate, PF 0.48. The %K/%D cross in the < 20 / > 80 zones fires
on nearly every RSI oscillation, and the opposite-cross exit
closes positions almost immediately (1,296 of 1,493 exits are
signal exits) — the strategy churns itself to death on fees
($8,664.52) before any move can develop. Every coin loses heavily
and the combined drawdown is −50.2%. No parameter was tuned; the
spec shipped as written, and both calibration alternates also lose
heavily (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,493 trades is a large sample and all three coins agree in sign
  and magnitude — the loss is systematic, not noise.
- StochRSI is an oscillator of an oscillator; on 1h bars its
  0–100 swings are mostly noise, and the cross logic has no trend
  filter to keep it out of chop.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
