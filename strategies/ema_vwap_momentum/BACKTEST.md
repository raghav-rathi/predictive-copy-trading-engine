# EMA Cross + Session VWAP Momentum — Backtest

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
| BTC | 261 | 25.3% | -3136.43 | -2.57 | -32.3% | -12.02 | 0.65 |
| ETH | 292 | 27.4% | -3672.53 | -3.29 | -43.1% | -12.58 | 0.60 |
| HYPE | 246 | 39.0% | 1219.18 | 0.96 | -14.0% | 4.96 | 1.14 |
| **Combined** | **799** | **30.3%** | **-5589.78** | **-2.07** | **-21.8%** | **-7.00** | **0.79** |

Fees: total $6152.82.
Exits: BTC {'signal': 152, 'stop': 109}; ETH {'signal': 175, 'stop': 117}; HYPE {'signal': 162, 'stop': 84}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$24,410.22.

## Verdict: LOSER (worst of the batch) — -$5,589.78 on 799 trades, combined Sharpe -2.07, MaxDD -21.8%.

The worst batch-41 strategy: BTC and ETH lose with profit factors
0.65 and 0.60 and Sharpe -2.57 / -3.29, ETH drawing down -43.1%.
HYPE is nominally green (+$1,219.18, PF 1.14) but far from
offsetting the other two. The EMA cross fires late into
already-moving trends and the VWAP exit cuts winners short —
signal exits (489) outnumber stops (310), so the strategy exits
itself out of trades that then keep moving. Fees ($6,152.82)
exceed the net loss. No parameter was tuned; the spec shipped as
written, and the calibration sweep (see CALIBRATION.md) found no
alternate setting that turns it green.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 799 trades is a decent sample; BTC/ETH agree in sign, HYPE
  disagrees — the combined loss is not a one-coin artifact, and
  the HYPE win is not a robust edge claim.
- The VWAP exit (any close back through the session VWAP) is a
  tight leash by design; see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
