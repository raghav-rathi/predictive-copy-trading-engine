# Ichimoku Cloud — Backtest

**Data:** Hyperliquid 1h, BTC + ETH, 2026-03-14 → 2026-10-09 (~5,000 bars).
**Costs:** 0.045% taker + 0.01% slippage per side. Funding unmodeled.
**Sizing:** 1% risk on 2.5xATR stop, 3xATR chandelier trailing, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 64 | 39.1% | -$357 (-3.6%) | -0.43 | -12.1% | -$5.58 | 0.86 |
| ETH | 67 | 28.4% | -$227 (-2.3%) | -0.26 | -8.5% | -$3.40 | 0.92 |
| **Combined** | **131** | — | **-$585** | — | — | — | — |

## The lookahead bug that almost shipped (read this)

First run showed BTC **+16.5% / Sharpe 2.31** and ETH **+18.6% / Sharpe 2.68**.
Too good — and it was fake. The Chikou confirmation was implemented as
`chikou[i] = close[i+26] > close[i]`: 26 bars of future data. Fixed to the
no-lookahead form (today's close must clear the high/low of 26 bars ago,
where the Chikou line is actually plotted). True result: mild loser.

Lesson recorded: any indicator with a shift **forward** in time (Chikou,
projected cloud) is a lookahead trap. The harness only guards execution
timing; indicator construction is on us.

## Verdict: MILD LOSER

Properly implemented, classic Ichimoku on 1h crypto slightly loses on both
coins. The setup is rare (131 trades / 7 months) and high-conviction in
theory, but the TK-cross trigger fires late after cloud breakouts and the
2.5xATR stop gives back too much on reversals. Possible future work:
4h/daily timeframes (Ichimoku's native scale), or cloud-only regime filter
with a faster trigger. Not for capital as a standalone.
