# RSI Volume Confirmation — Backtest

**Data:** Hyperliquid 1h candles from the local cache
(`data/candles/{BTC,ETH,HYPE}_1h.csv`). Window t in
[1773525600000, 1794924000000) (2026-03-14 22:00 UTC →
2026-11-17 14:00 UTC), duplicates dropped (keep first), filtered to the
window BEFORE indicators. $10k start per coin, 1% risk per trade on the
2xATR stop, 3x leverage cap, 0.045% fee + 0.01% slippage per side,
funding off, max hold 120 bars.

**Bar counts used:** BTC 5944, ETH 5944, HYPE 5942.

## Results (shipped config)

| Coin | Trades | Win% | Net $ | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 241 | 26.1% | -2733.31 | -2.22 | -33.5% | -11.34 | 0.69 |
| ETH | 242 | 24.0% | 146.54 | 0.22 | -17.2% | 0.61 | 1.02 |
| HYPE | 192 | 29.2% | -102.37 | 0.02 | -10.0% | -0.53 | 0.99 |
| **Combined** | **675** | **26.2%** | **-2689.14** | **-0.84** | **-15.7%** | **-3.98** | **0.89** |

Fees: total $5282.92.
Exits: BTC {'stop': 145, 'signal': 96}; ETH {'signal': 126, 'stop': 116}; HYPE {'signal': 96, 'stop': 96}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$27,341.47.

## Verdict: LOSER — -$2,689.14 on 675 trades, combined Sharpe -0.84, MaxDD -15.7%.

An RSI 50-cross with a volume filter is a high-frequency loser on
1h crypto: 675 trades, a 26.2% win rate, PF 0.89, and -$2,689.14
net after $5,282.92 in fees. BTC is the worst leg (-$2,733.31,
Sharpe -2.22, MaxDD -33.5%), ETH is essentially breakeven
(+$146.54, PF 1.02) and HYPE is breakeven (-$102.37, PF 0.99).
The exits split nearly evenly (318 signal vs 357 stop), so the
reverse-cross exit does real work here — the problem is the
entry: RSI crosses 50 constantly in choppy 1h crypto, the 1.25x
volume filter does not separate genuine momentum from noise, and
the 26% win rate cannot cover the 2xATR stops. No parameter was
tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 675 trades is a large sample, and the loss is broad-based
  (two coins near breakeven, BTC deeply negative) — the edge is
  absent, not merely unlucky.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
