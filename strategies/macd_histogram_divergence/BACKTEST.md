# MACD Histogram Divergence — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795269600000) (2026-03-14 22:00 UTC →
2026-11-21 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6040, ETH 6040, HYPE 6038.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 152 | 32.2% | -2627.61 | -2.41 | -30.1% | -17.29 | 0.63 |
| ETH | 154 | 34.4% | -598.50 | -0.37 | -18.1% | -3.89 | 0.91 |
| HYPE | 169 | 37.3% | 1011.70 | 0.86 | -17.8% | 5.99 | 1.14 |
| **Combined** | **475** | **34.7%** | **-2214.41** | **-0.73** | **-16.0%** | **-4.66** | **0.90** |

Fees: total $3555.68.
Exits: BTC {'stop': 109, 'signal': 43}; ETH {'stop': 98, 'signal': 56}; HYPE {'stop': 111, 'signal': 58}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,085.60.

## Verdict: LOSER (thin) — −$2,214.41 on 475 trades, combined Sharpe −0.73, MaxDD −16.0%.

The closest to break-even of the batch, but still negative on two
of three coins. Only HYPE is green (+$1,011.70, PF 1.14); BTC
(−$2,627.61, PF 0.63) carries the loss and ETH is near flat
(−$598.50, PF 0.91). Most exits are harness stops (318 of 475),
not signal exits (157) — a divergence entry on 1h bars does not
reliably mark a turn, and positions then ride to the 2xATR stop.
No parameter was tuned; the spec shipped as written, and neither
calibration alternate turns it green (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 475 trades is a moderate sample, but the three coins disagree in
  sign and the combined PF is 0.90 — no robust edge claim either
  way, and the combined result is negative.
- Divergence signals are rare and lagging by construction (the
  pivot is only confirmed 2 bars after the low); the 2-bar
  confirmation plus next-bar-open execution costs the turn.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
