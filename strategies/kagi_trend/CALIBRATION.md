# Kagi Yang/Yin Trend — Calibration

Reversal-amount sensitivity on the same Hyperliquid 1h data as
BACKTEST.md (BTC/ETH/HYPE, 2026-03-14 → 2026-10-19, same costs/sizing,
2xATR stop, 100-bar max hold). The reversal amount is the Kagi
equivalent of a timeframe: smaller = more columns, more transitions,
more whipsaw; larger = fewer, slower, more selective.

| Reversal | Coin | Trades | Win% | Net $ | Sharpe | PF | Expectancy |
|---|---|---|---|---|---|---|---|
| 4xATR (shipped) | BTC | 25 | 36.0% | +$3,371 | +2.70 | 2.73 | +$134.84 |
| 4xATR (shipped) | ETH | 21 | 19.0% | -$444 | -0.51 | 0.76 | -$21.15 |
| 4xATR (shipped) | HYPE | 23 | 21.7% | -$870 | -0.96 | 0.51 | -$37.82 |
| 2xATR | BTC | 69 | 20.3% | +$1,621 | +1.07 | 1.26 | +$23.49 |
| 2xATR | ETH | 63 | 19.0% | +$733 | +0.54 | 1.14 | +$11.63 |
| 2xATR | HYPE | 70 | 28.6% | +$204 | +0.26 | 1.04 | +$2.92 |
| 6xATR | BTC | 13 | 46.2% | +$2,804 | +2.71 | 4.22 | +$215.67 |
| 6xATR | ETH | 13 | 15.4% | +$1,823 | +1.72 | 2.48 | +$140.22 |
| 6xATR | HYPE | 13 | 23.1% | -$692 | -1.13 | 0.31 | -$53.21 |

## One-line verdict

- **2xATR:** positive on all three coins (combined +$2,558 on 202
  trades) — the most *consistent* setting. Smaller reversals catch
  more shoulders/waists; the win rate stays low but the expectancy
  turns positive everywhere. Trade count triples, so this is the least
  noise-driven read.
- **6xATR:** best combined (+$3,935) with the fattest per-trade
  expectancy (+$216 on BTC, PF 4.22) — but only 39 trades total and
  HYPE still loses (-$692). High variance, thin sample.
- **Shipped decision:** keep the specified 4xATR as the registry
  config. Both alternatives beat it in-sample on this exact window, so
  adopting either now would be pure in-sample selection. The honest
  read: the reversal amount is a genuine sensitivity knob (2x =
  consistency, 6x = selectivity), and the right choice needs
  walk-forward or out-of-sample evidence, not this 7-month window.
