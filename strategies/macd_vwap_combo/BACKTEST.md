# MACD + Session VWAP — Backtest

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
| BTC | 352 | 30.4% | -3758.21 | -2.49 | -45.2% | -10.68 | 0.71 |
| ETH | 350 | 30.6% | -2726.73 | -1.55 | -43.5% | -7.79 | 0.80 |
| HYPE | 352 | 35.2% | 2830.00 | 1.52 | -14.3% | 8.04 | 1.19 |
| **Combined** | **1054** | **32.1%** | **-3654.95** | **-0.82** | **-23.4%** | **-3.47** | **0.91** |

Fees: total $7675.62.
Exits: BTC {'stop': 217, 'signal': 135}; ETH {'stop': 226, 'signal': 124}; HYPE {'stop': 197, 'signal': 155}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,494.40.

## Verdict: Loser — −$3,654.95 on 1,054 trades, the worst batch-33 drawdown profile.

MACD crosses on 1h crypto fire about 1.5 times a day per coin
(~350 trades each), and the session-VWAP filter does not save them:
BTC −$3,758 (Sharpe −2.49, MaxDD −45.2%) and ETH −$2,727 (MaxDD
−43.5%) both bleed steadily, with 30% win rates and ~62% of trades
exiting on the ATR stop. Fees alone are $7,676 — more than twice the
net loss — so even a neutral signal would lose money at this trade
frequency. HYPE's +$2,830 is the same single-coin trend artefact
seen across this batch (HYPE trended hard in-window) and does not
offset two coins losing ~$3k each. The combination as specified is a
whipsaw machine on hourly bars: the MACD cross is too fast for the
timeframe and the VWAP gate is too weak to filter it.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 1,054 trades at 0.045% fee + 0.01% slippage per side: fee drag
  dominates the result; any lower-fee assumption would change the
  numbers but not the negative signal.
- HYPE's in-window trend flatters the combined figure; per-coin
  results are the honest read.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
