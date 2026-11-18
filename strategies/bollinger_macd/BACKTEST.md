# Bollinger MACD — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1795010400000) (2026-03-14 22:00 UTC →
2026-11-18 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5968, ETH 5968, HYPE 5966.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 88 | 43.2% | -1073.30 | -1.64 | -12.3% | -12.20 | 0.69 |
| ETH | 79 | 49.4% | -68.60 | -0.06 | -8.6% | -0.87 | 0.97 |
| HYPE | 54 | 50.0% | 208.83 | 0.44 | -5.9% | 3.87 | 1.11 |
| **Combined** | **221** | **47.1%** | **-933.06** | **-0.77** | **-5.9%** | **-4.22** | **0.88** |

Fees: total $1909.44.
Exits: BTC {'signal': 57, 'stop': 31}; ETH {'signal': 56, 'stop': 23}; HYPE {'signal': 34, 'stop': 20}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$29066.94.

## Verdict: LOSER — -$933.06 on 221 trades, combined Sharpe -0.77, MaxDD -5.9%.

Bollinger band tag + MACD cross loses modestly on 1h crypto:
221 trades, a 47.1% win rate, PF 0.88, and -$933.06 net after
$1,909.44 in fees. It is the least bad of this batch and the only
one with a winning coin — HYPE +$208.83 (PF 1.11, 50.0% win rate)
— while ETH is near breakeven (-$68.60, PF 0.97) and BTC drags
the total down (-$1,073.30, PF 0.69). The exit split is the
reverse of the trend strategies (147 signal vs 74 stop): the
opposite-MACD-cross / opposite-band exit fires first most of the
time, which keeps drawdowns small (combined MaxDD only -5.9%)
but also cuts winners short — the 47.1% win rate with PF 0.88
means the average loss still outweighs the average win. The
bounce thesis is not wrong so much as unprofitable after fees
on 1h bars. No parameter was tuned; the spec shipped as written
and lost, narrowly.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- HYPE wins (+$208.83) while BTC loses (-$1,073.30), so the
  combined -$933.06 is coin-dependent, not a uniform edge —
  and no coin's PF clears 1.11.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
