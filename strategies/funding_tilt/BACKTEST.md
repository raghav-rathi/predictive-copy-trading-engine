# Funding-Rate Tilt (contrarian) — Backtest

**Data:** Hyperliquid 1h candles + real hourly `fundingHistory`, BTC + ETH,
2026-03-14 → 2026-10-09 (~5,000 bars; ~3,500-4,500 funding prints per coin,
API coverage gaps noted).
**Costs:** 0.045% taker + 0.01% slippage per side; funding modeled in a
second run (see below).
**Sizing:** 1% risk on 2xATR stop, 2xATR target, 72-bar max hold, $10k start.

| Coin | Trades | Win% | Net | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|
| BTC | 110 | 50.0% | +$240 (+2.4%) | 0.43 | -7.3% | +$2.20 | 1.06 |
| ETH | 116 | 43.1% | -$960 (-9.6%) | -1.14 | -15.0% | -$8.28 | 0.79 |

With funding PnL modeled (hourly accrual): BTC +2.5% (funding +$8.58),
ETH -9.5% (funding +$5.68) — funding is second-order at these hold times.

## Verdict: MIXED, leans negative

BTC is slightly positive but ETH fails; the contrarian read (fade crowded
funding) doesn't survive both coins. Note the honest negative: funding
z-scores hit the theoretical max (|z|=12.88) on a market-wide funding
spike both coins shared — the signal fires hardest exactly when crowding
is a rational risk premium, not a fade. Possible future work: require the
z-extreme to persist N hours (crowding, not a print), or trade only the
funding *carry* (idea 3 in STRATEGY_RESEARCH.md) instead of fading it.
Not for capital as a standalone.
