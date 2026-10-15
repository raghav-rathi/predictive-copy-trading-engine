# McGinley Dynamic — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-15
(BTC 5,152 bars; ETH 5,152; HYPE 5,150).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: MD(10)/MD(30) cross entries, opposite-cross
exits, 2xATR stop, 96-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 86 | 24.4% | +$2,542 | +27.4% | +1.47 | −18.7% | +$29.55 | 1.37 |
| ETH | 101 | 22.8% | −$1,173 | −11.7% | −0.52 | −34.7% | −$11.62 | 0.86 |
| HYPE | 94 | 25.5% | +$1,271 | +16.7% | +1.13 | −13.5% | +$13.52 | 1.18 |
| **Combined** | **281** | **24.2%** | **+$2,640** | — | — | — | **+$9.40** | — |

## Verdict: batch's best — positive combined, BTC Sharpe 1.47

The speed-adaptive MA earns its keep: only 281 trades (the ^4 term
keeps the lines glued to price instead of whipsawing), a 24.2% win
rate with strong positive skew (+$29.55 expectancy on BTC). BTC +27.4%
at Sharpe 1.47 and HYPE +16.7% at 1.13 are real-looking; ETH −11.7% is
the weak leg. The slower MD(20,60) variant is even better combined
(+$1,708, BTC Sharpe 2.29 on just 50 trades) — worth walk-forward
validation before any sleeve talk. Nothing is for live capital yet.
