# SMC market-structure (BOS/CHoCH) trend — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Fractal (2,2) swing pivots; bullish/bearish BOS continues the leg, CHoCH reverses; exit when structure breaks the other way; 2xATR stop, 3xATR trail, 168-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 287 | 30.3% | -3062 | -30.8% | -1.93 | -37.4% | -10.67 | 0.76 |
| ETH | 295 | 29.8% | -3123 | -31.3% | -1.93 | -40.2% | -10.59 | 0.76 |
| HYPE | 248 | 37.1% | +3089 | +32.0% | +1.74 | -16.2% | +12.46 | 1.20 |

## Verdict: MIXED (HYPE winner, BTC/ETH losers)

HYPE +32.0% (Sharpe 1.74, 248 trades) is the batch's best print, and the (3,3)-pivot sweep keeps it at +32.9% (Sharpe 1.86) -- the HYPE edge is stable, not a parameter fluke. BTC/ETH lose ~-31% each: structure breaks on choppy majors are false-breakout generators. Regime-dependent, same as every other trend system in the library: it works where trends exist.

## Calibration note

Pivot/BOS/CHoCH mechanics verified on synthetic legs: continuation BOS entries during the up leg, CHoCH short at the reversal, direction persists through shallow pullbacks. Pivot confirmation lag (RIGHT=2) verified causal. (3,3) sweep: HYPE stable, BTC/ETH still negative -- the failure mode is the market, not the parameter.

## Mechanism

Fractal (2,2) swing pivots; bullish/bearish BOS continues the leg, CHoCH reverses; exit when structure breaks the other way; 2xATR stop, 3xATR trail, 168-bar max hold.

Source: SMC — BOS/CHoCH structure mechanics (LuxAlgo/TV docs) —
https://www.tradingview.com/scripts/liquiditysweep/

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
