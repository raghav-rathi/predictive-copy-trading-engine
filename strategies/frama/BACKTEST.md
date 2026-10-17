# Ehlers FRAMA fractal-adaptive trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Fractal-dimension alpha (N=16) adaptive average of (h+l)/2; long on close crossing above FRAMA with slope>0 and FRAMA above its 100-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 164 | 26.2% | -1781 | -17.8% | -2.12 | -20.0% | -10.86 | 0.66 |
| ETH | 171 | 29.2% | -729 | -7.3% | -0.63 | -12.6% | -4.26 | 0.86 |
| HYPE | 148 | 29.7% | -709 | -7.1% | -0.99 | -12.6% | -4.79 | 0.82 |

## Verdict: LOSER (small)

Same story as VIDYA: the fractal alpha works exactly as Ehlers described (alpha->1 on straight trends, ->0.01 in chop), but the cross signal loses on all three coins (-17.8/-7.3/-7.1). Adaptive averages solve lag, not direction. 148-171 trades at 26-30% win rate.

## Calibration note

Alpha verified in [0.01,1], dimension in [1,2] on all bars. Straight-line test: FRAMA == price to 2%. Chop test: FRAMA moves less than price. Truncation test proves lookahead-freedom. Indicator correct; signal loses.

## Mechanism

Fractal-dimension alpha (N=16) adaptive average of (h+l)/2; long on close crossing above FRAMA with slope>0 and FRAMA above its 100-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold.

Source: John Ehlers — Fractal Adaptive Moving Average (FRAMA) —
https://www.slideserve.com/mark-barnes/presented-by-john-ehlers-powerpoint-ppt-presentation

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
