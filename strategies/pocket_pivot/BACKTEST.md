# Pocket Pivot — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794315600000) (2026-03-14 22:00 UTC →
2026-11-10 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 240 bars.

**Bar counts used:** BTC 5775, ETH 5775, HYPE 5773.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 0 | n/a | 0.00 | 0.00 | 0.0% | 0.00 | 0.00 |
| ETH | 4 | 50.0% | 324.45 | 0.76 | -1.1% | 81.11 | 2.50 |
| HYPE | 1 | 0.0% | -61.21 | -0.99 | -1.0% | -61.21 | 0.00 |
| **Combined** | **5** | **40.0%** | **263.24** | **0.60** | **-0.7%** | **52.65** | **1.95** |

Fees: total $35.89.
Exits: BTC {}; ETH {'stop': 4}; HYPE {'stop': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,263.24.

## Verdict: Inconclusive — nominally +$263.24 on 5 trades, not a tradeable signal as shipped.

The pocket pivot almost never fires on 1h crypto: 5 entries in ~8 months
across three coins, and BTC produced zero trades — its single entry
signal fired before the 1250-bar warmup and was never repeated. The
binding constraint is the volume test (only 42–58 bars per coin pass it
in ~4,500 post-warmup bars): an up bar must out-volume the largest
down bar of the previous 240 bars, and 1h crypto down bars spike volume
hard. All 5 trades exited on the ATR stop — not one reached the
close-below-EMA(240) signal exit — so the sample says nothing about the
exit rule either. ETH's +$324.45 (2W–2L) and HYPE's single −$61.21 loss
are noise at this sample size; a 40% win rate over 5 trades with PF 1.95
is not evidence of edge. As specified, the setup is a rare-event
screener on this timeframe, not a system.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 5-trade sample: no statistical meaning; BTC contributed nothing.
- The volume test as specified (max down-bar volume over 240 bars) is
  far stricter on 1h bars than on daily bars, where down-day volume
  spikes are rarer relative to the window; the day-scale rule does not
  transfer cleanly to hourly bars.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
