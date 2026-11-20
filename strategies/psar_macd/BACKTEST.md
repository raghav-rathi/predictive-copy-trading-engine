# Parabolic SAR + MACD Agreement — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795183200000) (2026-03-14 22:00 UTC →
2026-11-20 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 6016, ETH 6016, HYPE 6014. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it. HYPE's cache starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 210 | 31.9% | -2713.54 | -2.09 | -28.1% | -12.92 | 0.71 |
| ETH | 217 | 32.7% | -2746.35 | -2.31 | -28.8% | -12.66 | 0.68 |
| HYPE | 247 | 41.7% | 3053.98 | 1.75 | -12.5% | 12.36 | 1.25 |
| **Combined** | **674** | **35.8%** | **-2405.90** | **-0.70** | **-13.5%** | **-3.57** | **0.92** |

Fees: total $5156.56.
Exits: BTC {'stop': 140, 'signal': 70}; ETH {'stop': 156, 'signal': 61}; HYPE {'stop': 153, 'signal': 94}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,583.26.

## Verdict: LOSER (nominal HYPE winner only) — -$2,405.90 on 674 trades, combined Sharpe -0.70, MaxDD -13.5%.

BTC and ETH both lose badly (PF 0.71 and 0.68, Sharpe -2.09 and
-2.31); HYPE is green (+$3,053.98, PF 1.25, 41.7% win rate) but
does not offset the other two. The PSAR flip is a lagging
reversal signal on 1h crypto — it flips after the move, and the
MACD filter does not rescue the entry timing. Fees ($5,156.56)
are more than 2x the net loss. No parameter was tuned; the spec
shipped as written, and the calibration sweep (see
CALIBRATION.md) found no alternate setting that turns it green.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 674 trades is a decent sample; BTC/ETH agree in sign, HYPE
  disagrees — the combined loss is not a one-coin artifact, and
  the HYPE win is not a robust edge claim.
- The PSAR seed (long from bar 0) and the flip-reset rule are
  interpretation choices; see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
