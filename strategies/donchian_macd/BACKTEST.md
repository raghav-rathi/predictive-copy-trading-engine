# Donchian MACD — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 243 | 29.6% | -2319.75 | -1.56 | -28.8% | -9.55 | 0.77 |
| ETH | 217 | 35.0% | -401.77 | -0.14 | -18.2% | -1.85 | 0.96 |
| HYPE | 251 | 36.3% | -115.39 | 0.04 | -17.1% | -0.46 | 0.99 |
| **Combined** | **711** | **33.6%** | **-2836.91** | **-0.75** | **-13.7%** | **-3.99** | **0.91** |

Fees: total $5325.12.
Exits: BTC {'stop': 158, 'signal': 85}; ETH {'stop': 159, 'signal': 58}; HYPE {'stop': 152, 'signal': 99}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,163.09.

## Verdict: LOSER — -$2,836.91 on 711 trades, combined Sharpe -0.75, MaxDD -13.7%.

Donchian breakouts confirmed by MACD lose on 1h crypto: 711
trades, a 33.6% win rate, PF 0.91, and -$2,836.91 net after
$5,325.12 in fees. No coin wins — BTC is the worst (-$2,319.75,
Sharpe -1.56, MaxDD -28.8%), ETH loses (-$401.77, PF 0.96) and
HYPE is near breakeven (-$115.39, PF 0.99). The exit split (469
stop vs 242 signal) shows the histogram-flip / opposite-break
exit fires often but does not save the trades: 20-bar breakouts
on 1h bars are mostly false breakouts that reverse into the
2xATR stop, and MACD histogram agreement does not filter them.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 711 trades is a large sample and the loss is present on all
  three coins — the edge is absent, not merely unlucky.
- The Donchian channel uses the previous 20 bars (see
  CALIBRATION.md); the literal "(incl. current bar)" reading
  would trade zero times.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
