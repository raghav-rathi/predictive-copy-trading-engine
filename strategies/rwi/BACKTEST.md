# Random Walk Index — Backtest

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
| BTC | 565 | 32.4% | -5847.97 | -4.31 | -60.7% | -10.35 | 0.63 |
| ETH | 584 | 35.3% | -2014.90 | -0.86 | -33.2% | -3.45 | 0.89 |
| HYPE | 492 | 36.8% | 1475.02 | 0.90 | -16.1% | 3.00 | 1.08 |
| **Combined** | **1641** | **34.7%** | **-6387.86** | **-1.43** | **-27.0%** | **-3.89** | **0.88** |

Fees: total $11481.44.
Exits: BTC {'signal': 284, 'stop': 281}; ETH {'signal': 311, 'stop': 273}; HYPE {'stop': 252, 'signal': 240}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$23,870.45.

## Verdict: LOSER — −$6,387.86 combined on 1,641 trades, do not trade as shipped.

The RWI fires constantly on 1h crypto (1,641 entries in ~8 months) —
the exact opposite of its daily-bar behaviour, where a 14-bar range
beyond the random-walk yardstick is a rare event. On hourly bars the
14-bar range routinely exceeds one bar's ATR, so the 1.0 level is not
a filter at all; the system churns in and out, paying $11,481 in fees
alone. Win rates of 32–37% with profit factors of 0.63–0.89 say the
entries have no edge at this timeframe: BTC is catastrophic (−$5,848,
Sharpe −4.31, −60.7% drawdown), ETH is a steady loser, and HYPE's
+$1,475 (PF 1.08, 36.8% win rate) is the only green coin and not
enough to offset the other two. The signal exits fire about half the
time, so the exit rule is at least exercised — it just exits losing
trades as often as winning ones. The RWI-1.0 threshold does not
transfer from daily to hourly bars without re-scaling.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- Very high trade count means the result is statistically meaningful
  — and it is negative. No parameter in the shipped config was tuned.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
