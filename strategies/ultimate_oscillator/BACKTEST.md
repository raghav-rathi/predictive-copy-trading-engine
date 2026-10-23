# Backtest: Ultimate Oscillator Divergence

Window: 2026-03-14 -> 2026-10-18 (1h Hyperliquid candles,
ms 1773446400000-1792713599000; cache opens at 1773525600000).
Start equity $10,000 per coin. Warmup 80 bars. No funding.
Risk: 1.5xATR stop, 2xATR chandelier trail, no fixed target,
96-bar max hold, 1% risk/trade, 3x leverage, fees 0.00045 +
slippage 0.0001 per side.

## Per-coin results

| Coin | Trades | Win rate | Net $ | Net % | Sharpe | Max DD % | Expectancy $ | Profit factor | Fees $ |
|---|---|---|---|---|---|---|---|---|---|
| BTC | 16 | 31.3% | -695.81 | -6.96 | -1.75 | -7.15 | -43.49 | 0.35 | 216.94 |
| ETH | 7 | 0.0% | -617.71 | -6.18 | -3.71 | -6.18 | -88.24 | 0.00 | 60.86 |
| HYPE | 18 | 27.8% | +515.56 | +5.16 | +1.02 | -4.69 | +28.64 | 1.61 | 122.20 |
| **Combined** | **41** | **26.8%** | **-797.97** | — | — | — | **-19.46** | — | **399.99** |

Signal counts (raw, pre-harness): BTC 6 long / 10 short entries,
ETH 1 long / 6 short, HYPE 5 long / 13 short.

## Honest verdict: LOSER

Combined -$798 over 41 trades. ETH went 0-for-7; BTC's profit
factor is 0.35. Only HYPE printed green (+$516, Sharpe 1.02), on
18 trades -- too small a sample to trust, and not enough to carry
the book.

Why it likely fails: confirmed-divergence setups are rare (about
one signal per coin per two weeks), and Williams' trigger -- UO
crossing back above the divergence high -- fires late, after much
of the snapback is already priced in. The 30/70 exits then cut
winners short while the 1.5xATR stop takes full losses. The
mechanism is faithfully implemented and the parameters were fixed
a priori (no tuning to rescue it with), so this reads as a genuine
negative result for the textbook method on 1h crypto perps, not an
implementation artifact. Trade count is low, so treat even the
negative with the usual small-sample humility -- but there is
nothing here that earns live capital.
