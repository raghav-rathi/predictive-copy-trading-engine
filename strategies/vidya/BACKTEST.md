# Chande VIDYA adaptive trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: CMO(9)-weighted adaptive average of close; long on cross above VIDYA with rising VIDYA above its 50-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 105 | 18.1% | -1255 | -12.5% | -1.35 | -15.1% | -11.95 | 0.70 |
| ETH | 118 | 24.6% | -634 | -6.3% | -0.68 | -12.1% | -5.38 | 0.85 |
| HYPE | 83 | 20.5% | -392 | -2.9% | -0.35 | -14.5% | -4.73 | 0.87 |

## Verdict: LOSER (small)

Adaptivity does not create edge: 105/118/83 trades, 18-25% win rates, negative everywhere. The CMO weighting slows the average in chop, but the cross signal still whipsaws -- VIDYA crosses price nearly as often as a plain MA cross in ranges, just with different timing. Tested honestly: fewer entries than a plain EMA(12)/SMA(50) cross in chop, but the survivors do not win.

## Calibration note

Recursion verified against an independent loop to 1e-9. Adaptivity verified: in a straight trend VIDYA sits within 2% of price; in chop it lags materially. The failure is the signal, not the indicator.

## Mechanism

CMO(9)-weighted adaptive average of close; long on cross above VIDYA with rising VIDYA above its 50-bar SMA; exit on cross back; 2xATR stop, 3xATR trail, 168-bar max hold.

Source: Tushar Chande — Variable Index Dynamic Average (VIDYA) —
https://www.mql5.com/en/articles/11341?print=

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
