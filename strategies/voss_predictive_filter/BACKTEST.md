# Voss Predictive Filter — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794402000000) (2026-03-14 22:00 UTC →
2026-11-11 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5776, ETH 5776, HYPE 5774.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 442 | 35.5% | -4158.25 | -3.39 | -43.3% | -9.41 | 0.70 |
| ETH | 423 | 37.6% | -1133.12 | -0.47 | -26.9% | -2.68 | 0.92 |
| HYPE | 457 | 39.6% | -1231.74 | -0.67 | -22.5% | -2.70 | 0.91 |
| **Combined** | **1322** | **37.6%** | **-6523.12** | **-1.92** | **-26.4%** | **-4.93** | **0.84** |

Fees: total $9785.42.
Exits: BTC {'signal': 278, 'stop': 164}; ETH {'signal': 257, 'stop': 166}; HYPE {'signal': 307, 'stop': 150}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23,566.77.

## Verdict: LOSER — −$6,523.12 combined on 1,322 trades, do not trade as shipped.

Every coin loses, with win rates of 35–40% and profit factors of
0.70–0.92. The Voss cross fires ~440 times per coin in ~8 months —
roughly twice a day — so the "predictive" phase advance is mostly
whipsaw on 1h crypto: the 20-bar cycle the filter is tuned to does not
persist on hourly bars, and the ADX < 25 gate does not save it (a
weak-trend filter is not a ranging-market filter when the cycle itself
keeps shifting). BTC is the worst (−$4,158, Sharpe −3.39, −43.3%
drawdown). Fees of $9,785 are ~1.5x the net loss, so even a
breakeven gross edge would have been fee-negative at this trade
frequency. The signal exits dominate (278–307 per coin vs 150–166
stops), so the cross exit works mechanically — the entries are simply
wrong more often than right.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- High trade count makes the negative result statistically meaningful.
  No parameter in the shipped config was tuned.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
