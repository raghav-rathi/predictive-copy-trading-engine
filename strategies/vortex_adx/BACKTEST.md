# Vortex + ADX — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794488400000) (2026-03-14 22:00 UTC →
2026-11-12 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5823, ETH 5823, HYPE 5821.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 309 | 23.3% | -4540.54 | -5.00 | -46.5% | -14.69 | 0.49 |
| ETH | 286 | 29.0% | -2382.45 | -2.23 | -23.9% | -8.33 | 0.71 |
| HYPE | 289 | 27.0% | -3072.44 | -3.34 | -31.4% | -10.63 | 0.65 |
| **Combined** | **884** | **26.4%** | **-9995.44** | **-5.19** | **-33.4%** | **-11.31** | **0.61** |

Fees: total $5655.48.
Exits: BTC {'signal': 208, 'stop': 101}; ETH {'signal': 183, 'stop': 103}; HYPE {'signal': 205, 'stop': 84}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$20,004.56.

## Verdict: LOSER — -$9,995.44 on 884 trades, combined Sharpe -5.19, MaxDD -33.4%.

The ADX filter does not save the Vortex cross on 1h crypto. Win rate
is only 26.4% and PF 0.61 — the winners are far too small for the
losers, and every coin loses (BTC -$4,540.54, ETH -$2,382.45, HYPE
-$3,072.44). The exit split is informative: 596 of 884 trades end on
the signal exit (opposite VI cross or ADX fading below 20), so the
system keeps getting faked out — a cross that clears ADX > 25 still
reverses or fades within a few bars more often than not, and the
2xATR stop takes the rest. Expectancy -$11.31 per trade against
$5,655.48 of fees means the system loses on the trade itself, not
just on costs. The Vortex cross is a lagging confirmation of a move
that has already happened; on 1h crypto the move is usually over by
the time VI crosses with ADX above 25.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 884-trade sample: a real sample, and the loss is consistent across
  all three coins (PF 0.49–0.71), so this is not one bad coin.
- The EMA(14) smoothing used here differs from Botes & Siepman's
  published 14-period sums; see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
