# Ehlers RSI — Backtest

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
| BTC | 206 | 40.8% | -1746.23 | -1.39 | -26.3% | -8.48 | 0.81 |
| ETH | 194 | 42.3% | -1137.90 | -0.86 | -25.5% | -5.87 | 0.87 |
| HYPE | 213 | 43.2% | 100.65 | 0.18 | -15.4% | 0.47 | 1.01 |
| **Combined** | **613** | **42.1%** | **-2783.49** | **-0.97** | **-19.9%** | **-4.54** | **0.90** |

Fees: total $4720.23.
Exits: BTC {'stop': 135, 'signal': 71}; ETH {'stop': 127, 'signal': 67}; HYPE {'stop': 136, 'signal': 77}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,216.51.

## Verdict: LOSER — −$2,783.49 combined on 613 trades, do not trade as shipped.

The best win rate of the batch (42.1% combined) still loses money:
smoothing the RSI with a SuperSmoother(10) does not fix the classic
mean-reversion problem on 1h crypto — oversold bounces keep falling
and overbought fades keep rising, so the 30/70 entries catch falling
knives and fading strength in a market that trends in bursts. BTC
(−$1,746, Sharpe −1.39) and ETH (−$1,138) both lose; HYPE is
essentially flat (+$101, PF 1.01). Stops dominate exits (398 of 613),
so most trades are closed by the risk layer, not by the RSI reaching
the opposite extreme — the oscillator's round trip is slower than the
stop. Fees of $4,720 exceed the net loss, so the gross edge is also
negative. No coin shows a tradeable edge as shipped.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 613 trades make the negative result statistically meaningful. No
  parameter in the shipped config was tuned.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
