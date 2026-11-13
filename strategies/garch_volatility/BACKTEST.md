# GARCH Volatility — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794574800000) (2026-03-14 22:00 UTC →
2026-11-13 13:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5847, ETH 5847, HYPE 5845.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 110 | 35.5% | 80.04 | 0.16 | -7.4% | 0.73 | 1.03 |
| ETH | 109 | 27.5% | -393.38 | -0.52 | -6.0% | -3.61 | 0.86 |
| HYPE | 144 | 28.5% | -1287.35 | -2.76 | -16.1% | -8.94 | 0.61 |
| **Combined** | **363** | **30.3%** | **-1600.70** | **-1.01** | **-7.0%** | **-4.41** | **0.82** |

Fees: total $2647.42.
Exits: BTC {'signal': 97, 'stop': 13}; ETH {'signal': 95, 'stop': 14}; HYPE {'signal': 134, 'stop': 10}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,399.30.

## Verdict: LOSER — -$1,600.70 on 363 trades, combined Sharpe -1.01, MaxDD -7.0%.

The GARCH vol filter does not save the 20-bar breakout on this
window: win rate 30.3% and PF 0.82 mean the system loses a little on
almost every coin, and $2,647.42 of fees eat what little the winners
make. BTC is essentially breakeven (+$80.04, PF 1.03) and ETH is a
small loser (-$393.38, PF 0.86); the damage is HYPE (-$1,287.35,
Sharpe -2.76, PF 0.61, MaxDD -16.1%), where normal-vol breakouts
kept failing. The one thing that worked as designed is the exit:
326 of 363 trades ended on the signal exit (close back inside the
range) and only 37 on the stop, so the system really is the
breakout-plus-range-exit as written — the entries just do not
follow through. MaxDD -7.0% is mild, so this is a slow bleed, not a
blow-up.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 363-trade sample, but the edge is negative on all three coins
  (BTC only at breakeven) — no coin supports the system as shipped.
- The vol filter is a blunt 30th–70th band on a fixed-parameter
  GARCH forecast; it cannot tell a genuine breakout from a
  range-expansion fake-out, and the normal band still contains
  most bars.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
