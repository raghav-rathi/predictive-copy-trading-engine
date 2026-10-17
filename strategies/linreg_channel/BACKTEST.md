# Raff linear-regression channel mean-reversion — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: LSMA(50) +/- 2 sigma of residuals; long the lower-band tag that closes back inside, short the upper-band tag; exit at midline or opposite band; 1.5xATR stop, 2xATR target, 48-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 411 | 47.0% | -5246 | -52.5% | -4.29 | -54.5% | -12.77 | 0.66 |
| ETH | 397 | 49.4% | -4703 | -47.0% | -3.90 | -47.1% | -11.85 | 0.70 |
| HYPE | 388 | 47.2% | -4122 | -41.2% | -3.43 | -49.6% | -10.62 | 0.73 |

## Verdict: LOSER

Band tags fade into trends that keep tagging: -52.5/-47.0/-41.2 with ~400 trades. A regression channel assumes stationarity around the fit; crypto trends ride the band for dozens of bars, and each tag adds a loser. Mean-reversion dies in trends -- the library's standing lesson, confirmed again.

## Calibration note

LSMA verified against numpy polyfit to 1e-9; on a perfect line the band width collapses as it should. Tag logic verified on a constructed dip: wick through + close back inside fires, and only then. Truncation test proves lookahead-freedom.

## Mechanism

LSMA(50) +/- 2 sigma of residuals; long the lower-band tag that closes back inside, short the upper-band tag; exit at midline or opposite band; 1.5xATR stop, 2xATR target, 48-bar max hold.

Source: Gilbert Raff — linear regression channel —
https://www.investopedia.com/terms/r/regression-channel.asp

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
