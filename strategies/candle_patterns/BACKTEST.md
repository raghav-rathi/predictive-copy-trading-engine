# Nison candlestick pattern reversal — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Bullish/bearish engulfing + pin bars (wick >= 2x body, body in favorable third, range >= 0.5 ATR); enter the pattern, exit on the opposite pattern; 1.5xATR stop, 2xATR target, 24-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 1145 | 32.3% | -8759 | -87.6% | -9.21 | -87.7% | -7.65 | 0.59 |
| ETH | 1091 | 32.1% | -8721 | -87.1% | -9.69 | -87.7% | -7.99 | 0.56 |
| HYPE | 1009 | 39.6% | -5297 | -53.1% | -3.54 | -56.5% | -5.25 | 0.82 |

## Verdict: LOSER (port failure)

1,009-1,145 trades per coin: single-bar patterns on 1h crypto are noise. Win rates of 32-40% with 2:1 target/stop should work if patterns had any memory -- they do not at this timeframe. The patterns detect exactly what Nison described; the market simply does not care on hourly bars. Costs turn a -50% strategy into -87%.

## Calibration note

Pattern detectors verified on constructed bars: engulfing requires body engulfment, pin bars require the wick/body geometry, centered doji bars are rejected. Exit wiring is exactly the opposite-pattern flag. Indicator correct; the timeframe is wrong for the idea.

## Mechanism

Bullish/bearish engulfing + pin bars (wick >= 2x body, body in favorable third, range >= 0.5 ATR); enter the pattern, exit on the opposite pattern; 1.5xATR stop, 2xATR target, 24-bar max hold.

Source: Steve Nison — Japanese candlestick patterns (engulfing, pin bar) —
https://www.investopedia.com/terms/b/bullish-engulfing-pattern.asp

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
