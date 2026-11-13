# MACD Signal-Line Crossover — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 426 | 31.5% | -3930.87 | -2.44 | -49.5% | -9.23 | 0.74 |
| ETH | 424 | 31.8% | -2047.00 | -0.99 | -41.7% | -4.83 | 0.87 |
| HYPE | 430 | 34.2% | 2037.96 | 1.14 | -16.5% | 4.74 | 1.11 |
| **Combined** | **1280** | **32.5%** | **-3939.90** | **-0.81** | **-24.1%** | **-3.08** | **0.92** |

Fees: total $9099.22.
Exits: BTC {'stop': 258, 'signal': 168}; ETH {'stop': 272, 'signal': 152}; HYPE {'stop': 250, 'signal': 180}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,179.68 (closed-trade net -$3,939.90; the $119.58 gap is unrealised
MTM on positions still open at the window end).

## Verdict: LOSER — -$3,939.90 on 1,280 trades, combined Sharpe -0.81, MaxDD -24.1%.

Appel's classic crossover whipsaws badly on 1h crypto: 1,280 trades
(~430 per coin, roughly two a day) at a 32.5% win rate and PF 0.92,
with $9,099.22 of fees — the highest trade count and fee bill in the
batch series so far. The signal cross does fire as designed (500 of
1,280 exits on the opposite cross), but the 2xATR stop takes the other
780, and the cross entries flip direction far faster than the 1h trend
can pay for them. Only HYPE wins (+$2,037.96, Sharpe 1.14, PF 1.11);
BTC is the worst leg (-$3,930.87, Sharpe -2.44, MaxDD -49.5%) and ETH
loses too (-$2,047.00, PF 0.87). The combined MaxDD of -24.1% is the
deepest in this batch. The honest read: the raw MACD signal-line cross
with no trend filter is a churn machine on hourly crypto — it needs a
filter (or a slower timeframe) to be tradeable, and none was added
here because the spec is the spec.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,280-trade sample: a large sample, but one window — the loss is
  consistent across BTC and ETH, so it is not a one-coin artefact.
- The opposite-cross exit fires often (500/1,280), so the reported
  result really is the MACD crossover system, not just the harness
  stop/trail.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
