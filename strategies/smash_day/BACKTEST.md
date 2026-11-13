# Smash Day — Backtest

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
| BTC | 15 | 20.0% | -583.10 | -1.62 | -6.9% | -38.87 | 0.14 |
| ETH | 18 | 33.3% | -281.27 | -0.70 | -5.7% | -15.63 | 0.67 |
| HYPE | 6 | 33.3% | -88.78 | -0.31 | -2.9% | -14.80 | 0.72 |
| **Combined** | **39** | **28.2%** | **-953.15** | **-1.48** | **-3.6%** | **-24.44** | **0.49** |

Fees: total $327.34.
Exits: BTC {'stop': 15}; ETH {'stop': 18}; HYPE {'stop': 6}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,046.85.

## Verdict: LOSER — -$953.15 on 39 trades, combined Sharpe -1.48, MaxDD -3.6%.

The Smash Day does not survive the transfer to 1h crypto: only 39
setups fire in eight months (the wide-then-inside sequence is rare on
hourly-aggregated days), and all 39 trades end on the harness stop —
not one reaches the opposite-break exit or a profitable trail. The
inside-day break on 1h bars is a 1-bar event that reverses into the
2xATR stop; BTC's 0.14 profit factor is the worst single-coin print in
the batch so far. The small sample (39 trades) means this is a weak
rejection rather than a definitive one, but nothing in the numbers
suggests the edge is hiding in a nearby parameterisation — the entries
themselves lose before fees (-$625.81 gross).
