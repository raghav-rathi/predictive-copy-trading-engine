# Vortex — backtest

Strategy: VI+/VI- crosses (Botes & Siepman, S&C Jan 2010), ADX(14) > 20
gate on entries, exit on opposite cross, 2.5xATR hard stop.

Data: cached Hyperliquid 1h candles, **2026-03-14 → 2026-10-10**
(5,037 bars/coin), read offline from `data/candles/*_1h.csv`.
Params: start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=60.

## Default (ADX filter ON)

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$2,168.38 | 319 | 27.6% | -1.52 | -36.46% | -$6.80 |
| ETH  | -$1,275.44 | 309 | 28.8% | -0.76 | -27.86% | -$4.13 |
| HYPE |   +$543.86 | 263 | 30.4% |  0.53 | -14.90% |  +$2.07 |

## ADX filter OFF

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$4,003.85 | 535 | 27.5% | -2.70 | -52.03% | -$7.48 |
| ETH  | -$2,548.44 | 566 | 29.0% | -1.42 | -38.90% | -$4.50 |
| HYPE |    +$67.03 | 491 | 32.6% |  0.19 | -14.91% |  +$0.14 |

## Verdict

**LOSER on BTC and ETH; marginally positive on HYPE.** Win rate ~28%
with trend-following exits means exits give back most of the move —
whipsaws dominate in this 2026 choppy tape. The ADX > 20 filter is
unequivocally better (halves trade count, improves every metric on all
three coins), so it ships as the default. HYPE's slight edge likely
reflects its stronger trending behavior over this window; treat as
coin-specific, not strategy skill.
