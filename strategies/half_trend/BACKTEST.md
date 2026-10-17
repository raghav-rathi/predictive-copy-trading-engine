# HalfTrend ATR-channel trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Amplitude-50 extremes, ATR(100)/2 x2 channel; stateful line trails below price in uptrends, above in downtrends; flip = entry; 2xATR stop, 3xATR trail, 240-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 40 | 20.0% | -1092 | -10.9% | -1.57 | -16.9% | -27.30 | 0.53 |
| ETH | 36 | 25.0% | -749 | -7.5% | -1.20 | -12.5% | -20.81 | 0.56 |
| HYPE | 33 | 33.3% | +103 | +1.0% | +0.21 | -9.3% | +3.12 | 1.06 |

## Verdict: FLAT (no edge)

Only 33-40 trades per coin: the amplitude-50 + ATR(100) scale makes this a very slow system that mostly sits out. HYPE prints +1.0% (noise), BTC/ETH bleed single digits. Honest read: no edge found, just a slow filter that avoids the worst chop. The line-below-price-in-uptrend / above-in-downtrend properties hold exactly as designed.

## Calibration note

State machine verified on synthetic trends: line trails the correct side, flips mark entries, no bar is ever both entries. Truncation test proves the line at bar i is independent of later data.

## Mechanism

Amplitude-50 extremes, ATR(100)/2 x2 channel; stateful line trails below price in uptrends, above in downtrends; flip = entry; 2xATR stop, 3xATR trail, 240-bar max hold.

Source: everget — HalfTrend (TradingView Pine, open source) —
https://deepwiki.com/everget/tradingview-pinescript-indicators/2.1.2-halftrend

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
