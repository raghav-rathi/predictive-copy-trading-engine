# Camarilla pivots — backtest

Strategy: Nick Stott Camarilla levels from the prior 24h-UTC session;
FADE mode (default): short first R3 touch / long first S3 touch per
session, exit at pivot mid, 3.0xATR disaster stop, 48h max hold.

Data: cached Hyperliquid 1h candles, **2026-03-14 → 2026-10-10**
(5,037 bars/coin), read offline from `data/candles/*_1h.csv`.
Params: start_equity=$10,000, risk_frac=0.01, max_leverage=3.0,
fee_rate=0.00045, slippage_rate=0.0001, use_funding=False, warmup=72.

## Default (fade, UTC session)

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$1,009.91 | 246 | 59.8% | -1.20 | -12.77% | -$4.11 |
| ETH  | -$2,183.49 | 234 | 56.4% | -2.82 | -24.90% | -$9.33 |
| HYPE | -$1,129.99 | 256 | 58.6% | -1.38 | -19.79% | -$4.41 |

## Fade, rolling-24h session

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$2,637.06 | 296 | 42.2% | -6.02 | -27.30% | -$8.91 |
| ETH  | -$1,712.15 | 292 | 51.0% | -3.74 | -17.29% | -$5.86 |
| HYPE |   -$660.63 | 269 | 54.6% | -1.60 |  -9.08% | -$2.46 |

## Breakout, UTC session

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | -$1,296.10 | 115 | 20.9% | -1.50 | -20.29% | -$11.27 |
| ETH  |    +$50.26 | 109 | 21.1% |  0.14 | -15.38% |  +$0.46 |
| HYPE |   +$584.84 | 121 | 21.5% |  0.68 | -12.06% |  +$4.83 |

## Breakout, rolling-24h session

| Coin | Net PnL | Trades | Win rate | Sharpe | Max DD | Expectancy |
|------|--------:|-------:|---------:|-------:|-------:|-----------:|
| BTC  | +$2,022.97 | 47 | 51.1% | 2.12 | -7.32% | +$43.04 |
| ETH  |   +$468.83 | 47 | 34.0% | 0.60 | -12.07% | +$9.98 |
| HYPE | +$1,294.81 | 24 | 45.8% | 1.80 | -5.02% | +$53.95 |

## Verdict

**Fade mode (the published classic) is a LOSER on all three coins.**
59-60% win rate with negative expectancy is the textbook fade profile:
wins small, losers run through the wide stop. UTC sessions beat rolling
for fades. The standout is breakout/rolling — positive on all three
coins — but it rests on thin trade counts (47/47/24), so it is a
candidate for out-of-sample follow-up, not a shipped default.
