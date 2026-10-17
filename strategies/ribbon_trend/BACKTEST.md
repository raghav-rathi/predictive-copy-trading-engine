# EMA ribbon (8/13/21/34/55) alignment trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Enter on full ribbon alignment flip with >0.4% fan spread; exit when alignment breaks or fan compresses below 0.2%; 2xATR stop, 3xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 103 | 26.2% | -1426 | -14.3% | -1.41 | -22.0% | -13.84 | 0.69 |
| ETH | 106 | 29.2% | -1800 | -18.0% | -2.09 | -20.6% | -16.98 | 0.60 |
| HYPE | 143 | 37.8% | +1720 | +17.3% | +1.36 | -9.2% | +12.03 | 1.27 |

## Verdict: MIXED (HYPE winner, BTC/ETH losers)

HYPE +17.3% (Sharpe 1.36, 143 trades); MIN_FAN=0.008 sweep improves it to +26.2% (Sharpe 2.17) -- the HYPE trend edge survives the stricter gate, suggesting it is real-ish. BTC/ETH lose -14% to -18%: the fan gate keeps entries out of flat chop but cannot save a trend system in choppy markets. Same regime story as the rest of the library.

## Calibration note

Stacking verified in sustained trends; fan spread exceeds 0.4% there. Flat-chop test: entries stay under 5% of bars via the fan gate. Exhaustion exit verified: alignment loss after a long entry always produces a long_exit.

## Mechanism

Enter on full ribbon alignment flip with >0.4% fan spread; exit when alignment breaks or fan compresses below 0.2%; 2xATR stop, 3xATR trail, 168-bar max hold.

Source: Multi-EMA ribbon alignment (trend-following classic) —
https://www.investopedia.com/terms/e/exponential-moving-average.asp

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
