# Stochastic RSI Cross — Backtest

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
| BTC | 727 | 33.3% | -6816.92 | -6.89 | -69.1% | -9.38 | 0.55 |
| ETH | 718 | 35.1% | -5227.20 | -4.16 | -53.8% | -7.28 | 0.69 |
| HYPE | 721 | 37.2% | -5671.12 | -5.48 | -58.0% | -7.87 | 0.63 |
| **Combined** | **2166** | **35.2%** | **-17715.24** | **-7.06** | **-59.9%** | **-8.18** | **0.62** |

Fees: total $11190.71.
Exits: BTC {'signal': 556, 'stop': 171}; ETH {'signal': 553, 'stop': 165}; HYPE {'signal': 567, 'stop': 154}.
Combined Sharpe / MaxDD are computed on the summed $30k
three-coin equity curve (each coin's curve reindexed to the union of
timestamps, forward-filled, leading gaps at $10k). Combined end equity
$12,284.76.

## Verdict: LOSER — -$17,715.24 on 2,166 trades, combined Sharpe -7.06, MaxDD -59.9%.

The StochRSI cross is a disaster on 1h crypto: 2,166 trades, a 35.2%
win rate, PF 0.62, and -$17,715.24 net after $11,190.71 in fees —
the worst batch-39 strategy by a wide margin and a -59.9% combined
drawdown that wipes out nearly 60% of the $30k start. No coin wins:
BTC is the worst (-$6,816.92, Sharpe -6.89, MaxDD -69.1%), ETH loses
(-$5,227.20, PF 0.69) and HYPE loses (-$5,671.12, PF 0.63). The
exit split (1,676 signal vs 490 stop) shows the opposite-cross /
far-level exits fire constantly — the oscillator whipsaws across
its own %K/%D cross several times a day on 1h bars, so entries
churn and each round trip pays fees while the average trade loses
$8.18. StochRSI mean-reversion crosses carry no edge here.
No parameter was tuned; the spec shipped as written and lost.

## Limitations

- Single ~8-month crypto window; funding unmodeled; next-bar-open
  execution vs idealized entry.
- 2,166 trades is a very large sample and the loss is present on all
  three coins with Sharpe below -4 on every coin — the edge is
  absent, not merely unlucky.
- On a monotonic move RSI saturates and the 14-bar RSI range
  collapses, so StochRSI falls back to the 50.0 guard (see
  CALIBRATION.md); the oscillator is effectively blind in trends.
- Never tune the shipped parameters on this window.

Paper only, no live execution.
