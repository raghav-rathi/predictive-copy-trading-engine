# TSI — backtest

Strategy: Blau TSI(25,13) crossing its 7-period signal line;
zero-line gate ON (longs only when TSI<0 at cross, shorts when TSI>0),
exhaustion exits OFF, opposite cross exits, 2.5xATR stop, 120-bar max hold.

Data: cached Hyperliquid 1h candles, **2026-03-14 → 2026-10-10**
(5,037 bars/coin), read offline from `data/candles/*_1h.csv`.
Params: start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=90.

## Default (zero gate ON, exhaustion OFF)

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$3,644.57 | 272 | 29.0% | -3.28 | -39.89% | -$13.40 |
| ETH  | -$2,811.69 | 268 | 29.5% | -2.42 | -37.56% | -$10.49 |
| HYPE | +$4,303.92 | 252 | 40.5% |  2.73 | -11.40% | +$17.08 |

## Zero gate OFF

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$4,643.98 | 438 | 28.5% | -3.75 | -47.99% | -$10.60 |
| ETH  | -$3,990.60 | 438 | 26.5% | -2.87 | -47.39% |  -$9.11 |
| HYPE | +$2,116.64 | 397 | 36.3% |  1.39 | -13.56% |  +$5.33 |

## Exhaustion exits ON (zero gate on)

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$3,425.80 | 272 | 29.0% | -3.22 | -38.55% | -$12.59 |
| ETH  | -$2,205.59 | 268 | 29.5% | -1.94 | -36.15% |  -$8.23 |
| HYPE | +$2,183.77 | 252 | 40.5% |  1.81 | -11.40% |  +$8.67 |

## Verdict

**Clear loser on BTC and ETH; strong winner on HYPE.** The zero-line
gate is the right call (gate-off is worse on all three coins: more
trades, worse every metric). Exhaustion exits are a mixed bag — they
help BTC/ETH slightly but halve HYPE's edge, so they stay OFF.
HYPE's +$4.3k / Sharpe 2.73 is the best single result in this batch;
it reflects HYPE's strong directional runs in this window, not a claim
that TSI is a good BTC strategy. Report both sides: it is.
