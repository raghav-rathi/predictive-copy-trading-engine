# Ehlers Center of Gravity — Backtest

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
| BTC | 1233 | 46.0% | -8075.01 | -8.05 | -81.0% | -6.55 | 0.60 |
| ETH | 1243 | 48.9% | -7406.06 | -6.75 | -75.2% | -5.96 | 0.68 |
| HYPE | 1181 | 53.6% | -5412.02 | -4.11 | -57.0% | -4.58 | 0.79 |
| **Combined** | **3657** | **49.4%** | **-20893.09** | **-8.32** | **-69.9%** | **-5.71** | **0.70** |

Fees: total $18528.97.
Exits: BTC {'signal': 917, 'stop': 316}; ETH {'signal': 937, 'stop': 306}; HYPE {'signal': 888, 'stop': 293}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$9,106.91.

## Verdict: LOSER (heavy) — -$20,893.09 on 3657 trades, combined Sharpe -8.32, MaxDD -69.9%.

All three coins lose badly; HYPE is the "best" at -$5,412.02 (PF
0.79) and still loses more than half its starting equity. The CG
crosses its 3-bar trigger constantly on 1h crypto (~1 trade per 5
bars per coin), so the strategy churns: $18,529 of fees on $20,893
of net loss. Gross PnL before fees is about -$2,364 — the entries
are near-breakeven before costs and the fee churn destroys the
account. Most trades (2742 of 3657) exit on the opposite cross, so
positions last only a few bars on average. No parameter was tuned;
the spec shipped as written, and both calibration alternates lost
money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- The brief's weighting convention (newest price weight 10) makes CG
  move opposite to price — see CALIBRATION.md. The shipped entries
  are therefore counter-trend by construction on this convention.
- 3657 trades is a large sample, but it is one window and three
  correlated coins — the loss is a property of the crossover churn
  plus fees, not a small-sample fluke.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
