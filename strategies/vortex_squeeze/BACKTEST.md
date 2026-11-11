# Vortex Squeeze — Backtest

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
| BTC | 267 | 28.1% | -3087.01 | -2.85 | -35.9% | -11.56 | 0.62 |
| ETH | 278 | 36.3% | 1704.80 | 1.23 | -10.1% | 6.13 | 1.20 |
| HYPE | 277 | 32.1% | 90.11 | 0.17 | -21.8% | 0.33 | 1.01 |
| **Combined** | **822** | **32.2%** | **-1292.09** | **-0.39** | **-12.0%** | **-1.57** | **0.95** |

Fees: total $7739.30.
Exits: BTC {'signal': 152, 'stop': 115}; ETH {'signal': 163, 'stop': 115}; HYPE {'signal': 145, 'stop': 132}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,707.91.

## Verdict: LOSER — -$1,292.09 on 822 trades, combined profit factor 0.95.

The squeeze gate does what it is supposed to do — it cuts the trade
count well below an ungated Vortex cross (822 vs the ~1,700-trade
pace of an unfiltered cross system) — but selectivity did not buy
edge. BTC lost -$3,087.01 (Sharpe -2.85, -35.9% MaxDD) and swamps
ETH's +$1,704.80 and HYPE's nominal +$90.11; one winning coin out of
three with a combined PF of 0.95 is a loser, not a mixed result.
Win rate ~32% combined, and the exit split is near-even between the
opposite VI cross (signal) and the ATR stop, so the squeeze-timed
entries still reverse about as often as they run. Fees were $7,739.30
against a -$1,292 net — the system is roughly break-even gross and
loses to friction, which is the honest summary: the squeeze gate
filters trades without filtering losers.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 822-trade sample: the combined loss is small relative to fees, so
  the verdict is "loser, but close to break-even gross" rather than a
  blowout rejection.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
