# Camarilla Pivot Breakout — Backtest

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
| BTC | 93 | 21.5% | -1334.17 | -1.54 | -18.2% | -14.35 | 0.63 |
| ETH | 84 | 27.4% | -861.52 | -1.02 | -13.0% | -10.26 | 0.73 |
| HYPE | 73 | 23.3% | 672.64 | 0.79 | -6.7% | 9.21 | 1.25 |
| **Combined** | **250** | **24.0%** | **-1523.04** | **-0.82** | **-7.3%** | **-6.09** | **0.84** |

Fees: total $1839.10.
Exits: BTC {'stop': 56, 'signal': 37}; ETH {'stop': 50, 'signal': 34}; HYPE {'stop': 39, 'signal': 34}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$28,476.96.

## Verdict: LOSER — -$1,523.04 on 250 trades, combined Sharpe -0.82, MaxDD -7.3%.

HYPE is the only green coin (+$672.64, PF 1.25) while BTC (-$1,334.17)
and ETH (-$861.52) lose; the combined win rate is just 24.0%. The
assigned 1.055 factor puts R3/S3 ~1.06 prior-day ranges away from the
prior close — far outside a normal day — so breakouts are rare
(~1 trade per 24 bars per coin) and, when they fire, are usually
late-day momentum exhaustions that reverse: 105 of 250 exits are
signal exits (price crossing back through the level), i.e. the
breakout fails and the trade is closed by its own exit rule. No
parameter was tuned; the spec shipped as written, and both
calibration alternates also lost money (see CALIBRATION.md).

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 250 trades is a small sample and the coins disagree in sign; the
  HYPE win does not survive the other two coins.
- The assigned 1.055 factor is NOT the canonical Camarilla R3
  (1.1/4 = 0.275); see CALIBRATION.md.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
