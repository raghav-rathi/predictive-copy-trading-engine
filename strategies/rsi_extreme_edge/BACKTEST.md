# RSI extreme-edge fade — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars,
2026-03-14 22:00 UTC → 2026-10-10 13:00 UTC (BTC/ETH 5037 bars, HYPE 5035 bars).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR(14) stop, 3x leverage cap, $10k start.
Warmup 60 bars.

## Results (shipped config: RSI(14) 90/10 cross-back, 1.5xATR stop, 1.5xSL target, 72-bar max hold)

| Coin | Trades (signals) | Win% | Net $ | Sharpe | MaxDD | Expectancy |
|---|---|---|---|---|---|---|
| BTC | 1 (2) | 0.0% | -$109.00 | -1.21 | -1.4% | -$109.00 |
| ETH | 2 (3) | 50.0% | +$36.18 | +0.45 | -1.1% | +$18.09 |
| HYPE | 1 (2) | 0.0% | -$103.21 | -1.46 | -1.6% | -$103.21 |
| **Combined** | **4 (7)** | **25.0%** | **-$176.03** | — | — | **-$44.01** |

## Verdict: UNVALIDATABLE at 1h — not a loser, a non-starter

RSI(14) crossed past 90 on 1–8 bars out of ~5,037 per coin (below 10 on
exactly 14 bars each). Four trades in seven months is not a sample; it is
anecdote. The author's system (138 live trades on BloFin, 2026) must run at
a faster timeframe or under different market conditions — at 1H the extreme
readings the system needs almost never occur, so the mechanism cannot be
confirmed or rejected here. Shipped the author's exact parameters rather
than re-tuning to manufacture signals.

## Author's coin-personality findings: cannot replicate

The author reported BTC/DOGE shorts working, SOL shorts a coin flip, and SOL
longs at RSI<10 working. Our universe is BTC/ETH/HYPE and our total sample
is 4 trades (1 long, 3 shorts, one win on ETH). Nothing about the author's
personality findings can be confirmed or denied from this — reported as
insufficient data, not as contradiction.

## Mechanism

Fade RSI(14) exhaustion on 1H: short the bar where RSI crosses back below 90
after being above it; long the bar where RSI crosses back above 10 after
being below it. Entry at the next bar's open (the author's "close of the
confirming bar" is one bar earlier — approximation documented). 1.5xATR(14)
stop, target at 1.5x the stop distance (2.25xATR), 72-bar max hold, no
signal exits. Per-coin direction filter parameterized via COIN_FILTER
(default: both directions on all coins).
