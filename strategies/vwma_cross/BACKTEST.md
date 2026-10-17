# VWMA(20/50) volume-conviction cross — Backtest

**Data:** Hyperliquid `candleSnapshot`, 1h bars, BTC + ETH + HYPE, 2026-03-23 → 2026-10-17
(BTC 5006 bars; ETH 5006; HYPE 5008).
**Costs:** 0.045% taker fee + 0.01% slippage per side. Funding not modeled.
**Sizing:** 1% equity risk per trade on the hard-stop distance, 3x leverage cap, $10k start.

## Results (shipped config: Typical-price VWMA(20) vs VWMA(50) cross gated on volume above its 20-bar average; exit on the cross back; 2xATR stop, 3xATR trail, 120-bar max hold)

| Coin | Trades | Win% | Net $ | Net % | Sharpe | MaxDD | Expectancy | Profit factor |
|---|---|---|---|---|---|---|---|---|
| BTC | 57 | 29.8% | -588 | -5.9% | -0.65 | -11.5% | -10.31 | 0.80 |
| ETH | 73 | 39.7% | -246 | -2.5% | -0.20 | -10.3% | -3.37 | 0.93 |
| HYPE | 66 | 39.4% | +2003 | +20.0% | +1.87 | -6.7% | +30.34 | 1.62 |

## Verdict: MIXED (unstable -- likely fluke)

Shipped config: HYPE +20.0% (Sharpe 1.87) but BTC -5.9%/ETH -2.5%. The (10,30) sweep moves the edge: ETH +14.0%, HYPE -7.6%. When the winner changes coins with the parameter, there is no edge -- just variance across 57-73 trades. The volume gate works mechanically (blocks low-conviction crosses) but does not create alpha.

## Calibration note

VWMA verified against a manual rolling computation to 1e-9. Heavy-volume bar test: the fast line jumps above the slow one as designed. Volume gate verified: crosses without volume confirmation do not enter.

## Mechanism

Typical-price VWMA(20) vs VWMA(50) cross gated on volume above its 20-bar average; exit on the cross back; 2xATR stop, 3xATR trail, 120-bar max hold.

Source: Volume-weighted MA cross (volume-confirmed trend) —
https://www.investopedia.com/terms/v/vwma.asp

## Limitations

- Single 7-month window; HYPE-specific edges may be regime-specific.
- Funding unmodeled.
- Next-bar-open execution; fast-turn signals can slip.
