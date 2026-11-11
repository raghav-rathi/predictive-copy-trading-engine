# Supertrend + EMA(200) Filter — Backtest

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
| BTC | 76 | 35.5% | -768.84 | -0.82 | -14.9% | -10.12 | 0.79 |
| ETH | 87 | 35.6% | -773.31 | -0.71 | -14.2% | -8.89 | 0.83 |
| HYPE | 83 | 39.8% | 2747.54 | 2.16 | -7.2% | 33.10 | 1.63 |
| **Combined** | **246** | **37.0%** | **1205.40** | **0.59** | **-5.7%** | **4.90** | **1.10** |

Fees: total $2091.58.
Exits: BTC {'stop': 74, 'signal': 2}; ETH {'stop': 87}; HYPE {'stop': 82, 'signal': 1}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$31,205.40.

## Verdict: Loser on BTC/ETH — the combined +$1,205.40 is a one-coin story, not a system.

BTC (−$769, PF 0.79) and ETH (−$773, PF 0.83) both lose with
near-identical profiles, and HYPE's +$2,748 (PF 1.63, Sharpe 2.16)
is doing all of the combined work — a single trending coin in a
window where HYPE trended hard. The damning detail is the exit mix:
243 of 246 trades exit on the ATR stop and only 3 on the Supertrend
flip. On 1h bars the flips lag so far behind the 2xATR stop that the
signal exit is nearly dead — the system is really "buy the flip,
get stopped out" on BTC/ETH. The EMA(200) filter did not rescue
either coin: it filtered entries but the entries it allowed still
lost. As shipped, not tradeable; HYPE's number is a trend-regime
artefact, not evidence the filter adds edge.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 246 trades but dominated by stop exits; the signal-exit rule is
  barely exercised, so little is learned about the flip exit itself.
- HYPE's strong trend in-window flatters any trend system; the
  combined figure must not be read as cross-coin edge.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
