# Donchian EMA Filter — Backtest

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
| BTC | 222 | 32.9% | -2153.12 | -1.33 | -27.8% | -9.70 | 0.79 |
| ETH | 208 | 33.7% | 153.98 | 0.19 | -19.6% | 0.74 | 1.02 |
| HYPE | 230 | 33.9% | -1121.33 | -0.52 | -21.4% | -4.88 | 0.90 |
| **Combined** | **660** | **33.5%** | **-3120.47** | **-0.75** | **-15.1%** | **-4.73** | **0.90** |

Fees: total $5036.00.
Exits: BTC {'stop': 200, 'signal': 22}; ETH {'stop': 187, 'signal': 21}; HYPE {'stop': 204, 'signal': 26}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$26,974.35 — $94.82 above $30,000 + net PnL (-$3,120.47), which is the
mark-to-market of positions still open at the window end (net PnL
counts closed trades only).

## Verdict: LOSER — -$3,120.47 on 660 trades, combined Sharpe -0.75, MaxDD -15.1%.

ETH is nominally flat (+$153.98, PF 1.02 — noise on 208 trades) while
BTC (-$2,153.12, PF 0.79) and HYPE (-$1,121.33, PF 0.90) lose. The
exit mix is the giveaway: 591 of 660 trades end on the harness stop /
trail and only 69 on the Turtle 10-bar signal exit. Breakouts on 1h
crypto keep failing fast — price breaks the 20-bar level, then
reverses through the 2xATR stop before the 10-bar exit can trigger,
so the exit that defines the Turtle system almost never gets to act.
Total fees $5,036.00 exceed the net loss, so gross of costs the
strategy is roughly breakeven (+~$1,916 before fees) — this one is
largely a fee-drag story, but with PF 0.90 and a 33.5% win rate
there is no edge hiding underneath the fees either. No parameter was
tuned; the spec shipped as written.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 660 trades is a decent sample, and two of three coins lose while
  the third is flat — no robust edge claim is available here.
- The Turtle rules were designed for daily futures with a 20-day
  breakout and a 10-day exit; the 20-bar / 10-bar hourly
  translation is the spec's adaptation, not the original system.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
