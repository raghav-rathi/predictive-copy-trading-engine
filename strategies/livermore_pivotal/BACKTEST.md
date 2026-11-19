# Livermore Pivotal Point — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 34 | 35.3% | 366.89 | 0.55 | -7.2% | 10.79 | 1.23 |
| ETH | 33 | 27.3% | 693.38 | 0.79 | -8.2% | 21.01 | 1.36 |
| HYPE | 49 | 28.6% | -1561.90 | -2.62 | -16.3% | -31.88 | 0.43 |
| **Combined** | **116** | **30.2%** | **-501.63** | **-0.27** | **-5.6%** | **-4.32** | **0.92** |

Fees: total $779.97.
Exits: BTC {'stop': 30, 'signal': 4}; ETH {'stop': 29, 'signal': 4}; HYPE {'stop': 43, 'signal': 6}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29,498.37.

## Verdict: LOSER (nominal) — −$501.63 on 116 trades, combined Sharpe −0.27, MaxDD −5.6%.

BTC (+$366.89) and ETH (+$693.38) both win, but HYPE loses
−$1,561.90 (PF 0.43, expectancy −$31.88/trade, MaxDD −16.3%) and
more than wipes them out. The combined −$501.63 is small against
$779.97 of fees — gross of fees the system is roughly break-even,
and the win rate (30.2%) with a 2xATR stop / 2.5xATR trail means
winners have to run well past the trail to pay for the losers,
which they mostly do not. The signal exits fire rarely (14 of 116
trades); the stop/trail carries nearly every position. No
parameter was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 116 trades is a thin sample for a three-coin combined verdict,
  and the HYPE leg dominates the loss.
- The reaction/resumption expiry guards (10 / 20 bars) and the
  volume thresholds are interpretation choices (see
  CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
