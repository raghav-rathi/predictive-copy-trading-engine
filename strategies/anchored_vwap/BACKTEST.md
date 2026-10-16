# Anchored VWAP reclaim — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-14 → 2026-10-15
(BTC 5,157 bars; ETH 5,157; HYPE 5,155).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the 2xATR stop, 3x leverage cap, $10k start.

## Results (shipped config: 51-bar fractal swing anchors, active anchor =
most recently confirmed extreme, cross + rising 5-bar slope + >=2 of last
10 bars below the line, 2xATR stop, 3xATR trail, 72-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 72 | 26.4% | −$2,291 | −22.9% | −2.94 | −24.5% | −$31.82 | 0.45 |
| ETH | 67 | 23.9% | −$1,422 | −14.2% | −1.44 | −15.0% | −$21.22 | 0.66 |
| HYPE | 59 | 37.3% | +$1,773 | +19.6% | +1.69 | −10.2% | +$30.05 | 1.56 |
| **Combined** | **198** | **29.2%** | **−$1,940** | — | — | — | **−$9.80** | — |

## Verdict: HYPE winner (+19.6%, Sharpe 1.69), majors losers

The anchor line works where trends actually follow through. HYPE's 2026
trend legs reclaim the anchored line and run (37.3% win rate, 1.56
profit factor). On BTC/ETH the reclaims fail at a ~25% win rate — the
line gets reclaimed and then immediately lost, and the 3xATR trail
cannot save a setup whose premise breaks within hours. The reclaim
filter (≥2 of 10 bars below) keeps trade count sane (59–72 per coin);
without it the system would trade every graze of the line.

Structural note: the 25-bar confirmation lag means the anchor is
always a month-old extreme on 1h bars. In fast markets that is fine
(the line is a slow institutional reference); in chop it means the
line lags the regime that broke it. Calibration shows wider anchors
(half=40) roughly double the HYPE print — the edge lives in major
swings, not minor ones — but BTC/ETH lose in every variant, so this is
a coin-scoped system, not a universal one. HYPE-only sleeve candidate
pending walk-forward validation.
