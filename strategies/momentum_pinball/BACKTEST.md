# Raschke Momentum Pinball (LBR/RSI) — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: LBR/RSI = 3-period Wilder RSI of the 1-period ROC of close; long on the flip up out of <30, short on the flip down out of >70; exit at the opposite extreme; 1.5xATR stop, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 706 | 48.0% | -6756 | -67.7% | -5.16 | -68.5% | -9.57 | 0.70 |
| ETH | 715 | 48.5% | -6948 | -69.5% | -5.62 | -69.5% | -9.72 | 0.66 |
| HYPE | 700 | 50.0% | -5496 | -55.0% | -3.89 | -63.5% | -7.85 | 0.73 |

## Verdict: LOSER (port failure)

The 1-3 bar flip horizon does not survive 1h bars. The system fires a trade roughly every 7 bars (706 on BTC); at 0.045% fee + 0.01% slippage per side on ~3x-leveraged notional, costs alone are ~0.33% of equity per round trip -- over 700 trades that is more than 2x the starting equity. The book's edge assumed daily bars and next-day first-hour entries; on hourly crypto the pinball is a cost machine.

## Calibration note

Indicator verified: independent loop recomputation of Wilder RSI(3) of diff(1) matches to 1e-6, including the pandas ewm seeding and min_periods masking. Truncation test proves lookahead-freedom. Flip frequency measured: 1 trade per ~7 bars on BTC -- the failure is structural (costs), not a bug.

## Mechanism

LBR/RSI = 3-period Wilder RSI of the 1-period ROC of close; long on the flip up out of <30, short on the flip down out of >70; exit at the opposite extreme; 1.5xATR stop, 24-bar max hold.

Source: Linda Raschke / Larry Connors — Momentum Pinball (Street Smarts) —
https://www.cryptodatadownload.com/blog/posts/short-term-strategy-momentum-pinball-python/

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
