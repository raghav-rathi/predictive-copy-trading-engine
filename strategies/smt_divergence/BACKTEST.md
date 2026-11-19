# SMT Divergence — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. Two separate $10k books (BTC traded / ETH
reference, and ETH traded / BTC reference); HYPE excluded (no pair).
1% risk per trade on the 2xATR stop, 3x leverage cap, 0.045% fee +
0.01% slippage per side, funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992.

## Results (shipped config)

| Book | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC/ETH | 142 | 31.0% | -1633.01 | -1.20 | -17.5% | -11.50 | 0.77 |
| ETH/BTC | 146 | 32.2% | 181.25 | 0.23 | -15.7% | 1.24 | 1.02 |
| **Combined** | **288** | **31.6%** | **-1451.77** | **-0.55** | **-12.9%** | **-5.04** | **0.90** |

Fees: total $2,916.02.
Exits: BTC/ETH {'stop': 130, 'signal': 12}; ETH/BTC {'stop': 132, 'signal': 14}.
Combined Sharpe / MaxDD are computed on the summed $20k two-book
equity curve (each book's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$18,579.93.

## Verdict: LOSER — -$1,451.77 on 288 trades, combined Sharpe -0.55, MaxDD -12.9%.

The divergence fires often (288 trades) but does not resolve in the
expected direction: both books sit at ~31–32% win rate and 262 of
288 trades end on the 2xATR stop. The ETH/BTC book is nominally
green (+$181.25, PF 1.02, expectancy +$1.24) — 146 trades of noise
around breakeven — while the BTC/ETH book loses -$1,633.01. Fees
($2,916.02) exceed the combined loss, so gross of fees the strategy
is roughly breakeven: the SMT divergence itself carries no edge on
this window, and the fee drag turns it into a loser. No parameter
was tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- BTC and ETH are highly correlated, so genuine SMT divergences are
  mostly small relative-strength wiggles, not the clean ICT setups
  the pattern describes on FX pairs; the 10-bar gap and 20-bar
  expiry are interpretation choices (see CALIBRATION.md).
- Never tune the shipped parameters on this window.

Paper only, no live execution.
