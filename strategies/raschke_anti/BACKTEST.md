# Raschke Anti — backtest

Strategy: Linda Raschke & Larry Connors "Anti" (Street Smarts Ch.9):
trend = slow-stochastic %D(7/10) slope; arming on %K hook against the
trend or a 2-bar inside day; entry when %K re-aligns or 3/10 crosses
back above its 16-signal; exit on opposite setup; 2.0xATR hard stop
(pullback-swing-low approximation), 3.0xATR chandelier trailing,
120-bar max hold.

Data: cached Hyperliquid 1h candles, **2026-03-14 → 2026-10-10**
(5,037 bars/coin), read offline from `data/candles/*_1h.csv`.
Params: start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=90.

## Default (slope_confirm=1, arm_window=5)

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$5,498.25 | 497 | 25.8% | -5.10 | -57.75% | -$11.06 |
| ETH  | -$4,185.93 | 485 | 27.8% | -3.65 | -50.82% |  -$8.63 |
| HYPE | -$1,625.11 | 444 | 32.0% | -1.17 | -26.87% |  -$3.66 |

## slope_confirm=2

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$3,700.26 | 261 | 29.5% | -4.06 | -40.23% | -$14.18 |
| ETH  | -$1,767.82 | 246 | 32.1% | -1.70 | -33.20% |  -$7.19 |
| HYPE | -$2,191.30 | 222 | 26.6% | -1.97 | -23.95% |  -$9.87 |

## arm_window=3

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$5,101.62 | 406 | 24.1% | -4.93 | -52.53% | -$12.57 |
| ETH  | -$3,520.62 | 398 | 27.9% | -3.27 | -48.17% |  -$8.85 |
| HYPE |   -$892.63 | 361 | 33.5% | -0.61 | -19.92% |  -$2.47 |

## Verdict

**Decisive loser on all three coins at every tested setting — the
worst performer in this batch.** 25-32% win rate with trailing exits
means the re-alignment entries catch counter-trend bounces that
immediately fail; the 3/10 trigger fires too late on hourly bars in
this tape. slope_confirm=2 and arm_window=3 lose less, but "loses less
money" is not a reason to adopt a variant of a strategy that fails
everywhere. Shipped with the published-style defaults (1 / 5); the
numbers stay on the record.
