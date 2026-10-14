# Bollinger on RSI — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-20 → 2026-10-14
(BTC 5,001 bars; ETH 5,001; HYPE 5,002).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 1.5xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 20-period Bollinger Bands (2σ) on RSI(14);
enter on re-entry from outside the band, exit at the midline, 1.5xATR
stop, no trail, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 252 | 46.8% | −$4,156 | −41.6% | −4.05 | −43.5% | −$16.49 | 0.61 |
| ETH | 231 | 48.5% | −$4,099 | −41.0% | −4.17 | −41.3% | −$17.75 | 0.59 |
| HYPE | 260 | 46.9% | −$4,820 | −48.2% | −4.78 | −48.9% | −$18.54 | 0.56 |
| **Combined** | **743** | **47.4%** | **−$13,075** | — | — | — | −$17.60 | — |

## Verdict: LOSER (killed — the "high win rate" trap)

The cruelest result in the batch: ~47% win rate on all three coins and
still −$13,075 combined. Average loss dwarfs average win (expectancy
−$17.60/trade, worst per-trade in the batch). Fading RSI extremes on
1h crypto catches falling knives: the midline exit cuts winners at the
mean while the 1.5xATR stop takes full losses on the extensions that
don't revert. Uniformly bad across coins — even HYPE bleeds −48.2%.
Mean reversion without a regime filter is dead here. Killed.

## Calibration note

Indicators verified: bands match independent rolling mean/std exactly;
band ordering (upper ≥ mid ≥ lower) holds; every long entry confirmed
to follow a genuine lower-band tag; truncation test proves
lookahead-freedom. Mechanism quirk: banding RSI double-normalizes —
RSI is already bounded 0–100, so the bands mostly mark RSI's own
volatility regime, not price exhaustion. Revisit path, if any: require
price confirmation (e.g. bullish close) on the re-entry bar and use a
time stop half the current length.
