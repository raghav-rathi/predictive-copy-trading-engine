# Balanced Price Range — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795096800000) (2026-03-14 22:00 UTC →
2026-11-19 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5992, ETH 5992, HYPE 5990. (The CSVs each
contain one further bar at exactly END_MS; the half-open window
excludes it. HYPE's cache starts 2 bars into the window.)

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 181 | 22.1% | -3198.31 | -4.39 | -32.6% | -17.67 | 0.43 |
| ETH | 169 | 29.0% | 247.82 | 0.30 | -11.5% | 1.47 | 1.05 |
| HYPE | 159 | 27.0% | 3337.14 | 2.38 | -9.9% | 20.99 | 1.59 |
| **Combined** | **509** | **25.9%** | **386.65** | **0.23** | **-8.3%** | **0.76** | **1.02** |

Fees: total $4117.35.
Exits: BTC {'signal': 131, 'stop': 50}; ETH {'signal': 105, 'stop': 64}; HYPE {'signal': 101, 'stop': 58}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$30,386.65.

## Verdict: WINNER (nominal, thin) — +$386.65 on 509 trades, combined Sharpe 0.23, MaxDD -8.3%.

The combined row is green, but do not read an edge into it: the
entire profit comes from HYPE (+$3,337.14, PF 1.59, expectancy
+$20.99/trade), ETH is flat (+$247.82, PF 1.05), and BTC loses
badly (-$3,198.31, PF 0.43, Sharpe -4.39, MaxDD -32.6%). With a
25.9% win rate and PF 1.02 combined, the +$386.65 is
statistically indistinguishable from luck — one coin's winners
offsetting another coin's losers. Total fees $4,117.35 are more
than 10x the net profit, so the strategy is a fee-drag story
gross of costs as well. No parameter was tuned; the spec shipped
as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 509 trades is a decent sample, but the three coins disagree in
  sign — the combined win rests on HYPE alone and is not a robust
  edge claim.
- The "traded beyond" reading (close, not wick) and the
  replace-on-new-BPR rule are interpretation choices; see
  CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
